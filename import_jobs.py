import csv
from mongoengine import connect
from app.models import Job
from app.config import Config  # Import Config class

# Establish MongoDB connection
connect(
    db=Config.MONGODB_SETTINGS['db'],
    host=Config.MONGODB_SETTINGS['host'],
    port=Config.MONGODB_SETTINGS['port']
)

def import_jobs_from_csv(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            print(row)
            # Check if a job with the same title already exists
            existing_job = Job.objects(title=row['title']).first()
            if existing_job:
                print(f"Job '{row['title']}' already exists. Skipping...")
                continue  # Skip to the next job
            
            # Create a new job if it doesn't exist
            job = Job(
                title=row['title'],
                requirements=row['requirements'],
                description=row.get('description')
            )
            job.save()

# Run the import function
import_jobs_from_csv('openings.csv')
