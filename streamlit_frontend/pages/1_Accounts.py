# pages/1_Accounts.py
import streamlit as st
from lib.state import ensure
from lib.api import list_hsa_accounts, open_hsa_account, APIError

ensure()
st.title("View HSA Accounts")

if not st.session_state.account:
    st.warning("Open an account first.")
    st.stop()

def fmt_cents(cents: int) -> str:
    return f"${cents/100:,.2f}"

# 1) Load accounts
with st.spinner("Loading accounts..."):
    try:
        accounts = list_hsa_accounts(st.session_state.account)  # expects a list[dict]: {id, balance_cents, ...}
    except APIError as e:
        st.error(f"Failed to load accounts: {e}")
        st.stop()

if not accounts:
    st.info("No HSA accounts found. Create one on the Accounts page.")


for a in accounts:
    st.write(
        f"**{a.get('acct_name','(unnamed)')}** — "
        f"Balance: {fmt_cents(a.get('balance_cents', 0))}  "
        f"(ID: {a['id']})"
    )


st.title("Open HSA Account")

with st.form("hsa_account_form", clear_on_submit=False):
    hsa_account_name = st.text_input("Account name")
    submitted_hsa_account = st.form_submit_button("Create Account")

if submitted_hsa_account:
    errs = []
    if not hsa_account_name: errs.append("Account name required")

    if errs:
        st.error("• " + "\n• ".join(errs))
    else:
        try:
            payload = {"hsa_account_name": hsa_account_name, "account": st.session_state.account}
            hsa_acc = open_hsa_account(payload)
            st.session_state.hsa_account = hsa_acc
            st.success(f"HSA account created!")
            st.rerun()
        except APIError as e:
            st.error(f"Failed to create HSA account: {e}")
    st.stop()

