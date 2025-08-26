from ..extensions import db
from ..models import HSAAccount, Card, Transaction
from ..validators.expenses import is_qualified

def deposit(account_id: str, amount_cents: int):
    acct = HSAAccount.query.get_or_404(account_id)
    acct.balance_cents += amount_cents
    db.session.commit()
    return acct

def issue_card(account_id: str):
    acct = HSAAccount.query.get_or_404(account_id)
    card = Card(account_id=acct.id, last4="0000") #0000 as a dummy last4
    db.session.add(card)
    db.session.commit()
    return card

def validate_and_post(account_id: str, merchant: str, category: str, amount_cents: int):
    acct = HSAAccount.query.get_or_404(account_id)
    qualified = is_qualified(category)
    approved = qualified and acct.balance_cents >= amount_cents
    txn = Transaction(
        account_id=acct.id, merchant=merchant, category=category,
        amount_cents=amount_cents, approved=approved
    )
    if approved:
        acct.balance_cents -= amount_cents
    db.session.add(txn)
    db.session.commit()
    return txn
