import smtplib
from email.mime.text import MIMEText
from config import settings

def send_email_alert(subject: str, body: str):
    # Ví dụ: cấu hình email trong .env
    # Thực tế bạn có thể thay bằng Telegram/Slack
    sender = "you@example.com"
    recipients = ["admin@example.com"]
    password = "your_app_password"

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())
