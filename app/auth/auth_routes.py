from app import db
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sqla
from app.main.models import Student
from app.auth.auth_forms import  RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth



@auth.route('/student/register', methods=['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        student = Student(username=rform.username.data,
                          firstname=rform.firstname.data,
                          lastname=rform.lastname.data,
                          email=rform.email.data,
                          address=rform.address.data)
        student.set_password(rform.password.data)
        db.session.add(student)
        try:
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering. Please try again.', 'danger')
   
    return render_template('register.html', form=rform)


@auth.route('/student/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
   
    lform = LoginForm()
    if lform.validate_on_submit():
        student = db.session.execute(sqla.select(Student).where(Student.username == lform.username.data)).scalar_one_or_none()


        if student is None or not student.check_password(lform.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))


        login_user(student, remember=lform.remember_me.data)
        flash(f'The user {current_user.username} has successfully logged in!')
        return redirect(url_for('main.index'))
   
    return render_template('login.html', form=lform)


@auth.route('/student/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

