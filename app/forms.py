from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, EmailField, RadioField, FieldList, FormField, ValidationError
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    answer = RadioField('Answer', choices=[])
class QuizForm(FlaskForm):
    questions = FieldList(FormField(QuestionForm), min_entries=0)
