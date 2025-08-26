from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User, HSAAccount
from sqlalchemy.exc import IntegrityError

bp = Blueprint("accounts", __name__)

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
def hash_password(pw: str) -> str:
    # pbkdf2:sha256 with per-password random salt
    return generate_password_hash(pw, method="pbkdf2:sha256", salt_length=16)




@bp.post("/create")
def create_account():
    name = request.json.get("name", "Demo User")
    email = request.json.get("email").strip().lower()
    password = request.json.get("password", "")
    password_hash = hash_password(password)

    user = User(name=name, email=email, password_hash=password_hash)
    acct = HSAAccount(user = user, balance_cents=0)
    db.session.add_all([user, acct])

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"ok": False, "errors": ["Email already registered"]}), 409

    return jsonify({"ok": True, "name": user.name, "id": user.id, "email": user.email}), 200

@bp.post("/login")
def login():
    email = request.json.get("email").strip().lower()
    password = request.json.get("password", "")
    
    
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    return jsonify({"ok": True, "name": user.name, "id": user.id, "email": user.email}), 200
