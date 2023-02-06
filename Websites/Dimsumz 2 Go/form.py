from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):

    username = StringField(label='Username', validators=[
                           DataRequired(), Length(min=4, max=30)])
    password = PasswordField(label='Password', validators=[
                             DataRequired(), Length(min=6, max=30)])


class RegistrationForm(FlaskForm):

    username = StringField(label='Username', validators=[
                           DataRequired(), Length(min=4, max=30)])
    password = PasswordField(label='Password', validators=[
        DataRequired(), Length(min=6, max=30)])

    confirmPassword = PasswordField(label='Confirm Password', validators=[
                                    DataRequired()])

    firstName = StringField(label='First name', validators=[
                            DataRequired(), Length(min=2, max=30)])

    lastName = StringField(label='Last name', validators=[
                           DataRequired(), Length(min=2, max=30)])
