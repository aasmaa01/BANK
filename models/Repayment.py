from app import db

class Repayment(db.Model):
    __tablename__ = 'repayments'
    
    repayment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.loan_id'), nullable=False)
    repayment_date = db.Column(db.Date, nullable=False)
    repayment_amount = db.Column(db.Numeric(10, 2), nullable=False)

    loan = db.relationship('Loan', back_populates='repayments')

    def to_dict(self):
        return {
            'repayment_id': self.repayment_id,
            'loan_id': self.loan_id,
            'repayment_date': self.repayment_date.isoformat() if self.repayment_date else None,
            'repayment_amount': float(self.repayment_amount)
        }
