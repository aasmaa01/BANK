from app import db

class Loan(db.Model):
    __tablename__ = 'loans'
    
    loan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    loan_amount = db.Column(db.Numeric(10, 2))
    interest_rate = db.Column(db.Numeric(5, 2))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    outstanding_balance = db.Column(db.Numeric(10, 2))

    customer = db.relationship('Customer', back_populates='loans')
    repayments = db.relationship('Repayment', back_populates='loan', lazy=True)

    def to_dict(self):
        return {
            'loan_id': self.loan_id,
            'client_id': self.client_id,
            'loan_amount': float(self.loan_amount),
            'interest_rate': float(self.interest_rate),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'outstanding_balance': float(self.outstanding_balance)
        }
