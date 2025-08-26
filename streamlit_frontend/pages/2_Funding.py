# pages/2_Funding.py
import streamlit as st
from lib.state import ensure
from lib.api import create_contribution, APIError

ensure()
st.title("Funding")

if not st.session_state.account:
    st.warning("Open an account first.")
    st.stop()

acc = st.session_state.account

with st.form("fund_form"):
    st.write(f"Account: **{acc.get('id','')}** — {acc.get('name')}")
    amount = st.number_input("Contribution amount (USD)", min_value=0.0, step=10.0, format="%.2f")
    bank = st.selectbox("Funding source", ["Mock Checking ****1234", "Mock Savings ****5678"])
    submitted = st.form_submit_button("Contribute")

if submitted:
    try:
        res = create_contribution({
            "accountId": acc.get("id"),
            "amount": amount,
            "source": bank,
        })
        st.session_state.last_result = res
        st.success(f"Contributed ${amount:,.2f}")
        st.toast("Funding created", icon="✅")
    except APIError as e:
        st.error(f"Funding failed: {e}")
