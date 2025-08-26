# pages/4_Transactions.py
import streamlit as st
import pandas as pd
from lib.state import ensure
from lib.api import list_transactions, APIError

ensure()
st.title("Transactions")

@st.cache_data(ttl=15)
def fetch_tx():
    return list_transactions()

try:
    data = fetch_tx()
    if not data:
        st.info("No transactions yet.")
    else:
        df = pd.DataFrame(data)
        # nice formatting
        if "amount" in df.columns:
            df["amount"] = df["amount"].map(lambda x: f"${x:,.2f}")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        st.dataframe(df, use_container_width=True, hide_index=True)
except APIError as e:
    st.error(f"Failed to load transactions: {e}")
