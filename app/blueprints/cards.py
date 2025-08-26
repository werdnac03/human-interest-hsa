from flask import Blueprint, request, jsonify
from ..services.hsa import issue_card
from ..models import HSAAccount, Card

bp = Blueprint("cards", __name__)

@bp.post("/")
def create_card():

    account_id = request.json.get("account_id", "default")
    last4 = request.json.get("last4")
    nickname = request.json.get("nickname")


    if not account_id or not last4 or len(last4) != 4 or not last4.isdigit():
        return jsonify({"error": "accountId and valid last4 required"}), 400
    
    account = HSAAccount.query.get(account_id)
    if not account:
        return jsonify({"error": f"Account not found"}), 404
    
    card = issue_card(account_id, nickname, last4)
    return jsonify({"card_id": card.id, "nickname": card.nickname, "last4": card.last4, "active": card.active})


@bp.get("/accounts/<account_id>/cards")
def list_cards(account_id: str):  # handles GET /accounts
    acct = HSAAccount.query.get(account_id)
    if not acct:
        return jsonify({"error": "Account not found"}), 404

    rows = Card.query.filter_by(account_id=account_id).all()
    data = [
        {
            "id": c.id,
            "account_id": c.account_id,
            "last4": c.last4,
            "nickname": c.nickname ,
            "active": bool(c.active),
        }
        for c in rows
    ]
    return data