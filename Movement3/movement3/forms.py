from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, BooleanField, SelectField, TextAreaField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from movement3.models import User, Exercise, Comp, Point_Node
from urllib.parse import urlparse

class SignupForm(FlaskForm):
    email = StringField(
        'email', 
        validators=[
            DataRequired(), 
            Email(),
        ]
    )
    username = StringField(
        'username', 
        validators=[
            DataRequired(), 
            Length(min=2,max=20),
        ]
    )
    color = StringField(
        'color', 
    )
    height_ft = DecimalField(
        'height (ft)',
        validators=[
            DataRequired(), 
            NumberRange(min=1,max=7),
        ]
    )
    height_in = DecimalField(
        'height (in)',
        validators=[
            NumberRange(min=1,max=12),
        ]
    )
    weight = DecimalField(
        'weight'
    )
    password = PasswordField(
        'password', 
        validators=[
            DataRequired(), 
        ]
    )
    password_confirm = PasswordField(
        'confirm password', 
        validators=[
            DataRequired(), 
            EqualTo('password')
        ]
    )
    submit = SubmitField(
        'Sign up'
    )


    def validate_username(form, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(form, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('An account with this email already exists!')


class ProfileForm(FlaskForm):
    email = StringField(
        'email', 
        validators=[
            DataRequired(), 
            Email(),
        ]
    )
    username = StringField(
        'username', 
        validators=[
            DataRequired(), 
            Length(min=2,max=20),
        ]
    )
    color = StringField(
        'color', 
    )
    height = DecimalField(
        'height'
    )
    weight = DecimalField(
        'weight'
    )
    submit = SubmitField(
        'Update!'
    )



class LoginForm(FlaskForm):
    email = StringField(
        'email', 
        validators=[
            DataRequired(), 
            Email(),
        ]
    )
    password = PasswordField(
        'password', 
        validators=[
            DataRequired(), 
        ]
    )
    remember = BooleanField(
        'remember me'
    )
    submit = SubmitField(
        'Log in'
    )

    def validate_email(form, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if not user:
            raise ValidationError('There is no account associated with this email')

class AddExerciseForm(FlaskForm):
    name = StringField(
        'name', 
        validators=[
            DataRequired(), 
        ]
    )
    description = TextAreaField(
        'description',
        validators=[
            DataRequired(), 
        ]
    )
    value = StringField(
        'value',
        validators=[
            DataRequired(), 
        ]
    )
    link = StringField(
        'link',
        validators=[
            DataRequired(), 
        ]
    )
    unit = SelectField(
        'unit', 
        coerce=str
    )
    category = SelectField(
        'category',
        coerce=str
    )
    weighted = BooleanField(
        'weighted?'
    )
    submit = SubmitField(
        'Submit your request!'
    )

    def validate_name(form, name):
        exercise = Exercise.query.filter_by(name=name.data).first()
        if exercise:
            if(exercise.public == 0):
                raise ValidationError('An exercise with this name is already in the aproval process.')
            raise ValidationError('An exercise with this name aready exists.')

    def validate_link(form, link):
        data = urlparse(link.data)
        print(data)
        if(data.netloc != "www.youtube.com" and data.netloc != "youtu.be"):
            raise ValidationError('Please submit a valid youtube link.')

class UpdateExerciseForm(FlaskForm):
    name = StringField(
        'name', 
        validators=[
            DataRequired(), 
        ]
    )
    description = TextAreaField(
        'description',
        validators=[
            DataRequired(), 
        ]
    )
    value = StringField(
        'value',
        validators=[
            DataRequired(), 
        ]
    )
    link = StringField(
        'link',
        validators=[
            DataRequired(), 
        ]
    )
    unit = SelectField(
        'unit', 
        coerce=str
    )
    category = SelectField(
        'category', 
        coerce=str
    )
    weighted = BooleanField(
        'weighted?'
    )
    public = BooleanField(
        'public?'
    )
    submit = SubmitField(
        'Confirm your edit/aproval!'
    )

class LogExerciseForm(FlaskForm):
    exercise = SelectField(
        'exercise', 
        coerce=int
    )
    reps = FloatField(
        'Reps...',
        validators=[
            DataRequired(), 
        ]
    )
    weight = StringField(
        'Weight...',
    )
    selection = StringField(
        'Selection...',
        validators=[
            DataRequired(), 
        ]
    )

    submit = SubmitField(
        'Log!'
    )
    submit_more = SubmitField(
        'Log + more!'
    )

    def validate_reps(form, reps):
        reps_val = float(form.reps.data)
        weight_val = 0
        if(form.weight.data != None): weight_val = form.weight.data
        if(weight_val == ""): weight_val = 0
        weight_val = float(weight_val)
        val = Exercise.query.filter_by(name=form.selection.data).first().calculate(reps_val,weight_val)
        print(val)
        if(val <= 0 or weight_val < 0 or reps_val <= 0):
            raise ValidationError('You can only submit exercises with a positive value')

class StartCompForm(FlaskForm):
    name = StringField(
        'name', 
        validators=[
            DataRequired(), 
        ]
    )
    goal = DecimalField(
        'goal', 
        validators=[
            DataRequired(), 
        ]
    )
    group_link = StringField(
        'group link', 
    )
    users = SelectMultipleField(
        'users', 
        coerce=int
    )
    exercises = SelectMultipleField(
        'users', 
        coerce=int
    )
    accept_new = BooleanField(
        'accept new exercises'
    )
    repeating = BooleanField(
        'repeat'
    )
    global_comp = BooleanField(
        'global'
    )
    bonus_time = DecimalField(
        'bonus time'
    )
    days_off = DecimalField(
        'days off'
    )
    submit = SubmitField(
        'Start!'
    )

    def validate_group_link(form, group_link):
        if(group_link.data != ""):
            data = urlparse(group_link.data)
            if(data.netloc != "groupme.com"):
                raise ValidationError('Please submit a valid GroupMe link.')

    def validate_users(form,users):
        if(len(users.data) < 2):
            raise ValidationError('You need at least 2 users to start a comp.')


    def validate_name(form,name):
        comp = Comp.query.filter_by(name=name.data).first()
        if comp:
            raise ValidationError('There is already a comp with that name')
        for i in range(100):
            comp = Comp.query.filter_by(name=name.data+" "+str(i)).first()
            if comp:
                raise ValidationError('There is already a comp with that name')

class JoinCompForm(FlaskForm):
    code = StringField(
        'Join Code', 
        validators=[
            DataRequired(), 
            Length(min=8,max=8),
        ]
    )
    submit = SubmitField(
        'Join!'
    )

class RequestResetForm(FlaskForm):
    email = StringField(
        'email', 
        validators=[
            DataRequired(), 
            Email(),
        ]
    )
    submit = SubmitField(
        'Submit'
    )



class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'password', 
        validators=[
            DataRequired(), 
        ]
    )
    password_confirm = PasswordField(
        'confirm password', 
        validators=[
            DataRequired(), 
            EqualTo('password')
        ]
    )
    submit = SubmitField(
        'Reset'
    )