# Initialize the database

from app import db

def initialize_database():
    db.create_all()

if __name__ == '__main__':
    initialize_database()
