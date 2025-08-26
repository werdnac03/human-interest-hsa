# lib/api.py
from __future__ import annotations
import os
import requests
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:5000")

class APIError(RuntimeError):
    def __init__(self, message, status=None, payload=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.payload = payload

    def __str__(self):
        return f"APIError(status={self.status}, message={self.message})"

def _request(method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    url = API_URL.rstrip("/") + path
    r = requests.request(method, url, json=json, timeout=15)
    if not r.ok:
        try:
            j = r.json()
            msg = j.get("errors") or j.get("message") or r.text
        except Exception:
            msg = r.text
            j = None
        raise APIError(str(msg), status=r.status_code, payload=j)
    if r.text:
        return r.json()
    return None



# Users
def open_account(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/users/create", json=payload)
def login_account(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/users/login", json=payload)

# Accounts
def list_hsa_accounts(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _request("GET", "/accounts", json=payload)
def open_hsa_account(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/accounts/create", json=payload)

# Funding
def create_deposit(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/funding/deposit", json=payload)

# Cards
def issue_card(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/cards", json=payload)
def list_cards(account_id: str) -> List[Dict[str, Any]]:
    return _request("GET", f"/cards/accounts/{account_id}/cards")

# Transactions
def list_transactions(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _request("GET", "/transactions", payload)
def create_purchase(payload: Dict[str, Any]):
    return _request("POST", "/transactions/purchase", payload)
