# pages/3_Card.py
import streamlit as st
from lib.state import ensure
from lib.api import issue_card, APIError

ensure()
st.title("Card Issuance")

if not st.session_state.account:
    st.warning("Open an account first.")
    st.stop()

acc = st.session_state.account

with st.form("card_form"):
    st.write(f"Account: **{acc.get('id','')}** — {acc.get('name')}")
    kind = st.radio("Card type", ["Virtual", "Physical"], horizontal=True)
    nickname = st.text_input("Card nickname", value="Primary HSA Card")
    submitted = st.form_submit_button("Issue Card")

if submitted:
    try:
        res = issue_card({
            "accountId": acc.get("id"),
            "type": kind.lower(),
            "nickname": nickname,
        })
        st.session_state.last_result = res
        card_id = res.get("id", "card_xxx")
        st.success(f"Issued {kind.lower()} card {card_id}")
        if kind == "Virtual":
            with st.expander("Card details (mock)"):
                st.write("Card Number: 4111 1111 1111 1111")
                st.write("Expiry: 12/29   CVV: 123")
    except APIError as e:
        st.error(f"Issuing card failed: {e}")
