# pages/2_Funding.py
import math
import streamlit as st
from lib.state import ensure
from lib.api import list_hsa_accounts, list_cards, create_deposit, APIError

def fmt_cents(cents: int | None) -> str:
    cents = cents or 0
    return f"${cents/100:,.2f}"

ensure()
st.title("Fund HSA")


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

# --- Load cards for the chosen HSA account -----------------------------------
with st.spinner("Loading cards..."):
    try:
        # Expects list[dict]: {"id","last4","nickname","active",...}
        cards = list_cards(hsa_id)
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

# preserve selected card PER HSA account
sel_cards_by_hsa = st.session_state.setdefault("sel_cards_by_hsa", {})
prev_card_id = sel_cards_by_hsa.get(hsa_id)

default_card_index = next(
    (i for i, c in enumerate(active_cards) if c.get("id") == prev_card_id),
    0
)

card = st.selectbox(
    "Choose card",
    options=active_cards,
    index=default_card_index,
    key=f"funding_card_select_{hsa_id}",  # key scoped to account to avoid widget clashes
    format_func=lambda c: f"{c.get('nickname','(card)')} •••• {c.get('last4','????')}",
)
card_id = card["id"]
sel_cards_by_hsa[hsa_id] = card_id
st.session_state.sel_cards_by_hsa = sel_cards_by_hsa

# --- Amount input -------------------------------------------------------------
amount_dollars = st.number_input(
    "Deposit amount (USD)",
    min_value=0.01,
    step=0.01,
    format="%.2f",
)

# --- Submit -------------------------------------------------------------------
if st.button("Deposit"):
    errs = []
    if amount_dollars is None or amount_dollars <= 0:
        errs.append("Amount must be greater than $0.00.")
    if not hsa_id:
        errs.append("Account is required.")
    if not card_id:
        errs.append("Card is required.")

    if errs:
        st.error(" • " + "\n • ".join(errs))
        st.stop()

    amount_cents = int(math.floor(amount_dollars * 100 + 0.5))
    payload = {
        "account_id": hsa_id,
        "card_id": card_id,
        "amount_cents": amount_cents,
    }

    with st.spinner("Creating deposit..."):
        try:
            resp = create_deposit(payload)
        except APIError as e:
            st.error(f"Deposit failed: {e}")
        else:
            st.success(f"Deposited {fmt_cents(amount_cents)} to account {hsa_id}.")
            # Show new balance if your API returns it
            new_balance = None
            if isinstance(resp, dict):
                new_balance = (
                    resp.get("new_balance_cents")
                    or (resp.get("account") or {}).get("balance_cents")
                )
            if isinstance(new_balance, int):
                st.info(f"New balance: {fmt_cents(new_balance)}")

            st.session_state["_flash"] = {
                "kind": "deposit_success",
                "message": f"Deposited {fmt_cents(amount_cents)} to account {hsa_id}.",
                "new_balance": new_balance,     # may be None if not returned
            }
            st.rerun()

# Flash message (survives st.rerun)
flash = st.session_state.pop("_flash", None)
if flash and flash.get("kind") == "deposit_success":
    st.success(flash["message"])
    nb = flash.get("new_balance")
    if isinstance(nb, int):
        st.info(f"New balance: {fmt_cents(nb)}")