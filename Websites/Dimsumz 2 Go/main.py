from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from icecream import ic
from flask_hashing import Hashing
from form import LoginForm, RegistrationForm, CreateForm, IngredientForm
from time import sleep
from functools import wraps
from sqlalchemy import Date


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dimsumz2go.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key hehelol'
login_manager = LoginManager()
login_manager.init_app(app)
hashing = Hashing(app)
db = SQLAlchemy(app)
user_type = 0


# -------------------------------- Database Design -------------------------------- #

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    # username is the primary key constraint and of course id is the primary key
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(450), unique=False, nullable=False)
    access_type_id = db.Column(db.Integer, db.ForeignKey('access_type.id'))


class Employees(UserMixin, db.Model):

    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(250), unique=False, nullable=False)
    lastName = db.Column(db.String(250), unique=False, nullable=False)


class accessType(UserMixin, db.Model):
    __tablename__ = 'access_type'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role = db.Column(db.String(100), unique=False, nullable=False)


class menuItem(db.Model):

    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=False, nullable=False)
    desc = db.Column(db.String(138), unique=False, nullable=False)
    cost = db.Column(db.Float(20), nullable=False)


class Image(db.Model):

    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey(
        'menu_item.id'), nullable=False)
    path = db.Column(db.String(250), nullable=False)
    instructions = db.Column(db.String(1500), nullable=False)


class Sale(db.Model):

    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey(
        'menu_item.id'), nullable=False)
    date_added = db.Column(Date, nullable=False)
    profit = db.Column(db.Float, nullable=False)


class Ingredient(db.Model):

    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float(20), nullable=False)
    weight_id = db.Column(db.Integer, db.ForeignKey(
        'weight.id'), nullable=False)


class Weight(db.Model):

    __tablename__ = 'weight'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=False, nullable=False)


class menuItemIngredient(db.Model):

    __tablename__ = 'menu_item_ingredients'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey(
        'menu_item.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey(
        'ingredient.id'), nullable=False)
    list_order = db.Column(db.Integer, nullable=False)
    weight_id = db.Column(db.Integer, db.ForeignKey(
        'weight.id'), nullable=False)


# --------------------------------^ Database Design ^-------------------------------- #
db.create_all()


def check_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_url = request.path

        id_and_url = (user_type, current_url)

        categories = [(1, "/recipes"), (2, "/graphs"), (2, '/inventory'), (3, '/recipes'),
                      (3, '/inventory'), (4, '/recipes'), (4, '/graphs'), (4, '/inventory')]

        if id_and_url in categories:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('unauthorized'))
    return wrapper

# ---------------------------- FLASK FUNCTIONS ----------------------------


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():

    form = CreateForm()

    # TODO: Will be populated by the ingredients table but for now these are the choices
    form.ingredients.choices = []

    all_ingredients = Ingredient.query.all()

    for ingredient in all_ingredients:

        key_pair_value = (ingredient.cost, ingredient.name)
        form.ingredients.choices.append(key_pair_value)

    if request.method == 'POST' and form.validate_on_submit():

        cost = []
        quantity = []
        weight = []

        ingredients_name = []
        # Get the key-pair value for the Ingredients field but only the value for other fieds
        for key, value in request.form.items():
            if key.startswith('ingredients-field-') or key == 'ingredients':
                cost.append(float(value))
            elif key.startswith('quantity-field-') or key == 'quantity':
                quantity.append(value)
            elif key.startswith('weight-field-') or key == 'weight':
                weight.append(value)

            choice = next(
                (c for c in form.ingredients.choices if c[0] == value), None)
            if choice is not None:
                # Append the stored value to the ingredients list
                ingredients_name.append(choice[1])

        # First insert a row into the menuItem table
        recipe = request.form.get('recipe')
        desc = request.form.get('desc')
        cost = sum(cost)
        menu_item = menuItem(name=recipe, desc=desc, cost=cost)
        db.session.add(menu_item)
        db.session.commit()

        # Get the id of the inserted menu
        menu_id = menu_item.id
        ic(menu_id)

        # Insert url and instruction and as well as the menu_id as the foreign key to the image table
        url = request.form.get('url')
        instructions = request.form.get('instructions')
        image = Image(menu_item_id=menu_id, path=url,
                      instructions=instructions)
        db.session.add(image)
        db.session.commit()

        return redirect(url_for('recipes'))

    return render_template('create.html', form=form, error="")


@app.route("/dashboard", methods=['GET', 'POSTS'])
@login_required
def dashboard():
    global user_type

    user = Users.query.filter_by(username=current_user.username).first()

    user_type = user.access_type_id

    return render_template("dashboard.html", user=user_type)


@app.route('/', methods=['POST', 'GET'])
def index():

    forms = LoginForm()

    if request.method == 'POST' and forms.validate_on_submit():

        username = request.form.get('username')
        password = request.form.get('password')

        hashed = hashing.hash_value(password, salt="abcd")

        is_user_exists = Users.query.filter_by(
            username=username, password=hashed).first()

        if is_user_exists:
            login_user(is_user_exists)
            return redirect(url_for('dashboard'))
        else:

            return render_template("login.html", form=forms, error="Username or Password does not match")

    return render_template("login.html", form=forms)


@app.route('/create-ingredient', methods=['GET', 'POST'])
def addIngredients():

    form = IngredientForm()

    if form.validate_on_submit() and request.method == 'POST':

        name = request.form.get('name')
        stock = request.form.get('stock')
        price = request.form.get('price')
        weight = request.form.get('weight')

        weight_id = Weight.query.filter_by(name=weight).first()

        ingredient = Ingredient(name=name, quantity=stock,
                                cost=price, weight_id=weight_id.id)

        db.session.add(ingredient)
        db.session.commit()

        return redirect(url_for('inventory'))

    return render_template("ingredientForm.html", form=form)


@app.route('/graphs', methods=['GET', 'POST'])
@check_user
def graphs():

    return "For Accountant"


@app.route('/home', methods=['GET', 'POST'])
def home():

    return "<h1>Simple static website for users</h1>"


@app.route('/inventory', methods=['GET', 'POST'])
@login_required
@check_user
def inventory():

    return render_template('ingredient.html')


@app.route('/item/<int:num>', methods=['GET', 'POST'])
@login_required
# @check_user TODO find a way to implement this:
def item(num):

    img = Image.query.filter_by(id=num).first()

    return f"{num} {img}"


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()

    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    # TODO create a what role for register to be automatically populated
    form = RegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():

        username = request.form.get('username')
        password = request.form.get('password')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        role = request.form.get('role')
        confirm = request.form.get('confirmPassword')

        if password != confirm:

            return render_template("register.html", error="Password must match!", form=form)
        else:
            h = hashing.hash_value(password, salt='abcd')

            is_username_exists = Users.query.filter_by(
                username=username).first()

            if is_username_exists:

                return render_template("register.html", error="Oops it seems like that username exists", form=form)

            else:

                # First insert a row into the Employees table
                employee = Employees(firstName=firstName, lastName=lastName)
                db.session.add(employee)
                db.session.commit()

                # Get the id of the inserted employee and get id of the name of the role
                employee_id = employee.id
                auth_level = accessType.query.filter_by(role=role).first()
                auth_id = auth_level.id
                ic(f"Employee ID is: {employee_id} and Auth Level is : {auth_id}")

                # Insert a row into the Users table with the employee_id as the foreign key and access_type id as well
                user = Users(username=username, password=h,
                             employee_id=employee_id, access_type_id=auth_id)
                db.session.add(user)
                db.session.commit()

                return redirect(url_for('index'))

    return render_template("register.html", form=form)


@app.route('/recipes', methods=['GET', 'POST'])
@login_required
@check_user
def recipes():

    menus = menuItem.query.all()
    imgs = Image.query.all()

    return render_template("recipes.html", menu=menus, img=imgs, zip=zip)


@app.route("/unauthorized", methods=['GET', 'POST'])
def unauthorized():

    return render_template("unauthorized.html")


@login_manager.user_loader
def load_user(user_id):

    return Users.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True)
