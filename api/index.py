from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure SQLite Database
import os

# Ensure the database is stored in the main directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{BASE_DIR}/waitlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Waitlist Model
class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    country = db.Column(db.String(100))
    geolocation = db.Column(db.String(100)) 
    device_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database
with app.app_context():
    db.create_all()

# ROUTE
@app.route('/submit', methods=['POST'])
def submit():
    data = request.json  # Get JSON data from frontend

    # Extract values
    email = data.get('email')
    ip_address = request.remote_addr  
    country = data.get('country')  
    geolocation = data.get('geolocation')  
    device_type = data.get('device_type')  

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Check if the email already exists
    existing_user = Waitlist.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409  

    try:
        # Save to database
        new_entry = Waitlist(email=email, ip_address=ip_address, country=country,
                            geolocation=geolocation, device_type=device_type)
        db.session.add(new_entry)
        db.session.commit()

        print(f"New user added: {email}")  # Print confirmation in terminal
        return jsonify({"message": "User added to waitlist!"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")  # Print error 
        return jsonify({"error": "Database error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
