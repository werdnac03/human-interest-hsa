from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User, HSAAccount

bp = Blueprint("accounts", __name__)

@bp.post("/")
def create_account():
    name = request.json.get("name", "Demo User")
    user = User(name=name)
    acct = HSAAccount(user_id=user.id, balance_cents=0)
    db.session.add_all([user, acct])
    db.session.commit()
    return jsonify({"user_id": user.id, "account_id": acct.id, "balance_cents": acct.balance_cents})

