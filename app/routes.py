"""
Routes for the AI Job Portal application.

This file contains the route handlers for the following functionalities:
- User Authentication (Signup, Login, Logout)
- Job Application Process (Job Listings, Job Applications, Resume Upload)
- Machine Learning Predictions (AI-based matching for job applications)
- Quiz Feature (Quiz questions and scoring)
- Administrative Tasks (View and update job applications, generate reports)

Each route function is responsible for handling specific HTTP requests, interacting
with the database models, and rendering templates to provide a smooth user experience.

Imports include Flask modules for routing and session management, MongoDB and ML model
interactions, and utility functions like email sending and file uploading.

Logging is configured to capture debug-level information for troubleshooting.
"""
import os
import json
import csv
from flask import Flask, Blueprint, request, flash, redirect, url_for, render_template, current_app, session, send_file
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user, logout_user, login_user
from app.models import User, Job, Application
from app.ml import load_ml_model, preprocess_resume, run_ai_ml_predictions
from app.email_utils import send_email, send_application_confirmation, send_result_email
from bson import ObjectId
from PyPDF2 import PdfReader
import logging
from app.forms import QuizForm, QuestionForm
from app.utils import calculate_score

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Create the Blueprint object
main = Blueprint('main', __name__)

# Set the upload folder path
UPLOAD_FOLDER = r'<path>\AiRe_Repo\uploads' 
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Add the upload folder to the app configuration
main.config = {
    'UPLOAD_FOLDER': UPLOAD_FOLDER
}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        flash("You are not logged in", "error")
        return redirect(url_for('main.login_view'))  # Redirect to login if not logged in
    
    # Welcome message
    flash(f"Welcome user {session['user_id']}", "success")
    jobs = Job.objects.all()  # Use MongoDB query (Mongoengine syntax)
    return render_template('jobs.html', jobs=jobs)

# Signup action route
@main.route('/signup', methods=['GET', 'POST'])
def signup_view():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        # Access MongoDB collections via current_app
        users_collection = current_app.users_collection

        # Check if the email already exists
        user = users_collection.find_one({"email": email})
        if user:
            flash("Email already exists", "error")
            return redirect(url_for('main.signup_view'))
        else:
            # Insert the new user into the database
            users_collection.insert_one({"email": email, "password": hashed_password})
            flash("Signup successful", "success")
            return redirect(url_for('main.login_view'))

    return render_template('signup.html')

# Login view for rendering the login form
@main.route('/login', methods=['GET'])
def login_view():
    return render_template('login.html')

# Login action route
@main.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Access MongoDB collections via current_app
        users_collection = current_app.users_collection
        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            # Set session details
            session['user_id'] = str(user['_id']) 
            session['is_admin'] = user.get('is_admin', False)  # Store admin status in session

            # Redirect based on user role
            if user.get('is_admin', False):  # Use get() to safely access 'is_admin'
                return redirect(url_for('main.view_applications'))  # Admin-specific page
            else:
                return redirect(url_for('main.job_list'))  # Regular user page
        else:
            flash("Invalid credentials", "error")
    return redirect(url_for('main.login_view'))

# Logout route
@main.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash("You have been logged out", "success")
    return redirect(url_for('main.login_view'))

@main.route('/jobs')
def job_list():
    jobs = Job.objects.all()  # Use MongoDB query (Mongoengine syntax)
    return render_template('jobs.html', jobs=jobs)

# Load the ML model once when the application starts
model = load_ml_model()

# Helper function to preprocess resume files
def preprocess_resume(file_path):
    extension = file_path.rsplit('.', 1)[1].lower()
    if extension == 'pdf':
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + ' '
        return text
    elif extension == 'txt':
        with open(file_path, 'r') as file:
            text = file.read()
        return text
    else:
        raise ValueError("Unsupported file type!")

# Route for applying to a job
@main.route('/apply/<job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    job = Job.objects(id=job_id).first()
    if job is None:
        flash('Job not found!', 'error')
        return redirect(url_for('main.job_list'))

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['resume']
        email = request.form.get('email')  # Get the email from the form
        logging.debug(f"Email extracted from form: {email}")

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            try:
                # Save the file
                file.save(file_path)
                flash(f"File saved to {file_path}")

                # Load models and preprocess the resume
                nb_model, nn_model, tfidf, label_encoder = load_ml_model()
                resume_text = preprocess_resume(file_path)

                # Run predictions
                predictions = run_ai_ml_predictions(nb_model, nn_model, tfidf, label_encoder, resume_text)
                
                match_score = predictions  
                
                # Save the application to the database
                application = Application(job=job, resume_path=file_path, status="Applied")
                application.save()

                if match_score is None:
                    flash("Match score calculation error!", "error")
                    return redirect(request.url)
                else:
                    flash(f"Match score: {match_score}")

                send_application_confirmation(email)

                return redirect(url_for('main.job_list'))

            except Exception as e:
                flash(f'Error saving file: {str(e)}', 'error')
                return redirect(request.url)

    return render_template('apply_job.html', job=job)

@main.route('/applications')
@login_required
def view_applications():
    if not session.get('is_admin'):
        flash("You must be an admin to view this page.", "error")
        return redirect(url_for('main.login'))

    applications = Application.objects()
    return render_template('applications.html', applications=applications)

@main.route('/update_application_status/<application_id>', methods=['POST'])
@login_required
def update_application_status(application_id):
    new_status = request.form.get('status')
    application = Application.objects(id=application_id).first()
    if application:
        application.status = new_status
        application.save()
        flash("Application status updated successfully", "success")
    else:
        flash("Application not found", "error")
    
    return redirect(url_for('main.view_applications'))

@main.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    applications = Application.objects()
    report_directory = os.path.join('static', 'reports')
    os.makedirs(report_directory, exist_ok=True)
    report_file_path = os.path.join(report_directory, 'applications_report.csv')
    
    with open(report_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Candidate Name', 'Job Title', 'Resume', 'Status', 'Email'])
        for application in applications:
            writer.writerow([
                application.user.username,
                application.job.title,
                application.resume_path,
                application.status,
                application.email
            ])
    
    return send_file(report_file_path, as_attachment=True)