# pages/2_Funding.py
import math
import streamlit as st
from lib.state import ensure
from lib.api import list_accounts, list_cards, create_deposit, APIError

ensure()
st.title("Fund HSA")

if not st.session_state.account:
    st.warning("Open an account first.")
    st.stop()


def fmt_cents(cents: int) -> str:
    return f"${cents/100:,.2f}"
    
# 1) Load accounts
with st.spinner("Loading accounts..."):
    try:
        accounts = list_accounts(st.session_state.account)  # expects a list[dict]: {id, balance_cents, ...}
    except APIError as e:
        st.error(f"Failed to load accounts: {e}")
        st.stop()

if not accounts:
    st.info("No HSA accounts found. Create one on the Accounts page.")
    st.stop()

acct_label_to_id = {
    f"{a.get('id')} — Balance: {fmt_cents(a.get('balance_cents', 0))}": a["id"]
    for a in accounts
}
acct_label = st.selectbox("Choose account", list(acct_label_to_id.keys()))
account_id = acct_label_to_id[acct_label]

# 2) Load cards for that account
with st.spinner("Loading cards..."):
    try:
        cards = list_cards(account_id)  # expects list[dict]: {id, last4, active, ...}
    except APIError as e:
        st.error(f"Failed to load cards: {e}")
        st.stop()

if not cards:
    st.warning("This account has no cards. Issue a card on the Card page.")
    st.stop()

active_cards = [c for c in cards if c.get("active")]
if not active_cards:
    st.warning("No active cards on this account.")
    st.stop()

card_label_to_id = {f"{c['nickname']} •••• {c['last4']}": c["id"] for c in active_cards}
card_label = st.selectbox("Choose card", list(card_label_to_id.keys()))
card_id = card_label_to_id[card_label]

# 3) Amount input
amount_dollars = st.number_input(
    "Deposit amount (USD)",
    min_value=0.01,
    step=0.01,
    format="%.2f",
)

# 4) Submit
if st.button("Deposit"):
    errs = []
    if amount_dollars is None or amount_dollars <= 0:
        errs.append("Amount must be greater than $0.00.")
    if not account_id:
        errs.append("Account is required.")
    if not card_id:
        errs.append("Card is required.")

    if errs:
        st.error(" • " + "\n • ".join(errs))
        st.stop()

    amount_cents = int(math.floor(amount_dollars * 100 + 0.5))

    payload = {
        "account_id": account_id,
        "card_id": card_id,
        "amount_cents": amount_cents,
    }

    with st.spinner("Creating deposit..."):
        try:
            resp = create_deposit(payload)  # matches your api.py signature
        except APIError as e:
            st.error(f"Deposit failed: {e}")
        else:
            st.success(f"Deposited {fmt_cents(amount_cents)} to account {account_id}.")
            new_balance = None
            if isinstance(resp, dict):
                new_balance = (
                    resp.get("new_balance_cents")
                    or (resp.get("account") or {}).get("balance_cents")
                )
            if isinstance(new_balance, int):
                st.info(f"New balance: {fmt_cents(new_balance)}")