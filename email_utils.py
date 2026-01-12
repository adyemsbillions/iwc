from email.message import EmailMessage
import smtplib
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "yourgmail@gmail.com"
EMAIL_PASSWORD = "your-app-password"  

def send_verification_email(to_email: str, token: str):
    verify_link = f"http://127.0.0.1:8000/verify-email?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Verify Your IWC Exchange Account"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(f"""
Welcome to IWC Exchange 🎉

Please verify your email by clicking the link below:

{verify_link}

If you didn’t register, ignore this email.
""")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
