from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    grade_name = db.Column(db.String(50), unique=True, nullable=False)

    # One-to-Many relationship with streams
    streams = db.relationship('Stream', backref='grade', lazy=True)

    def __repr__(self):
        return f'<Grade {self.grade_name}>'

class Stream(db.Model):
    __tablename__ = 'streams'
    id = db.Column(db.Integer, primary_key=True)
    stream_name = db.Column(db.String(50), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False)

    def __repr__(self):
        return f'<Stream {self.stream_name} of Grade ID {self.grade_id}>'
