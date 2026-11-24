from sqlalchemy.orm import Session
from app.models import User, Product, TrackedProduct

def create_tracking(db: Session, email: str, product_name: str, budget: int, product_url: str = None):
    # Get or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Get or create product
    product = db.query(Product).filter(Product.name == product_name).first()
    if not product:
        product = Product(name=product_name)
        db.add(product)
        db.commit()
        db.refresh(product)

    # Create tracked product
    tracked = TrackedProduct(
        user_id=user.id,
        product_id=product.id,
        budget=budget,
        product_url=product_url,
        status="watching"
    )
    db.add(tracked)
    db.commit()
    db.refresh(tracked)

    return tracked