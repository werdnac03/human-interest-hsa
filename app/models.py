from .extensions import db
from datetime import datetime
import uuid

def gen_id():
    return uuid.uuid4().hex[:8]

class User(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=gen_id)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)   # hash, never plaintext

    # one-to-many: a User can have many HSAAccounts
    accounts = db.relationship("HSAAccount", back_populates="user", cascade="all, delete-orphan")

class HSAAccount(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=gen_id)
    user_id = db.Column(db.String(8), db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    balance_cents = db.Column(db.Integer, default=0)

    # many-to-one back to User
    user = db.relationship("User", back_populates="accounts")

    # one-to-many: an HSAAccount can have many cards & transactions
    cards = db.relationship("Card", back_populates="account", cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Card(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=gen_id)
    account_id = db.Column(db.String(8), db.ForeignKey("hsa_account.id"), nullable=False)
    last4 = db.Column(db.String(4), nullable=False)
    nickname = db.Column(db.String(80), unique=True, default="defualt card")
    active = db.Column(db.Boolean, default=True)

    # many-to-one back to HSAAccount
    account = db.relationship("HSAAccount", back_populates="cards")

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.String(8), primary_key=True, default=gen_id)
    account_id = db.Column(db.String(8), db.ForeignKey("hsa_account.id"), nullable=False)
    merchant = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(64), nullable=False)  # e.g., "pharmacy", "grocery"
    amount_cents = db.Column(db.Integer, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # many-to-one back to HSAAccount
    account = db.relationship("HSAAccount", back_populates="transactions")
