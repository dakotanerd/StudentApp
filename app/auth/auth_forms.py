from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import Length, DataRequired, Email, EqualTo, ValidationError

import sqlalchemy as sqla
from app import db
from app.main.models import Student

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', [Length(min=0, max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Post')    

    def validate_username(self, username):
        if Student.query.filter_by(username=username.data).first():
            raise ValidationError('This username already exists! Please choose a different one.')

    def validate_email(self, email):
        if Student.query.filter_by(email=email.data).first():
            raise ValidationError('This email already exists! Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')
