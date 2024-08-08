from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app import db
class Card(db.Model):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    card_number = Column(String(16), nullable=False)
    card_type = Column(String(20), nullable=False)
    expiration_date = Column(Date, nullable=False)
    cardholder_name = Column(String(100), nullable=False)
    balance = Column(Float, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    customer = relationship('Customer', backref='cards')

    def __repr__(self):
        return f'<Card {self.card_number}>'
