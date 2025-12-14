from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla
from app.main.models import Course, Student, Major
from app.main.forms import CourseForm, EditForm, EmptyForm
from flask_login import current_user, login_required
from sqlalchemy import text
from app.main import main_blueprint as main


@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    empty_form = EmptyForm()
    courses = db.session.scalars(sqla.select(Course))
    students = db.session.scalars(sqla.select(Student))
    return render_template('index.html', title="Course List", courses=courses, students=students, form=empty_form)


@main.route('/course/create', methods=['GET', 'POST'])
@login_required
def createclass():
    cform = CourseForm()
    if cform.validate_on_submit():
        new_class = Course(majorid=cform.major.data.id,
                           coursenum=cform.coursenum.data,
                           title=cform.title.data)
       
        db.session.add(new_class)
        try:
            db.session.commit()
            flash(f'Course "{new_class.get_major().get_name()} - {new_class.get_coursenum()}" is created.')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the course. Please try again.', 'danger')
   
    return render_template('create_course.html', form=cform)


@main.route('/student/profile', methods=['GET'])
@login_required
def display_profile():
    empty_form = EmptyForm()
    return render_template('display_profile.html', title='Display Profile', student=current_user, form = empty_form)


@main.route('/student/editprofile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    eform = EditForm()
    if request.method == 'POST':
        if eform.validate_on_submit():
            current_user.firstname = eform.firstname.data
            current_user.lastname = eform.lastname.data
            current_user.email = eform.email.data
            current_user.address = eform.address.data
            current_user.set_password(eform.password.data)
            
            for m in current_user.get_majors():
                current_user.majors_of_student.remove(m)

            for m in eform.majors.data:
                current_user.majors_of_student.add(m)

            db.session.add(current_user)
            db.session.commit()
            flash("Your changes have been saved")
            return redirect(url_for('main.display_profile'))


    elif request.method == 'GET':
    #populate the form data from the database
        eform.firstname.data = current_user.firstname
        eform.lastname.data = current_user.lastname
        eform.email.data = current_user.email
        eform.address.data = current_user.address
        for m in current_user.get_majors():
            eform.majors.data.append(m)

    else:
        pass

    return render_template('edit_profile.html', title = 'Edit Profile', form = eform)


@main.route('/majors/<int:major_id>/students', methods=['GET'])
@login_required
def get_students_in_major(major_id):
    themajor = db.session.get(Major, major_id)
   
    if themajor is None:
        return "Major not found", 404
   
    students = themajor.get_students()
   
    # Debugging output
    print(f"Major: {themajor.name}, Students: {[student.username for student in students]}")


    return render_template('major_roster.html',
                           title='Students in Major "{}"'.format(themajor.name),
                           major=themajor,
                           students=students)


@main.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll(course_id):
    thecourse = db.session.get(Course, course_id)
    if thecourse is None:
        flash(f'Course with id {course_id} is not found!', 'danger')
        return redirect(url_for('main.index'))
   
    current_user.enroll(thecourse)
    try:
        db.session.commit()
        flash(f'You are enrolled in course {thecourse.get_major().get_name()} {thecourse.get_coursenum()}!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while enrolling in the course. Please try again.', 'danger')


    return redirect(url_for('main.index'))  # Refresh the page after enrolling


@main.route('/course/<int:course_id>/unenroll', methods=['POST'])
@login_required
def unenroll(course_id):
    thecourse = db.session.get(Course, course_id)
    if thecourse is None:
        flash(f'Course with id {course_id} is not found!', 'danger')
        return redirect(url_for('main.index'))
   
    current_user.unenroll(thecourse)
    try:
        db.session.commit()
        flash(f'You dropped the course {thecourse.get_major().get_name()} {thecourse.get_coursenum()}!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while unenrolling from the course. Please try again.', 'danger')


    return redirect(url_for('main.index'))  # Refresh the page after unenrolling



@main.route('/course/<int:course_id>/roster', methods=['GET'])
@login_required
def roster(course_id):
    thecourse = db.session.get(Course, course_id)
    if thecourse is None:
        flash('Course not found!', 'danger')
        return redirect(url_for('main.index'))

    enrollments = db.session.scalars(thecourse.roster.select()).all()
    return render_template('class_roster.html',
                           title="Class Roster",
                           course=thecourse,
                           enrollments=enrollments)



# @main.route('/course/<int:course_id>/data', methods=['GET'])
# @login_required
# def roster_data(course_id):
#     thecourse = db.session.get(Course, course_id)

#     enrollments = db.session.scalars(thecourse.roster.select()).all()
    
#     roster =[]

#     for e in enrollments:
#         student = e.get_student()
#         roster.append({'student_id' : student.id, 
#          'firstname': student.firstname,
#          'lastname': student.lastname,
#          'email': student.email,
#          'address': student.address,
#          'last_seen': student.last_seen})

#     data = { 'class_id': thecourse.id,
#             'course_num': thecourse.get_coursenum(),
#             'course_major': thecourse.get_major().get_name(),
#             'course_title': thecourse.get_title(),
#             'students': roster,
#             'student_count': len(roster)}
    
#     return jsonify(data)



@main.route('/course/<int:course_id>/data', methods=['GET'])
@login_required
def roster_data(course_id):
    
    qinput = {"course_id" : course_id }
    query = text("""
        SELECT Course.id, Course.coursenum, Course.title, Major.name as major_name
         FROM Course JOIN Major ON Course.majorid = Major.id 
         WHERE Course.id = :course_id     
                """)
    thecourse = db.session.execute(query, qinput).mappings().first()

    query = text("""
            SELECT Student.id, Student.firstname, Student.lastname, Student.email, Student.address, Student.last_seen
            FROM Student JOIN Enrolled ON Student.id = Enrolled.student_id
            WHERE Enrolled.course_id = :course_id
                """)
    enrollments = db.session.execute(query, qinput).mappings().all()


    roster =[]

    for student in enrollments:
        roster.append({'student_id' : student['id'], 
         'firstname': student ['firstname'],
         'lastname': student ['lastname'],
         'email': student ['email'],
         'address': student ['address'],
         'last_seen': student ['last_seen']})

    data = { 'class_id': thecourse ['id'],
            'course_num': thecourse ['coursenum'],
            'course_major': thecourse ['major_name'],
            'course_title': thecourse ['title'],
            'students': roster,
            'student_count': len(roster)}
    
    return jsonify(data)