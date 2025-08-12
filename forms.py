from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateTimeLocalField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class AdminLoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired(), Length(min=5, max=200)])
    start_time = DateTimeLocalField('Start Time', validators=[DataRequired()], default=datetime.now)
    end_time = DateTimeLocalField('End Time', validators=[DataRequired()], default=datetime.now)
    
    # Question 1
    question1 = TextAreaField('Question 1', validators=[DataRequired(), Length(min=10, max=500)])
    question1_option1 = StringField('Option A', validators=[DataRequired(), Length(max=200)])
    question1_option2 = StringField('Option B', validators=[DataRequired(), Length(max=200)])
    question1_option3 = StringField('Option C', validators=[DataRequired(), Length(max=200)])
    question1_option4 = StringField('Option D', validators=[DataRequired(), Length(max=200)])
    question1_correct = SelectField('Correct Answer', choices=[
        (0, 'Option A'), (1, 'Option B'), (2, 'Option C'), (3, 'Option D')
    ], coerce=int, validators=[DataRequired()])
    
    # Question 2
    question2 = TextAreaField('Question 2', validators=[DataRequired(), Length(min=10, max=500)])
    question2_option1 = StringField('Option A', validators=[DataRequired(), Length(max=200)])
    question2_option2 = StringField('Option B', validators=[DataRequired(), Length(max=200)])
    question2_option3 = StringField('Option C', validators=[DataRequired(), Length(max=200)])
    question2_option4 = StringField('Option D', validators=[DataRequired(), Length(max=200)])
    question2_correct = SelectField('Correct Answer', choices=[
        (0, 'Option A'), (1, 'Option B'), (2, 'Option C'), (3, 'Option D')
    ], coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Create Quiz')

class QuizSubmissionForm(FlaskForm):
    answer1 = SelectField('Answer for Question 1', choices=[
        (0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')
    ], coerce=int, validators=[DataRequired()])
    answer2 = SelectField('Answer for Question 2', choices=[
        (0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')
    ], coerce=int, validators=[DataRequired()])
    time_taken = IntegerField('Time Taken (seconds)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Submit Quiz')
