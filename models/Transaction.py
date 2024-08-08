from app import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_transaction = db.Column(db.Integer, unique=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'id_transaction': self.id_transaction,
            'amount': self.amount,
            'currency': self.currency,
            'date': self.date.isoformat() if self.date else None,
            'transaction_type': self.transaction_type
        }
