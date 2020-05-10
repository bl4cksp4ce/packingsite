from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed,FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flasksite.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists!')

    def validate_email(self, email):

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists!')


class LoginForm(FlaskForm):

    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    #confirm_password = PasswordField('Confirm Password',
                                    # validators=[DataRequired(), EqualTo('password')]
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

#class ExcelForm(FlaskForm):
    #boxes = FileField \
     #   ('Add boxes', validators=[FileRequired(['xls', 'xlsx'])])
    #submit = SubmitField('Update')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField\
    ('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username :
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists!')

    def validate_email(self, email) :
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists!')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class ContainerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    x = IntegerField('X', validators=[DataRequired()])
    y = IntegerField('Y', validators=[DataRequired()])
    z = IntegerField('Z', validators=[DataRequired()])
    max_weight = IntegerField('Max Weight', validators=[DataRequired()])
    submit = SubmitField('Save')

class PackingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class BoxForm(FlaskForm):
    #excel_data = FileField \
    #    ('Update Profile Picture', validators=[FileAllowed(['xls', 'xlsx'])])
    name = StringField('Name', validators=[DataRequired()])
    x = IntegerField('X', validators=[DataRequired()])
    y = IntegerField('Y', validators=[DataRequired()])
    z = IntegerField('Z', validators=[DataRequired()])
    weight = IntegerField('Weight', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    r_x = BooleanField('X side:')
    r_y = BooleanField('Y side:')
    r_z = BooleanField('Z side:')
    up = BooleanField('Up:')
    down = BooleanField('Down:')
    submit = SubmitField('Save')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')