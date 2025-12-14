from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import Length, DataRequired, Email, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from flask_login import current_user
import sqlalchemy as sqla
from app import db
from app.main.models import Major, Student

class CourseForm(FlaskForm):
    coursenum = StringField('Course Number', [Length(min=3, max=6)])
    title = StringField('Course Title', validators=[DataRequired()])
    major = QuerySelectField(
        'Major',
        query_factory=lambda: db.session.scalars(sqla.select(Major)),
        get_label=lambda themajor: themajor.name,
        allow_blank=False
    )
    submit = SubmitField('Post')

class EditForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', [Length(min=0, max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    majors = QuerySelectMultipleField(
        'Majors',
        query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
        get_label=lambda themajor: themajor.name,
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput()
    )
    submit = SubmitField('Post')

    def validate_email(self, email):
        student = Student.query.filter_by(email=email.data).first()
        if student and student.id != current_user.id:
            raise ValidationError('This email already exists! Please choose a different one.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
