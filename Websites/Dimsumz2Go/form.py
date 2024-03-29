from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, DateField, URLField, SelectField, TextAreaField, FloatField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Regexp, InputRequired
from wtforms.validators import ValidationError
from flask_wtf.file import FileAllowed, FileRequired


class LoginForm(FlaskForm):

    username = StringField(label='Username', validators=[
                           DataRequired(), Length(min=4, max=30)])
    password = PasswordField(label='Password', validators=[
                             DataRequired(), Length(min=6, max=30)])


class RegistrationForm(FlaskForm):

    username = StringField(label='Username', validators=[
                           DataRequired(), Length(min=4, max=30)], render_kw={"placeholder": "JonTractor"})
    password = PasswordField(label='Password', validators=[
        DataRequired(), Length(min=6, max=30)], render_kw={"placeholder": "6+ Characters"})

    confirmPassword = PasswordField(label='Confirm Password', validators=[
                                    DataRequired()])

    firstName = StringField(label='First name', validators=[
                            DataRequired(), Length(min=2, max=30)], render_kw={"placeholder": "Jon"})

    lastName = StringField(label='Last name', validators=[
                           DataRequired(), Length(min=2, max=30)], render_kw={"placeholder": "Tractor"})

    role = SelectField("Role", validators=[DataRequired()], choices=[
                       'Normal', 'Chef', 'Accountant', 'Admin'])


class CreateForm(FlaskForm):

    recipe = StringField(label='Recipe Title', validators=[
                         DataRequired(), Length(min=3, max=32)], render_kw={"placeholder": "Burger"})
    desc = TextAreaField(label="Title Description", validators=[
        DataRequired(), Length(min=10, max=138)], render_kw={"placeholder": "A Krabby Patty made by spongebob", "cols":  50})

    url = FileField('Upload Image File')

    ingredients = SelectField(
        label="Select an Ingredient", validators=[DataRequired()])

    quantity = FloatField("Quantity", validators=[
                          DataRequired(), NumberRange(min=1, message='Please enter a valid number')], render_kw={"placeholder": "1"})
    price = FloatField("Price", validators=[DataRequired()])

    weight = SelectField(
        label="Select an Ingredient", validators=[DataRequired()], choices=[('oz', 'oz'), ('lb', 'lb'), ('g', 'g'), ('kg', 'kg')])

    instructions = TextAreaField(
        'Instructions of Recipe', validators=[DataRequired()], render_kw={"placeholder": "To cook this, you need the secret ingredient and some love.", "cols":  50})


class IngredientForm(FlaskForm):

    name = StringField(label='Ingredient', validators=[
        DataRequired(), Length(min=3, max=32)], render_kw={"placeholder": "Patty"})

    stock = FloatField(label="Quantity", validators=[
        DataRequired()], render_kw={"placeholder": "3"})

    price = FloatField(label="Price per unit", validators=[
        DataRequired()], render_kw={"placeholder": "1 lb of apple cost ₱150"})

    weight = SelectField(
        label="Weight Type", validators=[DataRequired()], choices=[('oz', 'oz'), ('lb', 'lb'), ('g', 'g'), ('kg', 'kg')])

    date_added = DateField('Date Added: YYYY/MM/DD',
                           validators=[DataRequired()])
    expiration_date = DateField(
        'Expiration Date: YYYY/MM/DD', validators=[DataRequired()])


class editIngredientForm(FlaskForm):

    name = StringField(label='Ingredient', validators=[
        DataRequired(), Length(min=3, max=32)], render_kw={"placeholder": "Patty"})

    stock = FloatField(label="Add a quantity,", validators=[
        InputRequired()], render_kw={"placeholder": "3"}, default=0)

    price = FloatField(label="Price", validators=[
        DataRequired()], render_kw={"placeholder": "20"})

    weight = SelectField(
        label="Weight Type", validators=[DataRequired()], choices=[('oz', 'oz'), ('lb', 'lb'), ('g', 'g'), ('kg', 'kg')])

    date_added = DateField('Date Added: YYYY/MM/DD',
                           validators=[DataRequired()])
    expiration_date = DateField(
        'Expiration Date: YYYY/MM/DD', validators=[DataRequired()])

    def __init__(self, current_stock, *args, **kwargs):
        super(editIngredientForm, self).__init__(*args, **kwargs)
        self.stock.label.text = f"Add a quantity, current stock is {current_stock}"
