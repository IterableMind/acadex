from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from ..models import Teacher
from wtforms import (
    StringField, 
    TextAreaField, 
    SubmitField, 
    IntegerField, 
    RadioField, 
    SelectField,
    FileField,
    PasswordField,
    EmailField,
    FileField,
    DateField
)
from wtforms.validators import (
    DataRequired, 
    Length, 
    Email, 
    NumberRange, 
    Optional, 
    Regexp,
    EqualTo,
    InputRequired
)

class SearchStudent(FlaskForm):
    search_input = StringField(
        validators=[
            DataRequired(message="Please enter ADM No, Name, or UPI No!")
        ]
    )
    search_by = RadioField(
        "Search Student",
        choices=[
            ("Enter adm no", "Adm no"),
            ("Enter name", "Name"),
            ("Enter UPI no", "UPI no")
        ],
        default="Enter adm no"
    )
    search = SubmitField("Search")


class SchoolInfoForm(FlaskForm):
    name = StringField(
        'School Name', 
        validators=[
            DataRequired(
                message='Please provide school name.'
            ), 
            Length(min=3, max=100)
        ],
        render_kw={"placeholder": "Enter school name"}
    )
    address = TextAreaField(
        'Address',
        validators=[
            DataRequired(
                message='Please provide school address.'
            ), 
            Length(max=250)
        ],
        render_kw={"placeholder": "Enter school address"}
    )
    registration_number = StringField(
        'Registration Number (Optional)',
        validators=[
            Length(min=5, max=50), 
            Optional()
        ],
        render_kw={"placeholder": "Enter registration number"}
    )
    contact_email = StringField(
        'Contact Email (Optional)',
        validators=[
            Optional(),
            Email(), 
            Length(max=100)
        ],
        render_kw={"placeholder": "Enter email address"}
    )
    contact_phone = StringField(
        'Contact Phone',
        validators=[
            DataRequired(
                message='Please provide phone number.'
            ), 
            Length(min=10, max=15)
        ],
        render_kw={"placeholder": "Enter contact phone number"}
    )
    submit = SubmitField('Submit')

 
class TeacherForm(FlaskForm):
    teacher_name = StringField(
        'Teacher Name', 
        validators=[
            DataRequired(
                message='You must provide the teacher\'s name.'
            ), 
            Length(min=2, max=100, 
                message="Name must be between 2 and 100 characters."
            )
        ],
        render_kw={"placeholder": "Enter the teacher's full name"}
    )
    tsc_no = IntegerField(
        'TSC No',
        validators=[
            Optional()
        ], 
        render_kw={"placeholder": "Enter the TSC number"}
    )
    id_no = IntegerField(
        'ID No', 
        validators=[DataRequired(
            message="The ID No of the Teacher must be provided.")
        ],
        render_kw={"placeholder": "Enter the ID number"}
    )
    phone_no = StringField(
        'Phone No', 
        validators=[
            DataRequired(message="Phone number is required."),
            Regexp(r'^\d{10}$', message="Enter a valid 10-digit phone number.")
        ],
        render_kw={"placeholder": "Enter a 10-digit phone number"}
    )
    email = StringField(
        'Email', 
        validators=[
            Optional(), 
            Email(message="Enter a valid email address.")
        ],
        render_kw={"placeholder": "Enter email address"}
    )
    gender = SelectField(
        'Gender', 
        validators=[
            DataRequired(
                message='You must select the teacher\'s gender.'
            )
        ],
        choices=[
            ('', 'Select Gender'), 
            ('male', 'Male'),
            ('female', 'Female')
        ], 
        default=''
    )
    submit = SubmitField('Add')

    # Custom validators
    def validate_tsc_no(self, field):
        if field.data:
            teacher = Teacher.query.filter_by(tsc_no=field.data).first()
            if teacher:
                raise ValidationError('TSC No already exists.')

    def validate_id_no(self, field):
        teacher = Teacher.query.filter_by(id_no=field.data).first()
        if teacher:
            raise ValidationError('ID No already exists.')

    def validate_phone_no(self, field):
        teacher = Teacher.query.filter_by(phone_no=field.data).first()
        if teacher:
            raise ValidationError('Phone number already exists.')

    def validate_email(self, field):
        if field.data:
            teacher = Teacher.query.filter_by(email=field.data).first()
            if teacher:
                raise ValidationError('Email address already exists.')
    
    def validate_teacher_name(self, field):
        if field.data:
            teacher = Teacher.query.filter_by(teacher_name=field.data).first()
            if teacher:
                raise ValidationError('There is a teacher with that username already.')
            


class UpdateForm(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        render_kw={"placeholder": "Enter current password"}
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            Length(min=4, max=20),
            Optional()
        ],
        render_kw={"placeholder": "Enter new password"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            EqualTo('new_password', message='Passwords must match.')
        ],
        render_kw={"placeholder": "Confirm password"}
    )
    phone_no = StringField(
        'Phone No', 
        validators=[
            Optional(),
            Regexp(r'^\d{10}$', message="Enter a valid 10-digit phone number.")
        ],
        render_kw={"placeholder": "Enter a 10-digit phone number"}
    )
    profile_picture = FileField(
        'Profile Picture',
        validators=[
            Optional(),
        ]
    )
    submit = SubmitField('Update')


class StreamForm(FlaskForm):
    name = StringField(
                'Stream Name', 
                validators=[
                    DataRequired(message='You must enter the name of the stream to add.')
                ]
            )


class GradeForm(FlaskForm):
    grade_name = SelectField(
        'Grade',
        choices=[('', 'Select Grade')] + [(f'Grade {i}', f'Grade {i}') for i in range(1, 10)],
        validators=[DataRequired(message='Please select a grade.')]
    )
    stream1 = StringField(
        'Stream 1',
         render_kw={"placeholder": "Enter stream 1 name"}
        )
    stream2 = StringField(
        'Stream 2',
         render_kw={"placeholder": "Enter stream 2 name"}
        )
    stream3 = StringField(
        'Stream 3',
         render_kw={"placeholder": "Enter stream 3 name"}
        )
    
    submit = SubmitField('Add')

    def validate_grade_name(self, field):
        if field.data == '':
            raise ValidationError('Please select a valid grade.')


class StudentRegistrationForm(FlaskForm):
    fullname = StringField(
        "Fullname", 
        validators=[
            DataRequired(message='You must enter the fullname of the student.'),
            Length(
                min=8, 
                max=50,
                message='Student name must be between 8-50 characters long.'
            )
        ],
    render_kw={"placeholder": "Enter student's name"}
    )

    grade = SelectField(
        'Grade',
        choices=[('', 'Select Grade')] + [(f'Grade {i}', f'Grade {i}') for i in range(1, 8)],
        validators=[InputRequired(message='Please select a grade.')]
    )

    dob = DateField(
        "Date of Birth", 
        format="%Y-%m-%d", 
        validators=[
            DataRequired(
                message='Please Select DOB to continue.'
            )
        ]
    )

    photo = FileField(
        "Photo", 
        validators=[Optional()]
    )

    adm_no = StringField(
        "Admission Number", 
        validators=[
            DataRequired(
                message='You must enter the student\'s adm no.'
            )
        ],
        render_kw={"placeholder": "Enter Adm no"}
    )

    adm_date = DateField(
        "Admission Date", 
        format="%Y-%m-%d", 
        validators=[
            DataRequired(
                message='Please enter the date the student was admitted.'
            )
        ]
    )

    gender = SelectField(
        "Gender", choices=[
            ("Male", "Male"), ("Female", "Female")
        ], 
        validators=[
            DataRequired(message='You must select student\s gender')
        ]
    )

    stream = StringField(
        "Stream", 
        validators=[Optional()]
    )

    previous_school = StringField(
        "Previous School", 
        validators=[Optional()],
        render_kw={"placeholder": "Enter previous school"}
    )

    parent_name = StringField(
        "Parent/Guardian Name", 
        validators=[
            DataRequired(
                message='Please provide fullname of the parent/guardian.'
            )
        ],
        render_kw={"placeholder": "Parent/Guardian's name"}
    )

    relationship = StringField(
        "Relationship with Student", 
        validators=[
            DataRequired(
                message='You must indicate the relationship with the student.'
            )
        ],
        render_kw={"placeholder": "Relationship with student"}
    )

    contact_phone = StringField(
        "Contact Information", 
        validators=[
            DataRequired(
                message='Phone number of the parent/guardian must be provided.'
            )
        ],
        render_kw={"placeholder": "07********"}
    )
    
    id_no = IntegerField("ID Number", 
        validators=[DataRequired(
            message='Please provide Id no of the parent/guardian.'
        )],
        render_kw={"placeholder": "Enter ID no"}
                    )
    email = EmailField(
        "Email", 
        validators=[Optional(), Email()],
        render_kw={"placeholder": "Enter Email"}
    )
    health_info = TextAreaField(
        "Health Information", 
        validators=[Optional()],
        render_kw={"placeholder": "Information about any chronical illiness"}
    )
    submit = SubmitField("Submit")


class SubjectForm(FlaskForm):
    subject = StringField(
        'Subject',
        validators = [
            DataRequired(message='Please enter a subject to add.')
        ],
        render_kw={"placeholder": "Enter Subject/Learning Area"}
    )
    add = SubmitField("Add Subject")


class ExamForm(FlaskForm):
    exam_name = StringField(
        'Exam Name',
        validators=[DataRequired(message="Please enter the exam name.")],
        render_kw={"placeholder": "Enter exam name"}
    )

    term = SelectField(
        'Term',
        choices=[
            ('', 'Select Term'),
            ('1', 'Term 1'),
            ('2', 'Term 2'),
            ('3', 'Term 3')
        ],
        validators=[DataRequired(message="Please select a term.")]
    )

    year = IntegerField(
        'Year',
        validators=[
            DataRequired(message="Please enter the exam year."),
            NumberRange(min=2000, max=2100, message="Enter a valid year.")
        ],
        render_kw={"placeholder": "Enter year (e.g., 2025)"}
    )

    exam_type = SelectField(
        'Exam Type',
        choices=[
            ('', 'Select Exam Type'),
            ('midterm', 'Midterm'),
            ('endterm', 'End Term'),
            ('mocks', 'Mock Exam'),
            ('assessment', 'Assessment')
        ],
        validators=[DataRequired(message="Please select an exam type.")]
    )

    exam_date = DateField(
        "Exam Date",
        validators=[DataRequired(message="Please select the exam date.")],
        format="%Y-%m-%d"
    )

    submit = SubmitField("Add Exam")