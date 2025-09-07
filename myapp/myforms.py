from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,TextAreaField,SubmitField,PasswordField,SelectField,DateField
from wtforms.validators import DataRequired,Email,EqualTo,Length
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from myapp.models import ApprovalStatusEnum
from datetime import datetime




class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(message='Please enter a valid email address'), Email()])
    password = PasswordField('Password', validators=[DataRequired(message='Password cannot be empty')])
    # checkbox = BooleanField('By checking, you accept our',validators=[DataRequired()])
    login = SubmitField('Login')




class RegistrationForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(message='Please enter your first name')])
    lname = StringField('Last Name', validators=[DataRequired(message='Please enter your last name')])
    email = EmailField('Email', validators=[DataRequired(message='Enter a valid email address'), Email()])
    phone = StringField('Phone', validators=[DataRequired(message='Enter phone number')])
    password = PasswordField('Password', validators=[DataRequired(message='Enter password'), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    signup = SubmitField('Register')


class OnboardingForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(message='Please enter your fisrt name')])
    lastname = StringField('Last Name', validators=[DataRequired(message='Please enter your last name')])
    email = EmailField('Email', validators=[DataRequired(message='Enter a valid email address'), Email()])
    phone = StringField('Phone', validators=[DataRequired(message='Enter phone number')])
    onboard = SubmitField('Onboard')




class ContactForm(FlaskForm):
    fullname = StringField('Full name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    send = SubmitField('Send Message')

class NewRequest(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    company = StringField('Company', validators=[DataRequired()])
    job_role = StringField('Job role', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(message='Enter a valid email address'), Email()])
    phone = StringField('Phone', validators=[DataRequired(message='Enter phone number')])

    # user_id = SelectField('Assigned User', coerce=int)
    id_card = SelectField(
        "ID Card",
        choices=[
            ('visitor', 'Visitor ID'),
            ('permanent', 'Permanent ID'),
            ('not_applicable', 'Not Applicable')
        ],
        default='visitor',
        validators=[DataRequired()]
    )
    # id_card = SelectField('ID Card', coerce=int)
    status = SelectField(
        "Approval Status",
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ],
        default='PENDING',
        validators=[DataRequired()],
    )
    
    expected_date = DateField('Expected Date', format='%Y-%m-%d', validators=[DataRequired()])
    departure_date = DateField('Departure Date', format='%Y-%m-%d', validators=[DataRequired()])
    duration = StringField('duration', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    purpose = TextAreaField('Purpose of visit', validators=[DataRequired()])
    document = MultipleFileField('Upload Documents (PDF only)', validators=[FileAllowed(['pdf'], 'PDFs only!')])

    submit = SubmitField('Send Request')

class StatusUpdateForm(FlaskForm):
    status = SelectField(
        'Approve/Reject',
        choices=[(status.name, status.value) for status in ApprovalStatusEnum],
        validators=[DataRequired()]
    )
    update = SubmitField('Submit')

# class UpdateTask(FlaskForm):
#     task_name = StringField('Task Name', render_kw={'readonly': True, 'class': 'form-control'}, validators=[DataRequired()])
#     task_description = TextAreaField('Task Description', render_kw={'readonly': True, 'class': 'form-control'}, validators=[DataRequired()])
#     user_id = SelectField('Assigned User', render_kw={'disabled': True, 'class': 'form-control'}, coerce=int)
#     task_status = SelectField(
#         "Task Status",
#         choices=[
#             ('pending', 'pending'),
#             ('assigned', 'assigned'),
#             ('Completed', 'Completed')
#         ],
#         default='Not Started',
#         validators=[DataRequired()],
#     )
    
    start_date = DateField('Start Date', render_kw={'readonly': True, 'class': 'form-control'}, format='%Y-%m-%d', validators=[DataRequired()], default=datetime.today)
    end_date = DateField('End Date', render_kw={'readonly': True, 'class': 'form-control'}, format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Create Task')


# class UpdateTask(FlaskForm):
#     taskname = StringField('Task Name',  render_kw={'readonly': True, 'class': 'form-control'}, validators=[DataRequired()])
#     taskdescription = TextAreaField('Task Description', render_kw={'readonly': True, 'class': 'form-control'}, validators=[DataRequired()])
#     user_id = SelectField('Assigned User', render_kw={'readonly': True, 'class': 'form-control'}, coerce=int)
#     taskstatus = SelectField(
#         "Task Status",
#         choices=[
#             ('pending', 'pending'),
#             ('assigned', 'assigned'),
#             ('Completed', 'Completed')
#         ],
#         default='Not Started',
#         validators=[DataRequired()],
        
#     )
#     start_date = DateField('Start Date', render_kw={'readonly': True, 'class': 'form-control'}, format='%Y-%m-%d', validators=[DataRequired()],default=datetime.today)
#     end_date = DateField('End Date', render_kw={'readonly': True, 'class': 'form-control'}, format='%Y-%m-%d', validators=[DataRequired()])
#     submit = SubmitField('Create Task')

# class UpdateTask(FlaskForm):
#     taskname = StringField('Task Name', validators=[DataRequired()])
#     taskdescription = TextAreaField('Task Description', validators=[DataRequired()])
   
#     submit = SubmitField('Update Task')

# class DeleteTask(FlaskForm):
#     submit = SubmitField('Delete Task')



    

