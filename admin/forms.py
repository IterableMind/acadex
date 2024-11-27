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
    PasswordField
)
from wtforms.validators import (
    DataRequired, 
    Length, 
    Email, 
    NumberRange, 
    Optional, 
    Regexp,
    EqualTo
)

class SearchStudent(FlaskForm):
    search_input = StringField(
        validators=[
            DataRequired(message="Please enter ADM No, Name, or UPI No!")
        ]
    )
    search_by = RadioField(
        "Search",
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