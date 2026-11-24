import random
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.models import PriceHistory

def normalize_price_result(
    site: str,
    price: Optional[int],
    available: bool,
    product_url: Optional[str] = None
) -> Dict:
    return {
        "site": site,
        "price": price,
        "available": available,
        "product_url": product_url
    }

def check_price_dummy(product_name: str) -> Dict:
    fake_price = random.randint(20000, 80000)

    return normalize_price_result(
        site="DummyStore",
        price=fake_price,
        available=True,
        product_url="https://example.com/product"
    )

def save_price(
    db: Session,
    product_id: int,
    price_data: dict
):
    record = PriceHistory(
        product_id=product_id,
        site=price_data["site"],
        price=price_data["price"]
    )
    db.add(record)
    db.commit()
