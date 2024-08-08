
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app import db

class Agency(db.Model):
    __tablename__ = 'agencies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100))

    # Define the reverse relationship
    users = db.relationship('User', back_populates='agency')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location
        }
