from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, URLField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_ckeditor import CKEditorField


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


class CreateForm(FlaskForm):

    recipe = StringField(label='Recipe', validators=[
                         DataRequired(), Length(min=3, max=32)])
    desc = StringField(label="Title Description", validators=[
                       DataRequired(), Length(min=10, max=138)])
    url = URLField(label='URL of the image', validators=[
                   DataRequired(), Length(min=20, max=250)])
    ingredients = SelectField(
        label="Select an Ingredient", validators=[DataRequired()])

    instructions = CKEditorField(
        'Instructions of Recipe', validators=[DataRequired()])
