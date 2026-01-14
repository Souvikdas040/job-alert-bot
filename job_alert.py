import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

def send_email(body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "Daily Fresher Software Job Alerts (India)"

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    email_body = """
Company: Demo Company
Role: Junior Software Engineer
Location: Remote (India)
Skills: Java, React, Node.js
Date Posted: Today
Apply: https://example.com
----------------------------------
    """

    send_email(email_body)
