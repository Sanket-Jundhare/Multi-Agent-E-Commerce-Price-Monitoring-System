from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.database import Base

class TrackedProduct(Base):
    __tablename__ = "tracked_products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    budget = Column(Integer, nullable=False)
    status = Column(String, default="watching")
    product_url = Column(String, nullable=True)  # For storing product link
    created_at = Column(DateTime, default=datetime.utcnow)