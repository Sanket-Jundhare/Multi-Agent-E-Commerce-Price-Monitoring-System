import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(
    to_email: str,
    product_name: str,
    price: int,
    product_url: str = None,
):
    """
    Sends an email notification with a direct product link.
    """
    # Configuration - use your Gmail App Password
    EMAIL_FROM = "sanketjundhare@gmail.com"
    EMAIL_PASSWORD = "dlcu gueq ilwk ptpy"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    subject = f"🎉 Price Alert: {product_name} is within your budget!"

    # Email body
    body = f"""
Good news! 🎉

The product you are tracking is now within your budget.

🛒 Product: {product_name}
💰 Current Price: ₹{price}
"""

    if product_url:
        body += f"""

👉 Buy now using this link:
{product_url}
"""

    body += """

⚡ Hurry! Prices can change anytime.

— Price Monitor Agent
"""

    # Send email
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()