from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from icecream import ic
from flask_hashing import Hashing
from form import LoginForm, RegistrationForm, CreateForm, IngredientForm, editIngredientForm
from time import sleep
from functools import wraps
from sqlalchemy import Date, extract, func
from datetime import datetime, timedelta
from itertools import zip_longest
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dimsumz2go.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key hehelol'
IMAGE_FOLDER = app.config['UPLOAD_FOLDER'] = os.path.abspath(
    'static/recipesImgs')
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
    profit = db.Column(db.Float(20), nullable=False)


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
    cost = db.Column(db.Float, nullable=False)


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


class IngredientCost(db.Model):
    __tablename__ = 'IngredientCost'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey(
        'ingredient.id'), nullable=False)
    date_added = db.Column(db.Date, nullable=False,
                           default=datetime.utcnow().date())
    cost = db.Column(db.Float, nullable=False)


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
    allowed_filetype = ['jpg', 'png', 'jpeg']
    if img.data and '.' in img.data.filename and img.data.filename.rsplit('.', 1)[1] in allowed_filetype:
        folder_path = os.path.join(app.static_folder, 'recipesImgs')
        os.makedirs(folder_path, exist_ok=True)
        filename = secure_filename(img.data.filename)
        filename_without_prefix = filename.split('/')[-1]
        filepath = os.path.join(folder_path, filename_without_prefix)
        img.data.save(filepath)

        ic("Is Image")
        # return only the filename
        return filename_without_prefix
    else:
        ic("Error")
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


def updateQuery(ingredients, quantity, weight, recipe, desc, num, isPushed, url, instruc, profit):

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
        menu.profit = profit

        # Second Query the Image table
        image = Image.query.filter_by(menu_item_id=num).first()
        image_path = os.path.join('recipesImgs', url)
        db.session.add(image)
        image.path = image_path
        image.instructions = instruc

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


@app.template_filter('format_instructions')
def format_instructions(instructions):
    steps = instructions.split('\n')
    formatted_steps = []
    for step in steps:
        if step.strip():
            step_parts = step.strip().split(':')
            if len(step_parts) >= 2:
                step_number = step_parts[0].strip()
                step_description = ':'.join(step_parts[1:]).strip()
                formatted_steps.append('{}) {}'.format(
                    step_number, step_description))
    return '<br>'.join(formatted_steps)
# Sample output:
 # Outputs; ic| req_ingredient_list: [('Lemon', 4, 'oz')]
   #  dup_req_ingredient_list: [('Patty', 1, 'kg'), ('Patty', 2, 'lb')]


def check_ingredient_availability(unique, duplicates, order):

    satisfied = []
    not_satisfied = []

    unique_grams = []

    # Calculate the unique first
    for x in range(len(unique)):

        ingredient = Ingredient.query.filter_by(name=unique[x][0]).first()
        weight_type = Weight.query.filter_by(id=ingredient.weight_id).first()

        ingredient_to_grams = ingredient.quantity * unit_map[weight_type.name]
        required_ingredient_to_grams = (
            unique[x][1] * unit_map[unique[x][2]]) * order

        if ingredient_to_grams < required_ingredient_to_grams:

            not_satisfied_name = unique[x][0]
            not_satisfied_quantity = ingredient_to_grams - required_ingredient_to_grams
            not_satisfied_quantity_to_orig_weight = round(not_satisfied_quantity /
                                                          unit_map[weight_type.name], 2)
            not_satisfied_weight = unique[x][2]
            not_satisfied.append(
                (not_satisfied_name, not_satisfied_quantity_to_orig_weight, not_satisfied_weight))
        else:
            satisfied_name = unique[x][0]
            satisfied_quantity = ingredient_to_grams - required_ingredient_to_grams

            # Convert gram to original weight
            satisfied_quan_to_orig_weight = round(satisfied_quantity /
                                                  unit_map[weight_type.name], 2)
            satisfied_weight = unique[x][2]
            unique_grams.append(
                (unique[x][0], required_ingredient_to_grams, weight_type.name))
            satisfied.append(
                (satisfied_name, satisfied_quan_to_orig_weight, satisfied_weight))

    # Group items by name and calculate total quantity in grams
    unique_items = {}
    for item in duplicates:
        name, quantity, weight = item
        if name not in unique_items:
            # Nested dictionary
            unique_items[name] = {'quantity': 0, 'weight': weight}
        conversion_factor = unit_map[weight]
        unique_items[name]['quantity'] += quantity * conversion_factor

    # Calculate the required ingredients of the duplicates
    for name, data in unique_items.items():

        ingredient = Ingredient.query.filter_by(name=name).first()
        weight_type = Weight.query.filter_by(id=ingredient.weight_id).first()

        dup_onhand_ingredient_to_grams = ingredient.quantity * \
            unit_map[weight_type.name]

        dup_required_ingredients_to_grams = data['quantity'] * order

        if dup_required_ingredients_to_grams > dup_onhand_ingredient_to_grams:

            not_satisfied_dup_name = name
            not_satisfied_dup_quantity = dup_onhand_ingredient_to_grams - \
                dup_required_ingredients_to_grams
            not_satisfied_dup_quan_to_orig_weight = round(not_satisfied_dup_quantity /
                                                          unit_map[weight_type.name], 2)
            not_satisfied_dup_weight = data['weight']
            not_satisfied.append(
                (not_satisfied_dup_name, not_satisfied_dup_quan_to_orig_weight, not_satisfied_dup_weight))
        else:
            satisfied_dup_name = name
            satisfied_dup_quantity = dup_onhand_ingredient_to_grams - \
                dup_required_ingredients_to_grams
            satisfied_dup_quan_to_orig_weight = round(satisfied_dup_quantity /
                                                      unit_map[weight_type.name], 2)
            satisfied_dup_weight = data['weight']
            satisfied.append((satisfied_dup_name,
                             satisfied_dup_quan_to_orig_weight, satisfied_dup_weight))

    return not_satisfied, satisfied, unique_items, unique_grams

    # OUTPUTS:
    # Patty: 56.7 g(oz)
    # Cheese: 454.59 g(g)


def compute_ingredient_quantity(unique, duplicates, orders):

    now = datetime.now()
    todays_date = now.strftime('%Y-%m-%d')

    quantity = 0
    # Calculate the non - duplicates first
    for ingredient, quantity, weight in unique:
        ic(quantity)
        # Query the Ingredient
        ingredient_obj = Ingredient.query.filter_by(
            name=ingredient).first()
        weight_type = Weight.query.filter_by(
            id=ingredient_obj.weight_id).first()

        # Convert on-hand quantity to grams
        ingredient_obj_grams = ingredient_obj.quantity * \
            unit_map[weight_type.name]

        # Since it is already validated substract it and quantity for unique list is already to grams
        new_value = (ingredient_obj_grams - quantity) / \
            unit_map[weight_type.name]

        # Update the Ingredient Quantity row with the new value
        ingredient_obj.quantity = round(new_value, 2)

        # Use the quantity to substract the required amount in the IngredientExpirationDate
        rows = ingredientDateExpiration.query.filter_by(
            ingredient_id=ingredient_obj.id).filter(
            ingredientDateExpiration.date_expiration >= todays_date).all()

        quantity_remaining = quantity

        for row in rows:
            ic(row.quantity_added)
            if row.ingredient_id == ingredient_obj.id:

                # Convert the on stock to grams first
                row_to_grams = row.quantity_added * unit_map[weight_type.name]

                quantity_remaining -= row_to_grams

                # Delete the row if it has been fully consumed
                if quantity_remaining > 0:
                    db.session.delete(row)

                # if quantity_remaining is zero it means that one row is more than enough
                # say -1 so the new value of this row is 1 (because it is more than enough)
                elif quantity_remaining < 0:

                    num = (abs(quantity_remaining)) / \
                        unit_map[weight_type.name]

                    row.quantity_added = num

    # Calculate the duplicate now
    for key, value in duplicates.items():

        # Query the Ingredient
        ingredient_obj = Ingredient.query.filter_by(
            name=key).first()
        weight_type = Weight.query.filter_by(
            id=ingredient_obj.weight_id).first()

        # Convert on-hand quantity to grams
        ingredient_obj_grams = ingredient_obj.quantity * \
            unit_map[weight_type.name]

        # Since it is already validated substract it and quantity for unique list is already to grams
        new_value = (ingredient_obj_grams - quantity) / \
            unit_map[weight_type.name]

        # Update the Ingredient Quantity row with the new value
        ingredient_obj.quantity = round(new_value, 2)

        # Use the quantity to substract the required amount in the IngredientExpirationDate
        rows = ingredientDateExpiration.query.filter_by(
            ingredient_id=ingredient_obj.id).filter(
            ingredientDateExpiration.date_expiration >= todays_date).all()

        quantity_remaining = quantity

        for row in rows:
            ic(row.quantity_added)
            if row.ingredient_id == ingredient_obj.id:

                # Convert the on stock to grams first
                row_to_grams = row.quantity_added * unit_map[weight_type.name]

                quantity_remaining -= row_to_grams

                # Delete the row if it has been fully consumed
                if quantity_remaining > 0:
                    db.session.delete(row)

                # if quantity_remaining is zero it means that one row is more than enough
                # say -1 so the new value of this row is 1 (because it is more than enough)
                elif quantity_remaining < 0:

                    # Convert back to original weight type
                    num = (abs(quantity_remaining)) / \
                        unit_map[weight_type.name]
                    row.quantity_added = num

    db.session.commit()


@app.route('/buyMenu/<string:name>')
def buyMenu(name):

    orders = int(request.args.get('quantity'))

    # Get menuItem ID to find all required ingredients in menu_item_ingredients
    _menuItem = menuItem.query.filter_by(name=name).first()

    total_ingredient_cost = _menuItem.profit * orders
    # Retrieve all associated menu_item_ingredients rows with menuItem
    _menuItemIngredient = menuItemIngredient.query.filter_by(
        menu_item_id=_menuItem.id).all()

    # Count total cost
    total_cost = float(_menuItem.profit) * orders

    # Add it to the sales table
    total_profit = float(_menuItem.profit) * orders

    now = datetime.now()
    todays_date = now.strftime('%Y-%m-%d')

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

    not_satisfied, satisfied, dup_into_one, unique_grams = check_ingredient_availability(
        req_ingredient_list, dup_req_ingredient_list, orders)

    # f"{unique_grams}": "[('Cheese', 907.18, 'lb')]" 907.18 is grams REMEMBER! I just passed in the orig weight
    # ic | f"{dup_into_one}": "{'Patty': {'quantity': 56.7, 'weight': 'oz'}}"
    date = datetime.now()
    if not_satisfied:

        return render_template('missingIngredients.html', cost=total_cost, is_missing="missing", missing_list=not_satisfied, date=date)

    elif not not_satisfied:

        x = compute_ingredient_quantity(unique_grams, dup_into_one, orders)

        sale = Sale(menu_item_id=_menuItem.id, date_added=datetime.strptime(todays_date, '%Y-%m-%d'),
                    profit=total_profit, cost=total_cost)
        db.session.add(sale)
        db.session.commit()

        return render_template('missingIngredients.html', cost=total_cost, is_missing="false", missing_list=satisfied, date=date)

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
            profit = request.form.get('price')

            try:
                float(profit)
                if float(profit) <= 0:
                    raise ValueError
            except ValueError:
                return redirect(url_for('create', error="Profit cannot contain any letters and should not be less than or equal to zero"))
            # Insert url and instruction and as well as the menu_id as the foreign key to the image table
            url2 = form.url

            is_valid_filetype = isImage(url2)

            if is_valid_filetype == "Error":
                return redirect(url_for('create', error="File type is invalid only images."))
            else:
                cost = sum(cost)
                menu_item = menuItem(name=recipe, desc=desc,
                                     cost=cost, profit=profit)
                db.session.add(menu_item)
                db.session.commit()

                # Get the id of the inserted menu
                menu_id = menu_item.id
                ic("No Error?")
                instructions = request.form.get('instructions')
                image_path = os.path.join('recipesImgs', is_valid_filetype)
                image = Image(menu_item_id=menu_id, path=image_path,
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

    # Check if there is a expired ingredient today and removed it from both Ingredient table and Ingredient Date expiration table
    now = datetime.now()
    todays_date = now.strftime('%Y-%m-%d')

    expired_ingredients = ingredientDateExpiration.query.filter_by(
        date_expiration=todays_date).all()

    if expired_ingredients:
        for ingredient_expired in expired_ingredients:

            # Use the row in the expired ingredients to reduce the total quantity of the quantity in Ingredients table

            ingredient = Ingredient.query.filter_by(
                id=ingredient_expired.ingredient_id).first()
            num_to_reduce = float(ingredient_expired.quantity_added)

            subtracted = ingredient.quantity - num_to_reduce

            if subtracted < 0:
                ingredient.quantity = 0
            else:
                ingredient.quantity = subtracted

            # Delete the matching row
            db.session.delete(ingredient_expired)
            db.session.commit()

            message = "There are expired ingredients and has been removed from the stock."

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

            # Delete all rows associated with the to be deleted Ingredient
            associated_rows_date_expiration = ingredientDateExpiration.query.filter_by(
                ingredient_id=_ingredient.id).all()

            for row in associated_rows_date_expiration:
                db.session.delete(row)

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

        profit = request.form.get('price')

        try:
            float(profit)
            if float(profit) <= 0:
                raise ValueError
        except ValueError:
            return redirect(url_for('edit', num=num, error_file="Only numbers and should not be less than zero"))

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

            upload = form.url

            url = isImage(upload)
            instruc = request.form.get('instructions')

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

            upload = form.url

            url = isImage(upload)

            instruc = request.form.get('instructions')

        if url == 'Error':
            error_messages = "Invalid filetype please upload images only, (jpg, jpeg, png)"
            return redirect(url_for('edit', num=num, error_file=error_messages))

        else:
            cost = updateQuery(ingredients_name, quantity,
                               weight, recipe, desc, num, button_value, url, instruc, profit)
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

    error_msg = request.args.get('error_file')
    return render_template('editRecipe.html', form=form, list_length=len(get_ingredients), num=num, error=error_msg)


@app.route("/editIngredient/<string:name>", methods=['POST', 'GET'])
@login_required
def editIngredient(name):

    # Query the Ingredient
    ingredient = Ingredient.query.filter_by(name=name).first()

    form = editIngredientForm(current_stock=ingredient.quantity)

    form.name.data = ingredient.name
    form.price.data = ingredient.cost

    # Remember the old quantity
    old_quantity_val = ingredient.quantity

    # Query the weight name using the ID
    weight = Weight.query.filter_by(id=ingredient.weight_id).first()
    form.weight.data = weight.name

    if request.method == 'POST' and form.validate_on_submit():

        # Validate the date
        date_added = request.form.get('date_added')
        exp_date = request.form.get('expiration_date')

        if date_added > exp_date:
            error = "Date added cannot be later than expiration date, please try again"
            return render_template("editIngredient.html", form=form, name=name, error=error)

        # Check if user is re-stocking if quantity field is greater than zero
        if float(request.form.get('stock')) > 0:

            _ingredient = Ingredient.query.filter_by(name=name).first()

            # Add the quantity and the expiration date to the ingredient_date_expiration table
            date_added_str = request.form.get('date_added')
            date_expiration_str = request.form.get('expiration_date')

            date_added = datetime.strptime(date_added_str, '%Y-%m-%d').date()
            date_expiration = datetime.strptime(
                date_expiration_str, '%Y-%m-%d').date()

            stock = float(request.form.get('stock'))
            ingredient_date = ingredientDateExpiration(
                ingredient_id=_ingredient.id, quantity_added=stock, date_added=date_added, date_expiration=date_expiration)

            _ingredient.name = request.form.get('name')

            _ingredient.quantity = old_quantity_val + \
                stock
            _ingredient.cost = request.form.get('price')

            weight_type = request.form.get('weight')
            _weight = Weight.query.filter_by(name=weight_type).first()
            _ingredient.weight_id = _weight.id
            db.session.add(ingredient_date)
            db.session.commit()

            ingredient_spent = float(request.form.get(
                'stock')) * float(request.form.get('price'))

            # Insert the newly added stock to the IngredientCost
            ingredient_cost = IngredientCost(
                ingredient_id=_ingredient.id, date_added=date_added, cost=ingredient_spent)
            db.session.add(ingredient_cost)
            db.session.commit()

            return redirect(url_for('inventory', message="Succesfully saved changes!!"))

        # This means that the user is just changing the other fields
        elif float(request.form.get('stock')) == 0:

            _ingredient = Ingredient.query.filter_by(name=name).first()
            _ingredient.name = request.form.get('name')
            _ingredient.cost = request.form.get('price')
            weight_type = request.form.get('weight')
            _weight = Weight.query.filter_by(name=weight_type).first()
            _ingredient.weight_id = _weight.id
            db.session.commit()

            return redirect(url_for('inventory', message="Succesfully saved changes!!"))
        else:
            error = "An error has occured, please double check your input."
            return render_template("editIngredient.html", form=form, name=name, error=error)

    elif request.method == 'POST':

        try:
            # This checks if the price can be converted to float if it is letter it will throw an error.
            price = float(request.form.get('price'))

            if price <= 0:
                raise ValueError
        except ValueError:
            message = "Invalid input for price. Please enter a valid number and should not be less than zero"
            return render_template("editIngredient.html", form=form, name=name, error=message)

        try:
            stock = float(request.form.get('stock'))
        except ValueError:
            message = "Invalid input for quantity field it must not contain any characters!"
            return render_template("editIngredient.html", form=form, name=name, error=message)

        # If the date remains empty, it means the user is only updating the othe fields.
        # Validate the date
        date_added = request.form.get('date_added')
        exp_date = request.form.get('expiration_date')
        ic(date_added)

        if not date_added or not exp_date:

            _ingredient = Ingredient.query.filter_by(name=name).first()
            _ingredient.name = request.form.get('name')
            _ingredient.cost = request.form.get('price')
            weight_type = request.form.get('weight')
            _weight = Weight.query.filter_by(name=weight_type).first()
            _ingredient.weight_id = _weight.id
            db.session.commit()

            return redirect(url_for('inventory', message="Succesfully saved changes!!"))

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
                error = f"Ingredient ({name}) already exists, please try again."
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

                new_ingredient_id = new_ingredient.id

                # For the analytics

                cost_per_unit = float(price) * float(stock)

                cost_of_stock = IngredientCost(
                    ingredient_id=new_ingredient_id, date_added=date_added, cost=cost_per_unit)
                db.session.add(cost_of_stock)
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

    # Top three ingredients that is low on stocks
    ingredients = Ingredient.query.order_by(
        Ingredient.quantity.asc()).limit(3).all()

    ingredient_low_data = []
    ingredient_low_labels = []

    if ingredients:
        for ingr in ingredients:

            ingredient_low_labels.append(ingr.name)
            ingredient_low_data.append(ingr.quantity)

    # Top three most bought menu item current month
    current_month = datetime.now().month

    # Query the most bought menu item in the current month
    top_three_menu_items = db.session.query(Sale.menu_item_id, func.count().label('row_count')) \
        .filter(extract('month', Sale.date_added) == current_month) \
        .group_by(Sale.menu_item_id) \
        .order_by(func.count().desc()) \
        .limit(3) \
        .all()

    top_three_menu = []
    top_three_labels = []

    ic(top_three_menu_items)
    if top_three_menu_items:

        for top in top_three_menu_items:
            menu_item_id = top.menu_item_id

            # Query the menu name
            # Query the Menu item first to check if the menu exists:
            menu_item_name = menuItem.query.filter_by(id=menu_item_id).first()
            if menu_item_name:
                top_three_labels.append(menu_item_name.name)

                row_count = top.row_count
                top_three_menu.append(row_count or 0)
            else:
                break

    # Get total users
    total_users = Users.query.count() or 0

    # Get total ingredients
    total_ingredient = Ingredient.query.count() or 0

    # Get total menu
    total_menu_items = menuItem.query.count() or 0

# ----------------------------- Weekly sales -----------------------------
    current_date = datetime.today()

    # Get the first day of the current month
    first_day_of_month = current_date.replace(day=1)

    # Get the current week number
    current_week_number = (current_date - first_day_of_month).days // 7 + 1

    # Calculate the start date of the current week
    start_date_of_week = first_day_of_month + \
        timedelta(days=(current_week_number - 1) * 7)

    # Create a dictionary to store weekly sales totals
    weekly_sales_total = {}

    sales_data = Sale.query.all()
    # Replace `sales_data` with the variable or query that fetches the sales data
    if sales_data:
        for sale in sales_data:
            sale_date = sale.date_added
            sale_week_number = (sale_date -
                                start_date_of_week.date()).days // 7 + 1

            # Add the sale to the corresponding week
            if sale_week_number not in weekly_sales_total:
                weekly_sales_total[sale_week_number] = 0.0
            weekly_sales_total[sale_week_number] += sale.profit

    # ic(weekly_sales_total) outputs :  weekly_sales_total: {1: 99.0}


# -----------------------------  Monthy Sales -----------------------------
    current_year = datetime.today().year
    current_date = datetime.today()
    current_month = "2023-07-1"
    # Query sales data per month

    sales_per_month = db.session.query(
        func.extract('month', Sale.date_added).label('month'),
        func.sum(Sale.profit).label('total_profit')
    ).filter(
        func.extract('year', Sale.date_added) == current_year,
        func.extract('month', Sale.date_added) <= current_month
    ).group_by(
        func.extract('month', Sale.date_added)
    ).all()

    # Query costs data per month
    costs_per_month = db.session.query(
        func.extract('month', IngredientCost.date_added).label('month'),
        func.sum(IngredientCost.cost).label('total_cost')
    ).filter(
        func.extract('year', IngredientCost.date_added) == current_year,
        func.extract('month', IngredientCost.date_added) <= current_month
    ).group_by(
        func.extract('month', IngredientCost.date_added)
    ).all()

    sales_per_month = [{'month': row[0], 'sum': row[1]}
                       for row in sales_per_month]
    costs_per_month = [{'month': row[0], 'sum': row[1]}
                       for row in costs_per_month]

# ----------------------------- ^ Monthly sales ^ -----------------------------

    return render_template('graph.html', costs_per_month=costs_per_month, sales_per_month=sales_per_month, weekly_sales_total=weekly_sales_total, total_menu_items=total_menu_items, total_users=total_users,  total_ingredient=total_ingredient, top_menu_data=top_three_menu, top_menu_labels=top_three_labels, top_three_label=ingredient_low_labels, top_three_data=ingredient_low_data)


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
    rounded_quantity = []

    for i in get_ingredients:

        weight_cat = Weight.query.filter_by(id=i.weight_id).first()
        weight_list.append(weight_cat.name)

    message = request.args.get('message')

    like_search_term = request.args.get('like_search_term')
    is_query = request.args.get('is_query')

    # For the ingredient being specifically queried
    get_matching_ingredients = Ingredient.query.filter(
        Ingredient.name.like(f"{like_search_term}%")).all()

    if get_matching_ingredients:
        for i in get_matching_ingredients:
            weight_ids = Weight.query.filter_by(id=i.weight_id).first()
            weight_list2.append(weight_ids.name)
        return render_template('ingredient.html', round=round, ingre=get_matching_ingredients, zip=zip, message=message, weight_list=weight_list2)
    elif not get_matching_ingredients and is_query == '1':
        ic("Is query")
        message = "It looks like that Ingredient does not exists please try again"
        return render_template('ingredient.html', round=round, ingre=get_ingredients, zip=zip, weight_list=weight_list, message=message)
    else:
        return render_template('ingredient.html', round=round, ingre=get_ingredients, zip=zip, weight_list=weight_list, message=message)


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


@app.route('/recipes/', methods=['GET', 'POST'])
@login_required
def recipes():

    menus = menuItem.query.all()
    imgs = Image.query.all()

    return render_template("recipes.html", menu=menus, img=imgs, zip=zip, image_path=IMAGE_FOLDER)


@app.route("/unauthorized", methods=['GET', 'POST'])
def unauthorized():

    return render_template("unauthorized.html")


@login_manager.user_loader
def load_user(user_id):

    return Users.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True)
