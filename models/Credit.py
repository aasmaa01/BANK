from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app import db


class Credit(db.Model):
    __tablename__ = 'credits'
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)
    credit_amount = Column(Float, nullable=False)
    credit_date = Column(Date, nullable=False)
    card = relationship('Card', backref='credits')

    def __repr__(self):
        return f'<Credit {self.amount}>'

