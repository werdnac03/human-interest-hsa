# lib/state.py
import streamlit as st

def ensure():
    if "account" not in st.session_state:
        st.session_state.account = None  # dict from backend
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
