"""
This file contains the functional tests for the routes.
These tests use GETs and POSTs to different URLs to check for the proper behavior.
Resources:
    https://flask.palletsprojects.com/en/1.1.x/testing/ 
    https://www.patricksoftwareblog.com/testing-a-flask-application-using-pytest/ 
"""
import os
import pytest
from flask import  url_for 
from app import create_app, db
from app.main.models import Course, Student, Major
from config import Config
import sqlalchemy as sqla


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True


@pytest.fixture(scope='module')
def test_client():
    # create the flask application ; configure the app for tests
    flask_app = create_app(config_class=TestConfig)

    # db.init_app(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()
 
    # Establish an application context before running the tests.
    ctx = flask_app.test_request_context()
    ctx.push()
 
    yield  testing_client 
    # this is where the testing happens!
 
    ctx.pop()


def new_user(username, email, firstname, lastname, address, passwd):
    user = Student(username = username, email = email, firstname = firstname, lastname = lastname, address = address)
    user.set_password(passwd)
    return user

# @pytest.fixture
# def user_fixture():
#     return new_user(username='sakire', email='sakire@wpi.edu',firstname='Sakire',lastname='Arslan Ay', address='Northborough, MA')

@pytest.fixture
def init_database(request,test_client):
    # Create the database and the database table
    db.create_all()
    # initialize the majors
    if Major.query.count() == 0:
        majors = [{'name':'CS','department':'Computer Science'},{'name':'SE','department':'Computer Science'},{'name':'EE','department':'Electrical Engineering'},
                  {'name':'ME','department':'Mechanical Engineering'}, {'name':'MATH','department': 'Mathematics'}  ]
        for t in majors:
            db.session.add(Major(name=t['name'],department=t['department']))
        db.session.commit()
    #add a user    
    user1 = new_user('sakire', 'sakire@wpi.edu', 'Sakire', 'Arslan Ay', 'Worcester, MA', '1234')
    # Insert user data
    db.session.add(user1)

    cs_major = db.session.scalars(sqla.select(Major).where(Major.name == 'CS')).first()
    course1 = Course(majorid = cs_major.id, coursenum =  '3733', title = "Software Engineering")
    db.session.add(course1)
    db.session.commit()     # Commit the changes 

    yield  # this is where the testing happens!

    db.drop_all()



def test_register_page(request,test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/student/register' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/student/register')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_register(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/student/register' form is submitted (POST)
    THEN check that the response is valid and the database is updated correctly
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.post('/student/register', 
                          data=dict(username='john', email='john@wpi.edu',password="bad-bad-password",password2="bad-bad-password", firstname='John',lastname='Yates', address='Worcester, MA'),
                          follow_redirects = True)
    assert response.status_code == 200
    # get the data for the new user from DB
    s = db.session.scalars(sqla.select(Student).where(Student.username == 'john')).first()
    s_count = db.session.scalar(sqla.select(db.func.count()).where(Student.username == 'john'))

    assert s.lastname == 'Yates'
    assert s_count == 1
    # Assumption: The application should re-direct to login page after login. 
    assert b"Please log in to access this page." in response.data  #Students should update this assertion condition according to their own page content
    assert b"Congratulations, you are now a registered user!" in response.data  #Students should update this assertion condition according to their own page content
    assert b"Sign In" in response.data   

def test_invalidlogin(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with wrong credentials
    THEN check that the response is valid and login is refused 
    """
    response = test_client.post('/student/login', 
                          data=dict(username='sakire', password='12345',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    # if you display a flash message for invalid login, include an assertion condition checking for that message. 
    assert b"Sign In" in response.data 

# ------------------------------------
# Helper functions

def do_login(test_client, path , username, passwd):
    response = test_client.post(path, 
                          data=dict(username= username, password=passwd, remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Hello, student!" in response.data  #Students should update this assertion condition according to their own page content

def do_logout(test_client, path):
    response = test_client.get(path,                       
                          follow_redirects = True)
    assert response.status_code == 200
    # Assuming the application re-directs to login page after logout. 
    assert b"Sign In" in response.data   #Students should update this assertion condition according to their own page content
# ------------------------------------

def test_login_logout(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/student/login' form is submitted (POST) with correct credentials
    THEN check that the response is valid and login is succesfull 
    """
    do_login(test_client, path = '/student/login', username = 'sakire', passwd = '1234')

    do_logout(test_client, path = '/student/logout')
   

def test_create_course(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing , after user logs in,
    WHEN the '/course/create' page is requested (GET)  AND '/course/create' form is submitted (POST)
    THEN check that response is valid and the class is successfully created in the database
    """
    #first login
    do_login(test_client, path = '/student/login', username = 'sakire', passwd = '1234')
    
    #test the "create class" form 
    response = test_client.get('/course/create')
    assert response.status_code == 200
    assert b"Create a new class" in response.data  #Students should update this assertion condition according to their own page content
    
    cs_major = db.session.scalars(sqla.select(Major).where(Major.name == 'CS')).first()
    #test posting a class
    response = test_client.post('/course/create', 
                          data=dict(coursenum = '1101', title = 'Programming with Gregor!', major = cs_major.id),   # "major" field of the form is a QuerySelectField ; we just pass the id of the cs_major.
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"1101" in response.data
    assert b"Programming with Gregor!" in response.data 

    # get the data for the new course from DB
    c = db.session.scalars(sqla.select(Course).where(Course.coursenum == '1101').where(Course.majorid == cs_major.id)).first()
    c_count = db.session.scalar(sqla.select(db.func.count()).where(Course.coursenum == '1101').where(Course.majorid == cs_major.id))
    assert c.get_title() == 'Programming with Gregor!'
    assert c_count == 1

    #finally logout
    do_logout(test_client, path = '/student/logout')


def test_enroll(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing , after user logs in, and after a class is created
    WHEN the '/course/<course_id>/enroll' form is submitted (POST)
    THEN check that response is valid and the currently logged in user (student) is successfully added to roster
    """
    #first login
    do_login(test_client =  test_client, path = '/student/login', username = 'sakire', passwd = '1234')


    # Get the course 'CS 3733' from DB. The course was created and added to the DB during setup. 
    cs_major = db.session.scalars(sqla.select(Major).where(Major.name == 'CS')).first()
    course1 = db.session.scalars(sqla.select(Course).where(Course.coursenum == '3733').where(Course.majorid == cs_major.id)).first()

    #enroll the logged in student in CS 3733 
    response = test_client.post('course/'+ str(course1.id) + '/enroll', 
                        data=dict(),
                        follow_redirects = True)
    assert response.status_code == 200
    assert b"You are enrolled in course CS 3733" in response.data #Students should update this assertion condition according to their own page content
    c = db.session.query(Course).filter(Course.coursenum =='3733' and Course.majorid == cs_major.id).first()
    thecourse = db.session.scalars(sqla.select(Course).where(Course.coursenum == '3733').where(Course.majorid == cs_major.id)).first()

    enrollments = db.session.scalars(thecourse.roster.select()).all()
    assert len(enrollments) == 1  # there should be a single student enrolled
    assert enrollments[0].student_enrolled.username == 'sakire'

    #finally logout
    do_logout(test_client = test_client, path = '/student/logout')

