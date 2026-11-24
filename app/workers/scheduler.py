from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import TrackedProduct, Product, User
from app.agents.decision_agent import evaluate_and_act
from app.services.price_fetcher import fetch_price

scheduler = BackgroundScheduler()

def price_check_job():
    print("⏰ Scheduler: Running price_check_job")

    db: Session = SessionLocal()
    try:
        tracked_items = (
            db.query(TrackedProduct)
            .filter(TrackedProduct.status == "watching")
            .all()
        )

        print(f"🔍 Found {len(tracked_items)} active tracked items")

        for tracked in tracked_items:
            product = db.query(Product).filter(
                Product.id == tracked.product_id
            ).first()

            user = db.query(User).filter(
                User.id == tracked.user_id
            ).first()

            if not product or not user:
                continue

            # Fetch price
            price_data = fetch_price(product.name)
            if not price_data:
                continue

            current_price = price_data["price"]
            site = price_data.get("site", "mock")

            # Decision agent
            evaluate_and_act(
                db=db,
                tracked=tracked,
                product=product,
                user=user,
                current_price=current_price,
                site=site
            )

    except Exception as e:
        print(f"❌ Scheduler error: {e}")

    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(
        price_check_job,
        "interval",
        minutes=1,  # Change to 60 for production
        id="price_check_job",
        replace_existing=True,
    )
    scheduler.start()
    print("✅ Scheduler started successfully")