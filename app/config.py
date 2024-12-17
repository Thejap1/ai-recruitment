import os

class Config:
    MONGODB_SETTINGS = {
        'db': '<your-db-name>',
        'host': 'localhost',
        'port': xxxxx
    }
    MONGO_URI = 'mongodb://localhost:xxxxx/<your-db-name>'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Folder for uploads
    SECRET_KEY = os.urandom(24)