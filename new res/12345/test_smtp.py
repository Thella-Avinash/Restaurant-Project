import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

sender_email = os.environ.get('GMAIL_USER')
sender_password = os.environ.get('GMAIL_APP_PASSWORD')

print(f"GMAIL_USER: {sender_email}")
print(f"GMAIL_APP_PASSWORD: {'*' * len(sender_password) if sender_password else 'None'}")

msg = EmailMessage()
msg.set_content("Test OTP 123456")
msg['Subject'] = 'Test OTP'
msg['From'] = sender_email
msg['To'] = sender_email

context = ssl.create_default_context()
try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
