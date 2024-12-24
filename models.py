from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class SchoolInfo(db.Model):
    __tablename__ = 'school_info'

    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False)  
    address = db.Column(db.String(250), nullable=False)
    registration_number = db.Column(db.String(50), nullable=True, unique=False)  
    contact_email = db.Column(db.String(100), nullable=True, unique=False)  
    contact_phone = db.Column(db.String(15), nullable=False, unique=False)  
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())   
    
    def __repr__(self):
        return f"<SchoolInfo(name={self.name}, registration_number={self.registration_number})>"


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_name = db.Column(db.String(100), unique=True, nullable=False)
    tsc_no = db.Column(db.String(20), unique=True, nullable=True)  
    id_no = db.Column(db.String(20), unique=True, nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)   
    gender = db.Column(db.Enum('male', 'female', name='gender_enum'), nullable=False)
    role = db.Column(db.String(20), default='teacher')
    passport_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Teacher {self.teacher_name} - ID: {self.id}>"
    

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False, unique=True)  
    username = db.Column(db.String(150), nullable=False, unique=True)   
    password_hash = db.Column(db.String(128), nullable=False)   
    is_password_updated = db.Column(db.Boolean, default=False, nullable=False)   

    # Relationship to Teacher
    teacher = db.relationship("Teacher", backref="user", uselist=False)

    # Password hashing methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    grade_name = db.Column(db.String(50), unique=True, nullable=False)

    # One-to-One relationship with Stream
    stream = db.relationship('Stream', backref='grade', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Grade {self.grade_name}>'

class Stream(db.Model):
    __tablename__ = 'streams'
    id = db.Column(db.Integer, primary_key=True)
    stream_name = db.Column(db.String(50), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), unique=True, nullable=False)

    def __repr__(self):
        return f'<Stream(s) {self.stream_name} of Grade ID {self.grade_id}>'
