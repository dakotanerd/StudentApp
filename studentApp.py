from app import db, create_app
from config import Config
from flask_login import current_user
from datetime import datetime, timezone
from app.main.models import Course, Major, Student, Enrolled
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

app = create_app(Config)

@app.shell_context_processor
def make_shell_context():
    return {'sqla': sqla, 'sqlo': sqlo, 'db': db, 'Course': Course, 'Major': Major, 'Student': Student, 'Enrolled' : Enrolled}

@sqla.event.listens_for(Major.__table__, 'after_create')
def add_majors(*args, **kwargs):
    query = sqla.select(Major)
    if db.session.scalars(query).first() is None:
        majors = [{'name':'CS','department':'Computer Science'},
            {'name':'DS','department':'Computer Science'},
            {'name':'RBE','department':'Robotics Engineering'},
            {'name':'ME','department':'Mechanical Engineering'}, 
            {'name':'MATH','department': 'Mathematics'}  ]
        for m in majors: 
            db.session.add(Major(name = m['name'], department = m['department']))
        db.session.commit()

@app.before_request
def beofre_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.add(current_user)
        db.session.commit()


@app.before_request
def initDB(*args, **kwargs):
    if app._got_first_request:
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

    