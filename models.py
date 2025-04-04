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
    # One-to-Many relationship with Stream
    streams = db.relationship('Stream', backref='grade', lazy=True)

    def __repr__(self):
        return f'<Grade {self.grade_name}>'


class Stream(db.Model):
    __tablename__ = 'streams'
    id = db.Column(db.Integer, primary_key=True)
    stream_name = db.Column(db.String(50), nullable=True) 
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False)

    def __repr__(self):
        return str(self.stream_name)


class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)   
    fullname = db.Column(db.String(50), nullable=False)   
    grade = db.Column(db.String(10), nullable=False)  
    dob = db.Column(db.Date, nullable=False)   
    photo = db.Column(db.String(255), nullable=True)   
    adm_no = db.Column(db.String(20), unique=True, nullable=False)  
    adm_date = db.Column(db.Date, nullable=False)   
    gender = db.Column(db.String(10), nullable=False)  
    stream = db.Column(db.String(50), nullable=True)   
    previous_school = db.Column(db.String(100), nullable=True)   
    parent_name = db.Column(db.String(50), nullable=False)   
    relationship = db.Column(db.String(30), nullable=False)   
    contact_phone = db.Column(db.String(15), nullable=False)   
    id_no = db.Column(db.Integer, nullable=False)   
    email = db.Column(db.String(120), nullable=True)  
    health_info = db.Column(db.Text, nullable=True)  

    def __repr__(self):
        return f'<Student {self.fullname} (Grade: {self.grade})>'
    

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    subject = db.Column(db.String(100), nullable=False)  


class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), default='Teacher')
    grade = db.Column(db.String(50), default=None)
    stream = db.Column(db.String(50), default=None)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), 
                 nullable=False) 
    teacher = db.relationship("Teacher", backref="duty")


class TeacherSubjectAssignment(db.Model):
    __tablename__ = 'teacher_subject_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.String(50), nullable=False)  
    stream = db.Column(db.String(50), nullable=True)  # Stream can be NULL if not provided

    # Relationships
    teacher = db.relationship("Teacher", backref="assigned_subjects")
    subject = db.relationship("Subject", backref="teacher_assignments") 

    def teaching_sub(self):
        return self.subject.subject
    
    def teaching_grade(self):
        return self.grade
    
    def teaching_stream(self):
        return self.stream
    
    def __repr__(self): 
        return f"{self.subject.subject} ({self.grade}  {self.stream})"
    
    
class Exam(db.Model):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Term 1 Exam 2025"
    term = db.Column(db.String(20), nullable=False)  # e.g., "Term 1"
    year = db.Column(db.Integer, nullable=False)  # e.g., 2025
    status = db.Column(db.Enum('open', 'closed', name='exam_status_enum'), default='open', nullable=False)  
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"{self.name} ({self.term} {self.year})"
 


class ExamMarks(db.Model):
    __tablename__ = 'exam_marks'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    marks = db.Column(db.Float, nullable=True)  # Can be NULL if not entered
    
    # Relationships
    exam = db.relationship('Exam', backref='marks')
    student = db.relationship('Student', backref='marks')
    subject = db.relationship('Subject', backref='marks')

    def __repr__(self):
        return f"<Marks: {self.marks} for {self.student.fullname} in {self.subject.subject} ({self.exam.name})>"
