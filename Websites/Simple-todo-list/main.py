from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import ToDoForm
from icecream import ic

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo-form.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key'
db = SQLAlchemy(app)


class Todo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(250), unique=False, nullable=False)
    description = db.Column(db.String(250), unique=False, nullable=False)
    status = db.Column(db.String(10), default="0", nullable=False)


# Executes creation of tables and rows
db.create_all()


@app.route("/", methods=["GET", "POST"])
def main():

    todo = db.session.query(Todo).all()

    if request.method == "POST":
        new_book = Todo(todo=request.form.get('title'),
                        description=request.form.get('description'))
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('main'))

    return render_template("index.html", todo=todo)


@app.route("/add", methods=["GET", "POST"])
def add():

    form = ToDoForm()
    return render_template("todoform.html", form=form)


@app.route("/delete/<post_id>", methods=['GET', 'DELETE'])
def delete_todo(post_id):

    todo_to_delete = Todo.query.get(post_id)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('main'))


@app.route("/update_todo/<update>/<id>", methods=['GET', 'PUT'])
def update_todo(update, id):

    todo_update = Todo.query.get(id)
    ic(update)

    if todo_update:
        if update == "1":
            todo_update.status = "1"

        elif update == "0":

            todo_update.status = "0"

    db.session.commit()
    return redirect(url_for('main'))


if __name__ == "__main__":
    app.run(debug=True)
