import warnings
warnings.filterwarnings("ignore")

from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.main.models import Course, Student, Major
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    
class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = Student(username='john', firstname='John', lastname='Yates')
        u.set_password('covid')
        self.assertFalse(u.check_password('flu'))
        self.assertTrue(u.check_password('covid'))

    def test_enroll(self):
        m1 = Major(name='CS', department='Computer Science')
        db.session.add(m1)
        db.session.commit()
        u1 = Student(username='john', firstname = "John", lastname = "Yates", address="WPI", email='john.yates@wpi.com')
        db.session.add(u1)
        db.session.commit()
        c1 = Course(majorid=m1.id, coursenum='3551', title = 'Test Course')
        db.session.add(c1)
        db.session.commit()

        # count = db.session.scalar(db.select(db.func.count()).select_from(Course))
        # count = db.session.scalar(db.select(db.func.count(Course.id)))

        self.assertEqual(db.session.scalars(u1.enrollments.select()).all(), [])
        self.assertEqual(db.session.scalars(c1.roster.select()).all(), [])

        u1.enroll(c1) # exercise the test
        db.session.commit()
        # check if the DB is updated correctly
        self.assertTrue(u1.is_enrolled(c1))
        u1_classes = db.session.scalars(u1.enrollments.select()).all()
        self.assertEqual(len(u1_classes), 1)
        self.assertEqual(u1_classes[0].course_enrolled.coursenum, '3551')
        self.assertEqual(u1_classes[0].course_enrolled.majorid, m1.id)
        c1_roster = db.session.scalars(c1.roster.select()).all()
        self.assertEqual(len(c1_roster), 1)
        self.assertEqual(c1_roster[0].student_enrolled.username, 'john')

        u1.unenroll(c1)  # exercise the test
        db.session.commit()
        # check if the DB is updated correctly
        c1_roster = db.session.scalars(c1.roster.select()).all()
        u1_classes = db.session.scalars(u1.enrollments.select()).all()
        self.assertFalse(u1.is_enrolled(c1))
        self.assertEqual(len(u1_classes), 0)
        self.assertEqual(len(c1_roster), 0)


    

if __name__ == '__main__':
    unittest.main(verbosity=2)