# app/__init__.py

import os
from flask import Flask, session
from flask_pymongo import PyMongo
from mongoengine import connect
from flask_login import LoginManager  # Import LoginManager
from app.routes import main
from app.config import Config
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

mail = Mail()

load_dotenv()  # Load environment variables from .env file

def create_app():
    app = Flask(__name__, template_folder='../templates')

    # Load the config from app/config.py
    app.config.from_object('app.config.Config')

    # Configure session settings
    app.config.update(
        SESSION_COOKIE_NAME='ai_app_cookie', 
        PERMANENT_SESSION_LIFETIME=3600,  # Set session to expire after 1 hour (3600 seconds)
        SESSION_REFRESH_EACH_REQUEST=True  # Refresh the session lifetime on each request
    )

    # Debugging info
    print("Template folder:", os.path.abspath(app.template_folder))
    print("App root path:", app.root_path)

    # Initialize extensions
    mail.init_app(app)

    # Initialize MongoDB with PyMongo for document-based collections
    mongo = PyMongo(app)

    # MongoDB collections (PyMongo)
    app.users_collection = mongo.db.users
    app.jobs_collection = mongo.db.jobs
    app.applications_collection = mongo.db.applications

    # Initialize MongoEngine for models (e.g., User, Job)
    connect(
        db=app.config['MONGODB_SETTINGS']['db'],
        host=app.config['MONGODB_SETTINGS']['host'],
        port=app.config['MONGODB_SETTINGS']['port']
    )

    # Initialize the LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)  # Associate it with Flask app

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        user = User.objects(pk=user_id).first()
        if user:
            session.permanent = True  # Set session to be permanent
        return user

    # Register the routes blueprint 
    app.register_blueprint(main) 

    return app
