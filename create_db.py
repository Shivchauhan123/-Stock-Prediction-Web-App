# create_db.py
from main import db, app

# Ensure the app context is used for creating tables
with app.app_context():
    db.create_all()
    print("Database and tables created successfully.")
