# lib/api.py
from __future__ import annotations
import os
import requests
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

load_dotenv()
BASE = os.getenv("API_URL", "http://localhost:5000")

class APIError(RuntimeError):
    def __init__(self, message, status=None, payload=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.payload = payload

    def __str__(self):
        return f"APIError(status={self.status}, message={self.message})"

def _request(method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    url = BASE.rstrip("/") + path
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

# Accounts
def open_account(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/accounts/create", json=payload)
def login_account(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/accounts/login", json=payload)

# Funding
def create_contribution(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/funding", json=payload)

# Cards
def issue_card(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/cards", json=payload)

# Transactions
def list_transactions() -> List[Dict[str, Any]]:
    return _request("GET", "/transactions")
