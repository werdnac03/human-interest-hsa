from .extensions import db
from datetime import datetime
import uuid

def gen_id():
    return uuid.uuid4().hex[:8]

class User(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=gen_id)
    name = db.Column(db.String(80), nullable=False)

class HSAAccount(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=gen_id)
    user_id = db.Column(db.String(8), db.ForeignKey("user.id"), nullable=False)
    balance_cents = db.Column(db.Integer, default=0)

class Card(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=gen_id)
    account_id = db.Column(db.String(8), db.ForeignKey("hsa_account.id"), nullable=False)
    last4 = db.Column(db.String(4), nullable=False)
    active = db.Column(db.Boolean, default=True)

class Transaction(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=gen_id)
    account_id = db.Column(db.String(8), db.ForeignKey("hsa_account.id"), nullable=False)
    merchant = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(64), nullable=False)  # e.g., "pharmacy", "grocery"
    amount_cents = db.Column(db.Integer, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
