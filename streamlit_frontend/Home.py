# Home.py
import streamlit as st
from lib.state import ensure

st.set_page_config(page_title="HSA Demo", page_icon="💳", layout="centered")
ensure()

st.title("HSA Demo")
st.write(
    "Use the pages on the left to walk through the core HSA flows:\n"
    "- Open an account\n"
    "- Fund it\n"
    "- Issue a card\n"
    "- View transactions"
)

if st.session_state.account:
    acc = st.session_state.account
    with st.expander("Current account"):
        st.json(acc)
else:
    st.info("No account yet. Start with **Accounts → Open Account**.")
