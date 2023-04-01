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
    quantity = db.Column(db.Integer, nullable=False)


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

# Create Recipe Form


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():

    form = CreateForm()

    form.ingredients.choices = []

    all_ingredients = Ingredient.query.all()

    for ingredient in all_ingredients:

        # Extract Ingredients
        form.ingredients.choices.append(ingredient.name)

    if request.method == 'POST' and form.validate_on_submit():

        cost = set()
        quantity = []
        weight = []
        ingredients_name = []

        for key, value in request.form.items():
            print(f"key: {key}, value: {value}")

       # Get the key-pair value for the Ingredients field but only the value for other fieds
        for key, value in request.form.items():
            if key.startswith('ingredients-field-') or key == 'ingredients':
                # cost.add(float(value))
                ingredients_name.append(value)
            elif key.startswith('quantity-field-') or key == 'quantity':
                quantity.append(value)
            elif key.startswith('weight-field-') or key == 'weight':
                weight.append(value)

        # Query the cost for each Ingredients added
        for i, q in zip(ingredients_name, quantity):
            get_ingredients_cost = Ingredient.query.filter_by(name=i).first()
            cost.add(float(get_ingredients_cost.cost) * float(q))

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

        ctr = 1
        for i, w, q in zip(ingredients_name, weight, quantity):

            get_id_of_ingredient = Ingredient.query.filter_by(name=i).first()
            get_id_of_weight = Weight.query.filter_by(name=w).first()

            # Insert menu_id recently created and other details such as list_order and weight_id
            insert_ingredient = menuItemIngredient(
                menu_item_id=menu_id, ingredient_id=get_id_of_ingredient.id, list_order=ctr, weight_id=get_id_of_weight.id, quantity=q)

            ctr += 1
            db.session.add(insert_ingredient)
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


# TODO: Check Users
@app.route('/edit/<int:num>', methods=['GET', 'POST'])
@login_required
def edit(num):

    form = CreateForm()

    form.ingredients.choices = []

    all_ingredients = Ingredient.query.all()

    # Set pre-set value using the to be edit Recipe

    img = Image.query.filter_by(id=num).first()
    form.url.data = img.path
    form.instructions.data = img.instructions

    menu = menuItem.query.filter_by(id=num).first()
    form.recipe.data = menu.name
    form.desc.data = menu.desc

    for ingredient in all_ingredients:

        # Extract Ingredients
        form.ingredients.choices.append(ingredient.name)

    get_ingredients = menuItemIngredient.query.filter_by(
        menu_item_id=menu.id).all()

    if request.method == 'POST' and form.validate_on_submit():

        cost = set()
        quantity = []
        weight = []
        ingredients_name = []

       # Get the key-pair value for the Ingredients field but only the value for other fieds
        for key, value in request.form.items():
            if key.startswith('ingredients-field-') or key == 'ingredients':
                # cost.add(float(value))
                ingredients_name.append(value)
            elif key.startswith('quantity-field-') or key == 'quantity':
                quantity.append(value)
            elif key.startswith('weight-field-') or key == 'weight':
                weight.append(value)

        # Query the cost for each Ingredients added
        for i, q in zip(ingredients_name, quantity):
            get_ingredients_cost = Ingredient.query.filter_by(name=i).first()
            cost.add(float(get_ingredients_cost.cost) * float(q))

        recipe = request.form.get('recipe')
        desc = request.form.get('desc')
        cost = sum(cost)

        # Query the row to be updated, in this case the menuItem table first
        menu = menuItem.query.filter_by(id=num).first()
        menu.recipe = recipe
        menu.desc = desc
        menu.cost = cost

        # Second Query the Image table
        image = Image.query.filter_by(menu_item_id=num).first()
        image.path = request.form.get('url')
        image.instructions = request.form.get('instructions')

        menu_item_ingredients = menuItemIngredient.query.filter_by(
            menu_item_id=num).all()

        # Query all the ids related to the TO BE edited recipe.
        ids = [int(ingre.id) for ingre in menu_item_ingredients]

        # Query all the IDs of weight and ingredients
        ingredient_ids = []
        weight_ids = []
        for ingre, wei in zip(ingredients_name, weight):

            query_ingredient = Ingredient.query.filter_by(name=ingre).first()
            ingredient_ids.append(query_ingredient.id)

            query_weight = Weight.query.filter_by(name=wei).first()
            weight_ids.append(query_weight.id)

        # Update ingredient_id and weight_id of menuItemIngredients accordingly to the ids queried.
        for id, i2, w2 in zip(ids, ingredient_ids, weight_ids):

            row = menuItemIngredient.query.filter_by(id=id).first()

            row.ingredient_id = i2
            row.weight_id = w2

        return f"Something {ids}"

        # ctr += 1
        # db.session.add(insert_ingredient)
        # db.session.commit()

        return f"{recipe}, {desc}, {cost}"

    return render_template('editRecipe.html', form=form, list_length=len(get_ingredients), num=num)


@ app.route('/', methods=['POST', 'GET'])
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


# Create Ingredient Form
@ app.route('/create-ingredient', methods=['GET', 'POST'])
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

    get_ingredients = Ingredient.query.all()

    weight_list = []

    for i in get_ingredients:

        weight_cat = Weight.query.filter_by(id=i.weight_id).first()
        weight_list.append(weight_cat.name)

    return render_template('ingredient.html', ingre=get_ingredients, zip=zip, weight_list=weight_list)


@app.route('/item/<int:num>', methods=['GET', 'POST'])
@login_required
# @check_user TODO find a way to implement this:
def item(num):

    img = Image.query.filter_by(id=num).first()
    menu_item = menuItem.query.filter_by(id=num).first()
    get_instructions = menuItemIngredient.query.filter_by(
        menu_item_id=num).all()

    ic(get_instructions)

    ingredient_list = []
    for ingre in get_instructions:

        weight = Weight.query.filter_by(id=ingre.weight_id).first()
        ingredient = Ingredient.query.filter_by(id=ingre.ingredient_id).first()

        ingredient_list.append(
            f"{ingre.list_order}) {ingredient.name} x{ingre.quantity} {weight.name}")

    return render_template('viewRecipe.html', img=img, menu=menu_item, list=ingredient_list, num=num)


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
