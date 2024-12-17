from mongoengine import Document, StringField, ReferenceField, BooleanField

class User(Document):
    username = StringField(required=True)
    email = StringField(required=True)
    password = StringField(required=True)
    test_status = StringField(choices=["Pending", "Passed", "Failed"], default="Pending")  
    is_admin = BooleanField(default=False)

class Job(Document):
    title = StringField(required=True)
    description = StringField()
    requirements = StringField()

class Application(Document):
    user = ReferenceField(User, required=True)
    job = ReferenceField(Job, required=True)
    resume_path = StringField(required=True)
    status = StringField(default="Pending")
    email = StringField()
