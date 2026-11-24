from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    site = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    checked_at = Column(DateTime, default=datetime.utcnow)