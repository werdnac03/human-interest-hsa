from flask import Blueprint, request, jsonify
from ..services.hsa import deposit, validate_and_post

bp = Blueprint("transactions", __name__)

@bp.post("/deposit")
def deposit_funds():
    data = request.json
    acct = deposit(data["account_id"], data["amount_cents"])
    return jsonify({"account_id": acct.id, "balance_cents": acct.balance_cents})

@bp.post("/purchase")
def purchase():
    data = request.json
    txn = validate_and_post(
        data["account_id"], data["merchant"], data["category"], data["amount_cents"]
    )
    return jsonify({
        "transaction_id": txn.id,
        "approved": txn.approved,
        "remaining_balance_cents": txn.account.balance_cents if txn.approved else None
    })
