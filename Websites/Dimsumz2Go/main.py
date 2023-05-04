from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from icecream import ic
from flask_hashing import Hashing
from form import LoginForm, RegistrationForm, CreateForm, IngredientForm
from time import sleep
from functools import wraps
from sqlalchemy import Date
from datetime import datetime
from itertools import zip_longest
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dimsumz2go.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key hehelol'
app.config['UPLOAD_FOLDER'] = 'static/recipesImgs'
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


class ingredientDateExpiration(db.Model):

    __tablename__ = 'ingredientDateExpiration'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey(
        'ingredient.id'), nullable=True)
    quantity_added = db.Column(db.Float(20), nullable=False)
    date_added = db.Column(db.Date, nullable=False,
                           default=datetime.utcnow().date())
    date_expiration = db.Column(
        db.Date, nullable=False, default=datetime.utcnow().date())


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


# -------------------------------- User Defined Functions -------------------------------- #
db.create_all()


def isImage(img):

    allowed_filetype = ['jpg', 'png']
    file_ext = img.data.rsplit('.', 1)[1]
    if file_ext in allowed_filetype:

        # Save the image to the file path.
        filename = secure_filename(img.data.filename)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return "Yes"
    else:
        return 'Error'


def check_Quantity(items):

    errors = []  # list to store any errors that occur
    for val in items:
        try:
            ic(val)
            val = float(val)
            if val <= 0:
                raise ValueError
        except ValueError:
            ic("Value Error")
            val = str(val)
            error_msg = f"Please input only numbers and should not be less than or equals to zero: {val}"
            errors.append(error_msg)
        except TypeError:
            ic("Type Error")
            val = str(val)
            error_msg = f"Please input only numbers and should not be less than or equals to zero: {val}"
            errors.append(error_msg)

    if len(errors) == 0:
        # return None if there are no errors
        return None
    else:
        # return the list of error messages if there are errors
        return errors


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


def updateQuery(ingredients, quantity, weight, recipe, desc, num, isPushed):

    # Check for quantity errors first
    error_messages = check_Quantity(quantity)
    if error_messages is not None:
        ic(error_messages)
        # redirect to error page if any errors occurred
        return error_messages
    else:
        ic("Update is else")
        total = 0

        # If true then remove all dynamically added Fields first.
        if isPushed == "pushed":

            # Query all of specific ingredient:
            all = menuItemIngredient.query.filter_by(menu_item_id=num).all()

            for row in all[1:]:

                db.session.delete(row)

            db.session.commit()

        # Query the cost for each Ingredients added
        for i, q in zip(ingredients, quantity):

            get_ingredients_cost = Ingredient.query.filter_by(name=i).first()
            total += float(get_ingredients_cost.cost) * float(q)

        # Query the row to be updated, in this case the menuItem table first
        menu = menuItem.query.filter_by(id=num).first()
        menu.name = recipe
        menu.desc = desc
        menu.cost = total

        # Second Query the Image table
        image = Image.query.filter_by(menu_item_id=num).first()
        image.path = request.form.get('url')
        image.instructions = request.form.get('instructions')

        menu_item_ingredients = menuItemIngredient.query.filter_by(
            menu_item_id=num).all()

        # Query all the ids related to the TO BE edited recipe.
        ids = [int(ingre.id) for ingre in menu_item_ingredients]

        ingredient_ids = []
        weight_ids = []

        # Query all the IDs of weight and ingredients
        for ingre, wei in zip(ingredients, weight):

            query_ingredient = Ingredient.query.filter_by(name=ingre).first()
            ingredient_ids.append(query_ingredient.id)

            query_weight = Weight.query.filter_by(name=wei).first()
            weight_ids.append(query_weight.id)

        ctr = 0
        # Update ingredient_id and weight_id of menuItemIngredients accordingly to the ids queried.
        for id, i2, w2, q2 in zip(ids, ingredient_ids, weight_ids, quantity):

            ctr += 1
            row = menuItemIngredient.query.filter_by(id=id).first()
            row.ingredient_id = i2
            row.weight_id = w2
            row.quantity = q2

        # Check if the old numbers of SelectField has changed i.e from 3 to 4

        old = len(menu_item_ingredients)
        new = len(ingredients)

        if old != new and len(ingredients) != 1:

            # Add the new Fields

            for i in range(old, new):

                # Query for the ids of the weight, ingredients and add them

                get_weight_id = Weight.query.filter_by(name=weight[i]).first()
                get_ingredient_id = Ingredient.query.filter_by(
                    name=ingredients[i]).first()

                if get_weight_id and get_ingredient_id:

                    ctr += 1

                    # Add the rows
                    menuItemIngredientsInsert = menuItemIngredient(
                        menu_item_id=num, ingredient_id=get_ingredient_id.id, list_order=ctr, weight_id=get_weight_id.id, quantity=quantity[i])

                    db.session.add(menuItemIngredientsInsert)

        db.session.commit()
        return "Success"


unit_map = {
    'oz': 28.35,   # 1 oz = 28.35 g
    'lb': 453.59,  # 1 lb = 453.59 g
    'g': 1,
    'kg': 1000    # 1 kg = 1000 g
}


def gramToOriginal(weight_type, remaining):

    if weight_type == 'kg':

        return round(remaining / 1000, 2)

    elif weight_type == 'lb':

        return round(remaining / 453.59, 2)

    elif weight_type == 'g':

        return remaining
    elif weight_type == 'oz':

        return round(remaining / 28.35, 2)
    else:

        return "404"


def ingredient_to_dict(ingredient):
    return {'id': ingredient.id, 'name': ingredient.name, 'quantity': ingredient.quantity, 'cost': ingredient.cost, 'weight_id': ingredient.weight_id}

# ---------------------------- FLASK FUNCTIONS ----------------------------

# Create Recipe Form


@app.route('/buyMenu/<string:name>')
def buyMenu(name):

    orders = int(request.args.get('quantity'))

    # Get menuItem ID to find all required ingredients in menu_item_ingredients
    _menuItem = menuItem.query.filter_by(name=name).first()

    # Retrieve all associated menu_item_ingredients rows with menuItem
    _menuItemIngredient = menuItemIngredient.query.filter_by(
        menu_item_id=_menuItem.id).all()

    # Count total cost
    total_cost = float(_menuItem.cost) * orders

    onhand_ingredient_list = []
    onhand_quantity_list = []
    onhand_weight_list = []

    # Contains the unique ingredients
    req_ingredient_list = []

    # Contains the non unique ingredients
    dup_req_ingredient_list = []

    for item in _menuItemIngredient:
        # Query the ingredient name to be appended
        req_ingredient_name = Ingredient.query.filter_by(
            id=item.ingredient_id).first()

        if req_ingredient_name.name not in [t[0] for t in req_ingredient_list]:
            # Query the weight name to be appended
            req_weight_name = Weight.query.filter_by(id=item.weight_id).first()

            unq = (req_ingredient_name.name,
                   item.quantity, req_weight_name.name)
            req_ingredient_list.append(unq)

        # If else then append the dups to the duplicate list
        else:
            dup_req_weight_name = Weight.query.filter_by(
                id=item.weight_id).first()

            dup = (req_ingredient_name.name,
                   item.quantity, dup_req_weight_name.name)
            dup_req_ingredient_list.append(dup)

            # Move the matching tuple from req_ingredient_list to the dup_req_ingredient_list
            matching_tuples = [
                t for t in req_ingredient_list if t[0] == req_ingredient_name.name]
            tuple_to_remove = matching_tuples[0]
            req_ingredient_list.remove(tuple_to_remove)
            dup_req_ingredient_list.append(tuple_to_remove)

    ic(req_ingredient_list, dup_req_ingredient_list)

    # Outputs; ic| req_ingredient_list: [('Lemon', 4, 'oz')]
   #  dup_req_ingredient_list: [('Patty', 1, 'kg'), ('Patty', 2, 'lb')]

    return "Yey"


@app.route('/quantityError', methods=['GET', 'POST'])
def quantityError():

    error = request.args.get('error')
    num = request.args.get('num')

    if num is None:
        return render_template('popupDelete.html', error=error, num="")
    elif num is not None:
        return render_template('popupDelete.html', error=error, num=num)

# TODO: Add quantity validation to this page.


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():

    form = CreateForm()

    form.ingredients.choices = []

    all_ingredients = Ingredient.query.all()

    for ingredient in all_ingredients:

        # Extract Ingredients
        form.ingredients.choices.append(ingredient.name)

    if form.validate_on_submit():
        ic("true")
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

        is_all_quantity = check_Quantity(quantity)

        if is_all_quantity:
            return redirect(url_for('quantityError', error=is_all_quantity))
        else:
            # Query the cost for each Ingredients added
            for i, q in zip(ingredients_name, quantity):
                get_ingredients_cost = Ingredient.query.filter_by(
                    name=i).first()
                cost.add(float(get_ingredients_cost.cost) * float(q))

            # First insert a row into the menuItem table
            recipe = request.form.get('recipe')
            ic(recipe)
            desc = request.form.get('desc')
            cost = sum(cost)
            menu_item = menuItem(name=recipe, desc=desc, cost=cost)
            db.session.add(menu_item)
            db.session.commit()

            # Get the id of the inserted menu
            menu_id = menu_item.id
            ic(f"{menu_id} what")

            # Insert url and instruction and as well as the menu_id as the foreign key to the image table
            url2 = form.url
            url = form.url.data

            is_valid_filetype = isImage(url2)

            if is_valid_filetype == "Error":
                return redirect(url_for('create', error="File type is invalid only images."))
            instructions = request.form.get('instructions')
            image = Image(menu_item_id=menu_id, path=url,
                          instructions=instructions)
            db.session.add(image)
            db.session.commit()

            ctr = 1
            for i, w, q in zip(ingredients_name, weight, quantity):

                get_id_of_ingredient = Ingredient.query.filter_by(
                    name=i).first()
                get_id_of_weight = Weight.query.filter_by(name=w).first()

                # Insert menu_id recently created and other details such as list_order and weight_id
                insert_ingredient = menuItemIngredient(
                    menu_item_id=menu_id, ingredient_id=get_id_of_ingredient.id, list_order=ctr, weight_id=get_id_of_weight.id, quantity=q)

                ctr += 1
                db.session.add(insert_ingredient)
                db.session.commit()

            return redirect(url_for('recipes'))

    elif form.validate_on_submit() == False:
        first_field = []
        for key, value in request.form.items():
            if key.startswith('quantity-field-') or key == 'quantity':
                first_field.append(value)
        has_errors = check_Quantity(first_field)

        if has_errors:
            return redirect(url_for('quantityError', error=has_errors))

    error_msgs = request.args.get('error')
    return render_template('create.html', form=form, error=error_msgs, error2="")


@app.route("/dashboard", methods=['GET', 'POSTS'])
@login_required
def dashboard():
    global user_type

    user = Users.query.filter_by(username=current_user.username).first()

    user_type = user.access_type_id

    message = request.args.get('message')

    return render_template("dashboard.html", user=user_type, message=message)


@app.route('/delete/<int:num>', methods=['GET', 'POST'])
@login_required
def delete(num):

    # Delete dependencies table first

    img = Image.query.filter_by(menu_item_id=num).first()
    db.session.delete(img)

    menuItem_Ingredients = menuItemIngredient.query.filter_by(
        menu_item_id=num).all()

    for ingredient in menuItem_Ingredients:
        db.session.delete(ingredient)

    # Delete parent table

    menu = menuItem.query.filter_by(id=num).first()
    db.session.delete(menu)

    db.session.commit()

    return redirect(url_for('dashboard', message="Deletion of Ingredient Succesfull!"))


@app.route('/deleteIngredient/<string:name>', methods=['GET', 'POST'])
def deleteIngredient(name):

    _ingredient = Ingredient.query.filter_by(name=name).first()

    deleted_related_menus = request.args.get('deleteRelatedMenus')
    print("deleted_related_menus:", deleted_related_menus)

    if _ingredient:

        if deleted_related_menus == 'true':

            # Check if ingredient is associated with a menu item and delete them
            _menuItemIngredient = menuItemIngredient.query.filter_by(
                ingredient_id=_ingredient.id).all()

            if _menuItemIngredient:

                for item in _menuItemIngredient:
                    _menuItem = menuItem.query.filter_by(
                        id=item.menu_item_id).first()
                    _image = Image.query.filter_by(
                        menu_item_id=item.menu_item_id).first()

                    db.session.delete(item)
                 # Check if _menuItem is not None before deleting it
                    if _menuItem and _image:
                        db.session.delete(_menuItem)
                        db.session.delete(_image)

            # Delete the ingredient
            db.session.delete(_ingredient)
            db.session.commit()
            message = "Ingredient deleted successfully"

        elif deleted_related_menus == 'false':
            message = "Delete the menu items associated first before deleting the ingredient or you can the checkbox to do this automatically"
    else:
        message = "Ingredient not found"

    return redirect(url_for("inventory", message=message))


@login_required
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

        button_value = request.form.get('submit-button')
        quantity = []
        weight = []
        ingredients_name = []

        # Due to the deleted fields are still being passed in the POST request get only the first form field
        if button_value == 'pushed':

            for key, value in request.form.items():

                if len(ingredients_name) == 1 and len(weight) == 1 and len(quantity) == 1:
                    ic(f"{ingredients_name}, {quantity}, {weight}")
                    break

                if key.startswith('ingredients-field-') or key == 'ingredients':
                    ingredients_name.append(value)
                elif key.startswith('quantity-field-') or key == 'quantity':
                    quantity.append(value)

                elif key.startswith('weight-field-') or key == 'weight':
                    weight.append(value)

            recipe = request.form.get('recipe')
            desc = request.form.get('desc')
            ic(quantity)

            cost = updateQuery(ingredients_name, quantity,
                               weight, recipe, desc, num, button_value)

        else:

            # Get the key-pair value for the Ingredients field but only the value for other fieds
            for key, value in request.form.items():
                if key.startswith('ingredients-field-') or key == 'ingredients':
                    ingredients_name.append(value)
                elif key.startswith('quantity-field-') or key == 'quantity':
                    quantity.append(value)
                elif key.startswith('weight-field-') or key == 'weight':
                    weight.append(value)

            recipe = request.form.get('recipe')
            desc = request.form.get('desc')
            ic(quantity)
            cost = updateQuery(ingredients_name, quantity,
                               weight, recipe, desc, num, button_value)
        if cost == 'Success':

            return redirect(url_for('dashboard', message="Form submitted succesfully"))
        else:
            return redirect(url_for('quantityError', error=cost, num=num))
    elif request.method == 'POST' and form.validate_on_submit() == False:

        first_box = []
        for key, value in request.form.items():
            if key.startswith('quantity-field-') or key == 'quantity':
                first_box.append(value)

        error_messages = check_Quantity(first_box)
        if error_messages is not None:
            ic(error_messages)
            # redirect to error page if any errors occurred
            return redirect(url_for('quantityError', error=error_messages, num=num))

    return render_template('editRecipe.html', form=form, list_length=len(get_ingredients), num=num)


@app.route("/editIngredient/<string:name>", methods=['POST', 'GET'])
@login_required
def editIngredient(name):

    form = IngredientForm()

    # Query the Ingredient
    ingredient = Ingredient.query.filter_by(name=name).first()

    form.name.data = ingredient.name
    form.stock.data = ingredient.quantity
    form.price.data = ingredient.cost

    # Query the weight name using the ID
    weight = Weight.query.filter_by(id=ingredient.id).first()
    form.weight.data = weight.name

    # Query the to be edited
    if request.method == 'POST' and form.validate_on_submit():

        has_error = False
        try:

            stock = float(request.form.get('stock'))
            price = float(request.form.get('price'))
            if stock <= 0 or price <= 0:
                has_error = True
                raise ValueError
            else:
                has_error = False
        except (TypeError, ValueError):
            ic("error")
            error = "Stock and Quantity fields should only contains numbers and must not be less than zero"
            return render_template("editIngredient.html", form=form, name=name, error=error)

        if has_error is False:

            _ingredient = Ingredient.query.filter_by(name=name).first()

            _ingredient.name = request.form.get('name')
            _ingredient.quantity = request.form.get('stock')
            _ingredient.cost = request.form.get('price')

            _weight = Weight.query.filter_by(id=_ingredient.id).first()
            _ingredient.weight_id = _weight.id
            db.session.commit()

            message = 'Form submitted successfully.'
            flash(message)

            return redirect(url_for('inventory', message="Succesfully saved changes!!"))
    elif request.method == 'POST' and form.validate_on_submit() == False:
        has_error = False
        try:
            stock = float(request.form.get('stock'))
            price = float(request.form.get('price'))
            if stock <= 0 or price <= 0:
                has_error = True
                raise ValueError
            else:
                has_error = False
        except (TypeError, ValueError):
            ic("error")
            error = "Stock and Quantity fields should only contains numbers and must not be less than zero"
            return render_template("editIngredient.html", form=form, name=name, error=error)

    return render_template("editIngredient.html", form=form, name=name, error="")


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


# Create Ingredient Form
@app.route('/create-ingredient', methods=['GET', 'POST'])
def addIngredients():

    # TODO: When Ingredient is deleted, delete all items also in ingredientExpiration table
    # TODO: After done above, fix re-stocking same as above add required data ingredientExpiration
    form = IngredientForm()

    if form.validate_on_submit():

        name = request.form.get('name')
        stock = request.form.get('stock')
        price = request.form.get('price')
        weight = request.form.get('weight')
        date_added = datetime.strptime(
            request.form.get('date_added'), '%Y-%m-%d')
        expiration_date = datetime.strptime(
            request.form.get('expiration_date'), '%Y-%m-%d')

        # Check if ingredient name already exists
        ingredient_is_exists = Ingredient.query.filter_by(name=name).first()
        try:
            if price.isalpha() or stock.isalpha() or float(price) <= 0 or float(stock) <= 0:
                error = "Price and Quantity should be numbers only and should not be less than or equals to zero!"
                return redirect(url_for('addIngredients', error=error))
            elif ingredient_is_exists:
                error = "Ingredient (name) already exists, please try again."
                return redirect(url_for('addIngredients', error=error))
            elif date_added > expiration_date:
                error = "Date expiration cannot be earlier than date added or should not be empty"
                return redirect(url_for('addIngredients', error=error))
            else:
                weight_id = Weight.query.filter_by(name=weight).first()

                # create a instance first of Ingredient since the date_expiration_id value does not exist yet.
                new_ingredient = Ingredient(name=name, quantity=stock,
                                            cost=price, weight_id=weight_id.id)
                db.session.add(new_ingredient)
                db.session.commit()

                # Insert the expiration date to the table to create an id for the Ingredient table
                new_date_expiration = ingredientDateExpiration(
                    ingredient_id=new_ingredient.id, quantity_added=stock, date_added=date_added, date_expiration=expiration_date)

                # Commit the changes
                db.session.add(new_date_expiration)
                db.session.commit()

        except ValueError:
            error = "Price and Quantity should be numbers only and should not be less than or equals to zero!"
            return redirect(url_for('addIngredients', error=error))

        return redirect(url_for('inventory'))

    elif form.validate_on_submit() == False and request.method == 'POST':
        stock = request.form.get('stock')
        price = request.form.get('price')
        date_added = datetime.strptime(
            request.form.get('date_added'), '%Y-%m-%d')
        expiration_date = datetime.strptime(
            request.form.get('expiration_date'), '%Y-%m-%d')

        if price.isalpha() or stock.isalpha() or float(price) <= 0 or float(stock) <= 0:
            error = "Price and Quantity should be numbers only and should not be less than or equals to zero!"
            return redirect(url_for('addIngredients', error=error))

    error_msg = request.args.get('error')
    return render_template("ingredientForm.html", form=form, error=error_msg)


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
    weight_list2 = []
    for i in get_ingredients:

        weight_cat = Weight.query.filter_by(id=i.weight_id).first()
        weight_list.append(weight_cat.name)

    message = request.args.get('message')

    # TODO: For deleteIngredients
    is_associated = request.args.get('is_associated')

    like_search_term = request.args.get('like_search_term')
    is_query = request.args.get('is_query')

    # For the ingredient being specifically queried
    get_matching_ingredients = Ingredient.query.filter(
        Ingredient.name.like(f"{like_search_term}%")).all()

    if get_matching_ingredients:
        for i in get_matching_ingredients:
            weight_ids = Weight.query.filter_by(id=i.weight_id).first()
            weight_list2.append(weight_ids.name)
        return render_template('ingredient.html', ingre=get_matching_ingredients, zip=zip, message=message, weight_list=weight_list2)
    elif not get_matching_ingredients and is_query == '1':
        ic("Is query")
        message = "It looks like that Ingredient does not exists please try again"
        return render_template('ingredient.html', ingre=get_ingredients, zip=zip, weight_list=weight_list, message=message)
    else:
        return render_template('ingredient.html', ingre=get_ingredients, zip=zip, weight_list=weight_list, message=message)


@app.route('/searchIngredient', methods=['POST', 'GET'])
def searchIngredient():

    nice = request.form.get('search_term')

    for char in nice:
        if not char.isalnum():
            error = "Only letters and numbers are allowed, please try again"
            return redirect(url_for('inventory', message=error))

    return redirect(url_for('inventory', like_search_term=nice, is_query=1))


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


@app.route('/buyIngredients', methods=['GET', 'POST'])
def buyIngredients():

    data1 = request.args.get('data1').split(',')
    data2 = request.args.get('data2').split(',')
    data3 = request.args.get('data3').split(',')
    data4 = request.args.get('data4')
    data5 = request.args.get('data5')

    date = datetime.datetime.now()

    return render_template('missingIngredients.html', zip=zip, missing_ingre=data1, missing_qty=data2, missing_weight=data3, is_missing=data4, date=date, cost=data5)


@app.route('/recipes/', methods=['GET', 'POST'])
@login_required
# @check_user # TODO: check_user
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
