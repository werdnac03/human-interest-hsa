from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Card, HSAAccount, Transaction
from sqlalchemy.exc import IntegrityError

bp = Blueprint("funding", __name__)

# --------- helpers ---------

def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status

def _account_to_dict(a: HSAAccount) -> dict:
    return {
        "id": a.id,
        "user_id": a.user_id,
        "balance_cents": int(a.balance_cents or 0),
    }

def _transaction_to_dict(t: Transaction) -> dict:
    return {
        "id": t.id,
        "account_id": t.account_id,
        "merchant": t.merchant,
        "category": t.category,
        "amount_cents": int(t.amount_cents),
        "approved": bool(t.approved),
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


# --------- routes ---------

@bp.post("/deposit")
def deposit():
    data = request.get_json(silent=True) or {}
    account_id = data.get("account_id")
    card_id = data.get("card_id")
    amount_cents = data.get("amount_cents")

    # Basic validation
    if not account_id or not card_id:
        return _json_error("account_id and card_id are required.")
    if not isinstance(amount_cents, int) or amount_cents <= 0:
        return _json_error("amount_cents must be a positive integer.")

    # Fetch account + card
    acct: HSAAccount | None = HSAAccount.query.get(account_id)
    if not acct:
        return _json_error("Account not found.", 404)

    card: Card | None = Card.query.get(card_id)
    if not card or card.account_id != acct.id:
        return _json_error("Card not found for this account.", 404)
    if not card.active:
        return _json_error("Card is inactive.", 400)

    # Apply business logic
    try:
        # Increase balance and create an approved 'funding' transaction
        acct.balance_cents = int(acct.balance_cents or 0) + amount_cents

        tx = Transaction(
            account_id=acct.id,
            merchant="HSA Funding",
            category="funding",
            amount_cents=amount_cents,
            approved=True,
        )

        db.session.add(tx)
        db.session.add(acct)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return _json_error("Could not complete deposit due to a database error.", 500)

    return (
        jsonify(
            {
                "account": _account_to_dict(acct),
                "transaction": _transaction_to_dict(tx),
                "new_balance_cents": acct.balance_cents,
            }
        ),
        201,
    )

