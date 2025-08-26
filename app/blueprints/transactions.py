from flask import Blueprint, request, jsonify
from ..services.hsa import deposit, validate_and_post
from ..extensions import db
from ..models import Card, HSAAccount, Transaction
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

bp = Blueprint("transactions", __name__)

@bp.post("/purchase")
def purchase():
    data = request.json
    txn = validate_and_post(
        data["account_id"], data["merchant"], data["category"], data["amount_cents"]
    )
    return jsonify({
        "transaction_id": txn.id,
        "approved": txn.approved,
        "remaining_balance_cents": txn.account.balance_cents
    })

@bp.get("/")
def list_transactions():
    account_id = request.json.get("user_id")
    #return {"a": account_id}

    if account_id:
        q = (
        Transaction.query
        .join(HSAAccount, Transaction.account_id == HSAAccount.id)
        .filter(HSAAccount.user_id == account_id)
        .options(joinedload(Transaction.account))  # eager load to avoid N+1
        .order_by(Transaction.created_at.desc())
        )
    txns = q.all()

    result = []
    for t in txns:
        result.append({
            "id": t.id,
            "account_id": t.account_id,
            "account_name": t.account.name,
            "merchant": t.merchant,
            "category": t.category,
            "amount": t.amount_cents / 100.0,   # return dollars for frontend
            "approved": t.approved,
            "date": t.created_at.isoformat(),
        })
    return jsonify(result)