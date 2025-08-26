from flask import Blueprint, request, jsonify
from ..services.hsa import issue_card

bp = Blueprint("cards", __name__)

@bp.post("/")
def create_card():
    account_id = request.json.get("account_id", "default")

    card = issue_card(account_id)
    return jsonify({"card_id": card.id, "last4": card.last4, "active": card.active})
