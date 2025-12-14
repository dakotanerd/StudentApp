from app import app, db
from app.models import Course, Major, Student, Enrolled
from config  import Config

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
import os
#os.remove("student.db")

app.app_context().push()

db.create_all()


# Add couple Majors
major1 = Major(name = 'CS', department = 'Computer Science')
db.session.add(major1)
major2 = Major(name = 'DS', department = 'Computer Science')
db.session.add(major2)
major3 = Major(name = 'ME', department = 'Mechanical Engineering')
db.session.add(major3)
major4 = Major(name = 'RBE', department = 'Robotics Engineering')
db.session.add(major4)
major5 = Major(name = 'MATH', department = 'Mathematics')
db.session.add(major5)
db.session.commit()

# print Majors
for major in db.session.scalars(sqla.select(Major)):
    print(major)

#--------------------------------------------------------------
# Add courses
major1 = db.session.scalars(sqla.select(Major).where(Major.name == 'CS')).first()
major2 = db.session.scalars(sqla.select(Major).where(Major.name == 'RBE')).first()
major4 = db.session.scalars(sqla.select(Major).where(Major.name == 'ME')).first()


# Add couple courses
c1 = Course(coursenum='3733',majorid = major1.id, title='Software Engineering') # course is associated with major1
db.session.add(c1)
c2 = Course(coursenum='3431',majorid = major1.id, title='Database Systems')     # course is associated with major1
db.session.add(c2)
c3 = Course(coursenum='1001',majorid = major2.id, title='Introduction to Robotics')     # course is associated with major2
db.session.add(c3)
c4 = Course(coursenum='3411',majorid = major4.id, title='Fluid Mechanics')     # course is associated with major4 
db.session.add(c4)
db.session.commit()


# print Courses
for course in db.session.scalars(sqla.select(Course)):
    print(course)

#-------------------------
# Add couple students
s1 = Student(username='sakire', firstname = 'Sakire', lastname = 'Arslan Ay', email='sakire@wpi.edu', address = 'WPI') 
s1.set_password('123')
db.session.add(s1)

s2 = Student(username='john', firstname = 'John', lastname = 'Yates', email='john@wpi.edu', address = 'Seatle')  #address is optional
s2.set_password('123')
db.session.add(s2)

s3 = Student(username='kitten', firstname = 'Snow', lastname = 'Thecat', email='meow@wpi.edu', address = 'Cat Town')  #address is optional
s3.set_password('123')
db.session.add(s3)
db.session.commit()

# print students
for student in db.session.scalars(sqla.select(Student)):
    print(student)


# query table
s1 = db.session.scalars(sqla.select(Student).where(Student.username == 'sakire')).first()
s2 = db.session.scalars(sqla.select(Student).where(Student.username == 'john')).first()
s3 = db.session.scalars(sqla.select(Student).where(Student.username == 'kitten')).first()

major1 = db.session.scalars(sqla.select(Major).where(Major.name == 'CS')).first()
major2 = db.session.scalars(sqla.select(Major).where(Major.name == 'RBE')).first()
major4 = db.session.scalars(sqla.select(Major).where(Major.name == 'ME')).first()

c1 = db.session.scalars(sqla.select(Course).where(Course.majorid == major1.id).where(Course.coursenum == '3733')).first()
c2 = db.session.scalars(sqla.select(Course).where(Course.majorid == major1.id).where(Course.coursenum == '3431')).first()
c3 = db.session.scalars(sqla.select(Course).where(Course.majorid == major2.id).where(Course.coursenum == '1001')).first()


# associate the Students with Majors  (Many-to-Many relationship through 'students_majors_table' association table)
s1.majors_of_student.add(major1)   # student1 double majors in CS and RBE
s1.majors_of_student.add(major2)   
s2.majors_of_student.add(major2)   # student2 only majors in RBE
s3.majors_of_student.add(major1)   # student3 only majors in CS
db.session.commit()

enroll1 = Enrolled(course_id=c1.id, student_id=s1.id)
db.session.add(enroll1)
enroll2 = Enrolled(course_id=c2.id, student_id=s1.id)
db.session.add(enroll2)
enroll3 = Enrolled(course_id=c1.id, student_id=s2.id)
db.session.add(enroll3)
enroll4 = Enrolled(course_id=c1.id, student_id=s3.id)
db.session.add(enroll4)
enroll5 = Enrolled(course_id=c2.id, student_id=s3.id)
db.session.add(enroll5)
enroll6 = Enrolled(course_id=c3.id, student_id=s3.id)
db.session.add(enroll6)
db.session.commit()


