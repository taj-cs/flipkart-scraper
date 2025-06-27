"""Data models using SQLAlchemy ORM"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ProductInfo(Base):
    """Product information model"""
    __tablename__ = 'product_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    image_url = Column(Text, nullable=True)
    price = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ProductInfo(id={self.id}, title='{self.title[:50]}...', price='{self.price}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image_url,
            'price': self.price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
