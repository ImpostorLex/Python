from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from icecream import ic
from flask_hashing import Hashing
from form import LoginForm, RegistrationForm
from time import sleep
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dimsumz2go.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key'
login_manager = LoginManager()
login_manager.init_app(app)
hashing = Hashing(app)
db = SQLAlchemy(app)
user_type = 0


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    employee_id = (db.Integer, db.ForeignKey('employee.id'))
    # username is the primary key constraint and of course id is the primary key
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(450), unique=False, nullable=False)


class Employees(UserMixin, db.Model):

    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(250), unique=False, nullable=False)
    lastName = db.Column(db.String(250), unique=False, nullable=False)


db.create_all()


def check_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_url = request.path  # /graphs

        id_and_url = (user_type, current_url)

        categories = [(1, "/recipes"), (2, "/graphs"), (2, '/inventory'), (3, '/recipes'),
                      (3, '/inventory'), (4, '/recipes'), (4, 'graphs'), (5, 'inventory')]

        if id_and_url in categories:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('unauthorized'))
    return wrapper


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


@app.route('/register', methods=['POST', 'GET'])
def register():

    form = RegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():

        username = request.form.get('username')
        password = request.form.get('password')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
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

                # Get the id of the inserted employee
                employee_id = employee.id
                ic(employee_id)

                # Insert a row into the Users table with the employee_id as the foreign key
                user = Users(username=username, password=h,
                             employee_id=employee_id)
                db.session.add(user)
                db.session.commit()

                return redirect(url_for('index'))

    return render_template("register.html", form=form)


@app.route("/dashboard", methods=['GET', 'POSTS'])
@login_required
def dashboard():
    global user_type

    user_type = 1

    return render_template("dashboard.html", user=user_type)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()

    return redirect(url_for('index'))


@app.route("/unauthorized", methods=['GET', 'POST'])
def unauthorized():

    return "<h1>Unauthorized, you don't have enough permission to access this page.</h1>"


@app.route('/graphs', methods=['GET', 'POST'])
@check_user
def graphs():

    return "For Accountant"


@app.route('/inventory', methods=['GET', 'POST'])
@login_required
@check_user
def inventory():

    return "For Accountant/Chef"


@app.route('/recipes', methods=['GET', 'POST'])
@login_required
@check_user
def recipes():

    return render_template("recipes.html")


@ app.route('/home', methods=['GET', 'POST'])
def home():

    return "<h1>Simple static website for users</h1>"


@ login_manager.user_loader
def load_user(user_id):

    return Users.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True)
