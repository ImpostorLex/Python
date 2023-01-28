from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired


class ToDoForm(FlaskForm):

    title = StringField(label='Title', validators=[DataRequired()])
    description = StringField(label='Description', validators=[DataRequired()])
