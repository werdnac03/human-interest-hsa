from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User, HSAAccount
from sqlalchemy.exc import IntegrityError

bp = Blueprint("accounts", __name__)


@bp.post("/create")
def create_account():
    hsa_name = request.json.get("hsa_account_name", "Default account")
    acct = request.json.get("account")
    existing = HSAAccount.query.filter_by(user_id=acct.get("user_id"), name=hsa_name).first()
    if existing:
        return jsonify({"ok": False, "errors": ["HSA-Account name already in use"]})

    hsa_acct = HSAAccount(user_id=acct.get("user_id"), name=hsa_name, balance_cents=0)
    db.session.add_all([hsa_acct])

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"ok": False, "errors": ["Some commit error"]}), 409

    return jsonify({"ok": True, "hsa_name": hsa_name}), 200

@bp.get("")
def list_hsa_accounts():  # handles GET /accounts
    user_id = request.json.get("user_id")
    rows = HSAAccount.query.filter_by(user_id=user_id).all()
    data = [{"id": a.id, "user_id": a.user_id, "acct_name": a.name,"balance_cents": a.balance_cents or 0} for a in rows]
    return data

    