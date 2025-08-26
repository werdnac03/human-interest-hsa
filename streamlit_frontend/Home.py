# Home.py
import streamlit as st
from lib.state import ensure
from lib.api import open_account, login_account, APIError

st.set_page_config(page_title="HSA Demo", page_icon="💳", layout="centered")

ensure()
st.title("HSA Demo")

if st.session_state.account:
    acc = st.session_state.account
    with st.expander("Current user"):
        st.json(acc)
else:
    st.info("Not logged in yet")


if st.session_state.get("account"):
    acc = st.session_state.account
    st.info(f"Account active! User: {acc.get('name')}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log out / Reset"):
            # Clear just the account (or st.session_state.clear() to wipe everything)
            del st.session_state["account"]
            st.rerun()
    with col2:
        st.info("You must log out/reset to create a different user.")
    st.stop()


with st.form("account_form", clear_on_submit=False):
    first = st.text_input("First name")
    last  = st.text_input("Last name")
    email = st.text_input("Email")
    pw    = st.text_input("Password", type="password")
    submitted_account = st.form_submit_button("Create User Account")

if submitted_account:
    errs = []
    if not first: errs.append("First name required")
    if not last:  errs.append("Last name required")
    if not email: errs.append("Email required")
    if not pw: errs.append("Password required")

    if errs:
        st.error("• " + "\n• ".join(errs))
    else:
        try:
            payload = {"name": first + " " + last, "email": email, "password": pw}
            acc = open_account(payload)
            st.session_state.account = acc
            st.success(f"Account created! User: {acc.get("name")}")
            st.rerun()
        except APIError as e:
            st.error(f"Failed to create account: {e}")
    st.stop()

with st.form("login_form", clear_on_submit=False):
    email = st.text_input("Email")
    pw    = st.text_input("Password", type="password")
    submitted_login = st.form_submit_button("Login")

if submitted_login:
    errs = []
    if not email: errs.append("Email required")
    if not pw: errs.append("Password required")

    if errs:
        st.error("• " + "\n• ".join(errs))
    else:
        try:
            payload = {"email": email, "password": pw}
            acc = login_account(payload)
            st.session_state.account = acc
            st.success(f"Account Logged In! User: {acc.get("name")}")
            st.rerun()
        except APIError as e:
            st.error(f"Failed to Log In: {e}")