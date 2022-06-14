from datetime import date
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from src.TennisApplication.models import User, Tournament, Club
from src.TennisApplication import db


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    birth_date = DateField('Birth Date', format="%Y-%m-%d", validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken! Please choose different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already taken! Please choose different one.')

    def validate_phone_number(self, phone_number):
        phone_number = phone_number.data.replace(' ', '')
        if len(phone_number) > 12:
            raise ValidationError('Invalid phone number.')
        for char in phone_number:
            if (char < '0' or char > '9') and char != '+':
                raise ValidationError('Invalid phone number.')

    def validate_birth_date(self, birth_date):
        if birth_date.data >= date.today():
            raise ValidationError('Invalid birth date.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    birth_date = DateField('Birth Date', format="%Y-%m-%d", validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken! Please choose different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already taken! Please choose different one.')

    def validate_phone_number(self, phone_number):
        phone_number = phone_number.data.replace(' ', '')
        if len(phone_number) > 12:
            raise ValidationError('Invalid phone number.')
        for char in phone_number:
            if (char < '0' or char > '9') and char != '+':
                raise ValidationError('Invalid phone number.')

    def validate_birth_date(self, birth_date):
        if birth_date.data >= date.today():
            raise ValidationError('Invalid birth date.')


class FilterReservations(FlaskForm):
    date = DateField('Date', format="%Y-%m-%d", validators=[DataRequired()])
    club_id = StringField('Club id', validators=[DataRequired()])
    court_number = IntegerField('Court number', validators=[DataRequired()])
    filter = SubmitField('Filter')

    def validate_date(self, birth_date):
        if birth_date.data < date.today():
            raise ValidationError('Invalid date.')


class MakeReservation(FlaskForm):
    date = DateField('Date', format="%Y-%m-%d", validators=[DataRequired()])
    club_id = StringField('Club id', validators=[DataRequired()])
    court_number = IntegerField('Court number', validators=[DataRequired()])
    hour_from = IntegerField('Hour from', validators=[DataRequired()])
    hour_to = IntegerField('Hour to', validators=[DataRequired()])
    submit = SubmitField('Reserve')

    def validate_date(self, birth_date):
        if birth_date.data < date.today():
            raise ValidationError('Invalid date.')


class TournamentForm(FlaskForm):
    date = DateField('Date', format="%Y-%m-%d", validators=[DataRequired()])
    club_id = IntegerField('Club id', validators=[DataRequired()])
    max_players = IntegerField('Max number of players', validators=[DataRequired()])
    winner_rewards = StringField('Rewards', validators=[Length(min=2, max=30)])
    min_skill_lvl = IntegerField('Skill lvl', validators=[])
    submit = SubmitField('Add')

    def validate_club_id(self, id):
        clubs_id = db.session.query(Club.id).all()
        for id_c in clubs_id:
            if id.data == id_c._data[0]:
                return
        raise ValidationError('Club doesn\'t exist')

    def validate_min_skill_lvl(self, skill_lvl):
        if skill_lvl.data < 0 or skill_lvl.data > 100:
            raise ValidationError('Incorrect skill level')