from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from flask_cors import CORS
import requests  # To call the NLP microservice

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuration for email
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587  # TLS port
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Sender email
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Sender email password
COMPANY_SUPPORT_EMAIL = os.getenv("COMPANY_SUPPORT_EMAIL")  # Company email address

print(f"EMAIL_ADDRESS: {EMAIL_ADDRESS}")
print(f"COMPANY_SUPPORT_EMAIL: {COMPANY_SUPPORT_EMAIL}")

# Complaint model for the database
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    product = db.Column(db.String(200), nullable=False)
    issue = db.Column(db.Text, nullable=False)
    summarized_issue = db.Column(db.Text, nullable=True)  # Add summarized issue
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create the database
with app.app_context():
    db.create_all()

# Helper function to call NLP microservice
def summarize_text(text):
    try:
        response = requests.post("http://localhost:5001/summarize", json={"text": text})
        if response.status_code == 200:
            return response.json().get("summary", text[:250] + '...')
        else:
            return text[:250] + '...'  # Fallback to truncation
    except Exception as e:
        print(f"Error in summarization service: {e}")
        return text[:250] + '...'  # Fallback to truncation

# Route: Submit Complaint
@app.route('/send-complaint', methods=['POST'])
def send_complaint():
    try:
        # Get complaint details from the frontend
        data = request.json
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        product = data.get('product')
        issue = data.get('issue')

        # Validate input
        if not name or not email or not phone or not product or not issue:
            return jsonify({"error": "All fields are required."}), 400

        # Call NLP microservice to summarize the issue
        summarized_issue = summarize_text(issue)

        # Save complaint to the database
        new_complaint = Complaint(
            name=name,
            email=email,
            phone=phone,
            product=product,
            issue=issue,
            summarized_issue=summarized_issue
        )
        db.session.add(new_complaint)
        db.session.commit()

        # Compose the email
        subject = f"New Consumer Complaint from {name}"
        body = f"""
        Dear Support Team,

        A consumer has submitted a complaint. Below are the details:

        Name: {name}
        Email: {email}
        Phone: {phone}
        Product: {product}

        Issue Description (Summary):
        {summarized_issue}

        Please address this issue promptly.

        Regards,
        Automated Complaint System
        """
        # Send the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = COMPANY_SUPPORT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Add CC to the consumer
        msg['Cc'] = email

        server = smtplib.SMTP(SMTP_SERVER, 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return jsonify({"message": "Complaint submitted and saved successfully!"}), 200

    except smtplib.SMTPException as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Route: Get All Complaints
@app.route('/complaints', methods=['GET'])
def get_complaints():
    try:
        complaints = Complaint.query.all()
        result = [
            {
                "id": complaint.id,
                "name": complaint.name,
                "email": complaint.email,
                "phone": complaint.phone,
                "product": complaint.product,
                "issue": complaint.issue,
                "summarized_issue": complaint.summarized_issue,  # Include summarized issue
                "timestamp": complaint.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for complaint in complaints
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve complaints: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
