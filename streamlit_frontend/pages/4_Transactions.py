# pages/4_Transactions.py
import streamlit as st
import pandas as pd
from datetime import date
from lib.state import ensure
from lib.api import list_hsa_accounts, create_purchase, list_transactions, APIError

def fmt_cents(cents: int | None) -> str:
    cents = cents or 0
    return f"${cents/100:,.2f}"

ensure()
st.title("Initiate Purchase")

if not st.session_state.account:
    st.warning("Open an account first.")
    st.stop()

# --- Load HSA accounts for this user/base account ----------------------------
with st.spinner("Loading accounts..."):
    try:
        # Expects list[dict]: each dict has at least {"id", "acct_name", "balance_cents", ...}
        hsa_accounts = list_hsa_accounts(st.session_state.account)
    except APIError as e:
        st.error(f"Failed to load accounts: {e}")
        st.stop()

if not hsa_accounts:
    st.info("No HSA accounts found. Create one on the Accounts page.")
    st.stop()

# preserve previously selected HSA account by its id
prev_hsa_id = st.session_state.get("sel_hsa_id")
default_hsa_index = next(
    (i for i, a in enumerate(hsa_accounts) if a.get("id") == prev_hsa_id),
    0
)

hsa = st.selectbox(
    "Choose account",
    options=hsa_accounts,
    index=default_hsa_index,
    key="funding_hsa_select",
    format_func=lambda a: f"{a.get('acct_name','(unnamed)')} — Balance: {fmt_cents(a.get('balance_cents'))}",
)
hsa_id = hsa["id"]
st.session_state.sel_hsa_id = hsa_id
# --- Generate Purchase Form ----------------------------

with st.form("purchase_form", clear_on_submit=False):
    col1, col2 = st.columns([2, 1])
    with col1:
        merchant = st.text_input("Merchant", placeholder="e.g., CVS Pharmacy")
    with col2:
        category = st.text_input("Category", placeholder= "Pharmacy")

    amount_dollars = st.number_input("Amount (USD)", min_value=0.01, step=1.00, format="%.2f")
    submit = st.form_submit_button("Create Purchase")

if submit:
    errs = []
    if not merchant.strip():
        errs.append("Merchant is required.")
    if amount_dollars <= 0:
        errs.append("Amount must be positive.")

    if errs:
        st.error(" • " + "\n • ".join(errs))
    else:
        try:
            amount_cents = int(round(amount_dollars * 100))
            payload = {
                "account_id": hsa_id,
                "merchant": merchant.strip(),
                "category": category,
                "amount_cents": amount_cents
            }
            resp = create_purchase(payload)
            approved = bool(resp.get("approved"))
            txn_id = resp.get("transaction_id")
            remaining = resp.get("remaining_balance_cents")
            if approved:
                st.session_state["_flash"] = (
                    "success",
                    [
                    f"Approved: {merchant} for \${amount_dollars:,.2f} ",
                    f"(New balance: {fmt_cents(remaining)})"
                    ]
                )
            else:
                # clarify why it failed if backend adds `error` later; for now, generic
                st.session_state["_flash"] = (
                    "error",
                    [
                    f"Declined: {merchant} for \${amount_dollars:,.2f}. ", 
                    f"Insufficient funds or not HSA-qualified. ",
                    f"Balance: {fmt_cents(remaining)}"
                    ]
                )
            st.rerun()

        except APIError as e:
            st.error(f"Failed to create purchase: {e}")

# Show persisted success message after rerun, then clear it
if _flash := st.session_state.pop("_flash", None):
    level, parts = _flash
    msg = " ".join(str(p).strip() for p in parts if p)
    getattr(st, level)(msg)   # st.success / st.error / etc.


st.title("Past Transactions")

if not st.session_state.account:
    st.warning("Open an account first.")
    st.stop()

try:
    data = list_transactions(st.session_state.account)
    #st.info(f"{data}")
    #pass
    cols_to_hide = ["id", "account_id"]
    if not data:
        st.info("No transactions yet.")
    else:
        df = pd.DataFrame(data)
        # nice formatting
        df = df.drop(columns=cols_to_hide, errors="ignore")
        if "amount" in df.columns:
            df["amount"] = df["amount"].map(lambda x: f"${x:,.2f}")

        desired_order = ["account_name", "merchant", "category", "amount", "approved", "date"]
        df = df.reindex(columns=desired_order)

        st.dataframe(df, use_container_width=True, hide_index=True)
except APIError as e:
    st.error(f"Failed to load transactions: {e}")

