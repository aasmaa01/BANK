from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email_address = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    date_of_birth = Column(Date)
    address = Column(String(200))
    phone_number = Column(String(15))
    nin_cust = Column(String(50))
    rib_cust = Column(String(50))
    agency_id = Column(Integer, ForeignKey('agencies.id'))
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agency = relationship('Agency', back_populates='users')
    accounts = relationship('Account', back_populates='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'address': self.address,
            'phone_number': self.phone_number,
            'email_address': self.email_address,
            'nin_cust': self.nin_cust,
            'rib_cust': self.rib_cust,
            'agency_id': self.agency_id,
            'registration_date': self.registration_date,
        }
