from app.services.notification_service import send_email_notification
from app.services.price_service import save_price


def evaluate_and_act(db, tracked, product, user, current_price: int, site: str):
    """Save the latest price and email the user when it is within budget."""
    save_price(
        db,
        product.id,
        {"site": site, "price": current_price},
    )

    if tracked.status != "watching" or current_price > tracked.budget:
        return

    try:
        send_email_notification(
            to_email=user.email,
            product_name=product.name,
            price=current_price,
            product_url=tracked.product_url,
        )
        print(f"Notified {user.email} — {product.name} is ₹{current_price}")
    except Exception as exc:
        print(f"Email failed for {user.email}: {exc}")
        return

    tracked.status = "notified"
    db.commit()
