# pages/3_Card.py
import re
import streamlit as st
from lib.state import ensure
from lib.api import issue_card, list_cards, list_hsa_accounts, APIError

ensure()
st.title("Card Issuance")

if not st.session_state.account:
    st.warning("Open an account first.")
    st.stop()


# 1) Load accounts
with st.spinner("Loading accounts..."):
    try:
        accounts = list_hsa_accounts(st.session_state.account)  # expects a list[dict]: {id, balance_cents, ...}
    except APIError as e:
        st.error(f"Failed to load accounts: {e}")
        st.stop()

if not accounts:
    st.info("No HSA accounts found. Create one on the Accounts page.")
    st.stop()

acct_label_to_id = {
    f"{a.get('acct_name')}": a["id"]
    for a in accounts
}
acct_label = st.selectbox("Choose account", list(acct_label_to_id.keys()))
account_id = acct_label_to_id[acct_label]

acc = st.session_state.account

def digits_only(s: str) -> str:
    return re.sub(r"\D+", "", s or "")

with st.form("card_form"):
    st.write(f"Account: **{acc.get('user_id')}** — {acc.get('name','')}")
    nickname = st.text_input("Card nickname", value="Primary HSA Card")

    # Masked input
    card_input = st.text_input(
        "Card number",
        value="",
        type="password",
        help="Enter a 16-digit card number. Only the last 4 will be stored."
    )

    submitted = st.form_submit_button("Issue Card")

if submitted:
    try:
        raw = digits_only(card_input)

        # Only check: must be exactly 16 digits
        if len(raw) != 16:
            st.error("Card number must be exactly 16 digits.")
            st.stop()

        last4 = raw[-4:]

        payload = {
            "user_id": acc.get("id"),
            "account_id": account_id,
            "nickname": nickname,
            "last4": last4,   # backend stores only this
        }
        res = issue_card(payload)
        st.session_state.last_result = res
        card_id = res.get("id", "card_xxx")
        st.success(f"Issued {res.get("nickname")} {card_id} (•••• {last4})")

    except APIError as e:
        st.error(f"Issuing card failed: {e}")
