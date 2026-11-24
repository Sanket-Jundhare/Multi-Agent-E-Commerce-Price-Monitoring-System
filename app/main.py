from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import socket
import qrcode_terminal

from app.database import engine, Base, get_db
from app.services.tracking_service import create_tracking
from app.workers.scheduler import start_scheduler

from app.models import TrackedProduct, Product, User, PriceHistory

# -------------------------------------------------
# APP SETUP
# -------------------------------------------------
app = FastAPI(title="Price Monitor Agent")
templates = Jinja2Templates(directory="app/templates")

# -------------------------------------------------
# HELPER: GET LOCAL IP
# -------------------------------------------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# -------------------------------------------------
# STARTUP
# -------------------------------------------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()

    try:
        ip = get_local_ip()
    except OSError:
        ip = "127.0.0.1"
    url = f"http://{ip}:8000/dashboard"

    print("Scheduler started")
    print(f"\nOpen on phone: {url}\n")

    try:
        qrcode_terminal.draw(url)
    except Exception as exc:
        print(f"QR code skipped: {exc}")

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")


@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# DASHBOARD (READ)
# -------------------------------------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    status: str | None = None,
    product: str | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(TrackedProduct, Product, User)
        .join(Product)
        .join(User)
    )

    if status:
        query = query.filter(TrackedProduct.status == status)

    if product:
        query = query.filter(Product.name.ilike(f"%{product}%"))

    rows = query.order_by(TrackedProduct.created_at.desc()).all()

    items = []
    for tracked, product_obj, user in rows:
        last_price = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_obj.id)
            .order_by(PriceHistory.checked_at.desc())
            .first()
        )

        items.append({
            "id": tracked.id,
            "email": user.email,
            "product": product_obj.name,
            "budget": tracked.budget,
            "product_url": tracked.product_url,
            "status": tracked.status,
            "last_price": last_price.price if last_price else None,
            "last_checked": last_price.checked_at if last_price else None,
        })

    price_rows = (
        db.query(PriceHistory, Product)
        .join(Product)
        .order_by(PriceHistory.checked_at.asc())
        .all()
    )

    chart_data = {}
    for price, product_obj in price_rows:
        chart_data.setdefault(product_obj.name, []).append({
            "time": price.checked_at.strftime("%H:%M"),
            "price": price.price,
        })

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "items": items,
            "chart_data": chart_data or {},
            "status": status,
            "product": product,
        },
    )

# -------------------------------------------------
# CREATE (ADD FROM DASHBOARD)
# -------------------------------------------------
@app.post("/dashboard/create")
def create_from_dashboard(
    email: str = Form(...),
    product_name: str = Form(...),
    product_url: str = Form(default=""),
    budget: int = Form(...),
    db: Session = Depends(get_db),
):
    create_tracking(
        db=db,
        email=email,
        product_name=product_name,
        budget=budget,
        product_url=product_url,
    )

    response = RedirectResponse(url="/dashboard")
    response.status_code = 303
    return response

# -------------------------------------------------
# UPDATE (EDIT BUDGET)
# -------------------------------------------------
@app.post("/tracking/{tracking_id}/update")
def update_tracking(
    tracking_id: int,
    budget: int = Form(...),
    db: Session = Depends(get_db),
):
    tracked = db.query(TrackedProduct).filter(
        TrackedProduct.id == tracking_id
    ).first()

    if tracked:
        tracked.budget = budget
        tracked.status = "watching"
        db.commit()

    response = RedirectResponse(url="/dashboard")
    response.status_code = 303
    return response

# -------------------------------------------------
# STOP (PAUSE TRACKING)
# -------------------------------------------------
@app.post("/tracking/{tracking_id}/stop")
def stop_tracking(
    tracking_id: int,
    db: Session = Depends(get_db),
):
    tracked = db.query(TrackedProduct).filter(
        TrackedProduct.id == tracking_id
    ).first()

    if tracked:
        tracked.status = "stopped"
        db.commit()

    response = RedirectResponse(url="/dashboard")
    response.status_code = 303
    return response

# -------------------------------------------------
# DELETE
# -------------------------------------------------
@app.post("/tracking/{tracking_id}/delete")
def delete_tracking(
    tracking_id: int,
    db: Session = Depends(get_db),
):
    tracked = db.query(TrackedProduct).filter(
        TrackedProduct.id == tracking_id
    ).first()

    if tracked:
        db.delete(tracked)
        db.commit()

    response = RedirectResponse(url="/dashboard")
    response.status_code = 303
    return response