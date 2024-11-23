from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional

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
