from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from icecream import ic
import hashlib
from forms import LoginForm, RegistrationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///login.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=False, nullable=False)
    password = db.Column(db.String(450), unique=False, nullable=False)


db.create_all()


def hash_sha256(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()


@app.route("/", methods=['GET', 'POST'])
def index():

    form = LoginForm()

    if request.method == "POST":

        username = request.form.get_or_404("username")
        password = request.form.get_or_404("password")

        hashed = hash_sha256(password)

        is_user_exists = User.query.filter_by(
            username=username, password=hashed).first()
        ic(is_user_exists)
        if is_user_exists:
            login_user(is_user_exists, remember=True)
            return redirect(url_for("secret"))

        else:

            return render_template("index.html", form=form, error="There seems to be an error.")

    return render_template("index.html", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():

    form = RegistrationForm()

    if request.method == "POST":

        username = request.form.get("register_user")
        password = request.form.get("register_pass")
        confirm = request.form.get("confirm_pass")

        if password == confirm:

            # Hash the password : -
            hashed = hash_sha256(password)
            new_user = User(username=username, password=hashed)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))

        else:
            error = "There seems to be an error, please try again."
            return render_template("register.html", form=form, error=error)

    return render_template("register.html", form=form)


@app.route("/secret", methods=['GET', 'POST'])
@login_required
def secret():
    print(current_user.username)
    return "Wow you got in"


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True)
