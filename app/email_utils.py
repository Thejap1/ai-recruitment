import smtplib
from app.models import User
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import url_for, current_app, render_template
import os  # For accessing environment variables
from flask_mail import Message
from dotenv import load_dotenv
from flask import render_template


# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Fetch email credentials
EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_email(subject, body, to_email):
    from_email = EMAIL_ID
    password = EMAIL_PASSWORD

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    print(f"Attempting to send email to {to_email}")
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server: 
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_result_email(recipient_email, passed):
    subject = "Technical Test Results"
    
    if passed:
        # Render the 'successful.html' template for a passing result
        message = render_template('congratulations.html', company_name="Rec.ai")
    else:
        # Render the 'unsuccessful.html' template for a failing result
        message = render_template('unsuccessful.html', company_name="Rec.ai")
    

    send_email(to_email=recipient_email, subject=subject, body=message)
