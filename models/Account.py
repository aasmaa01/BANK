from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app import db

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False)
    account_number = Column(String(20), unique=True, nullable=False)
    account_type = Column(String(20), nullable=False)
    balance = Column(Float, nullable=False)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    user = relationship('User', back_populates='accounts')
    agency = relationship('Agency', backref='accounts')  # Assuming you have an Agency model

    def to_dict(self):
        return {
            'id': self.id,
            'balance': self.balance,
            'user_id': self.user_id
        }
