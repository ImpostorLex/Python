from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from icecream import ic

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///sales.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key'
db = SQLAlchemy(app)


class Sales(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(250), unique=False, nullable=False)
    profit = db.Column(db.String(450), unique=False, nullable=False)


db.create_all()


@app.route("/")
def home():

    # Sample Data
    data = [
        ("01-01-2020", 1597),
        ("02-01-2020", 1456),
        ("03-01-2020", 1908),
        ("04-01-2020", 896),
        ("05-01-2020", 755),
        ("06-01-2020", 453),
        ("07-01-2020", 1100),
        ("08-01-2020", 1235),
        ("09-01-2020", 1478),
    ]

    labels = []
    values = []

    for row in data:
        labels.append(row[0])
        values.append(row[1])

    return render_template("graph.html", labels=labels, values=values)


@app.route("/sales")
def sales():

    data = Sales.query.all()

    labels = []
    values = []

    for row in data:

        labels.append(row.item)
        values.append(row.profit)

    return render_template("yowie.html", labels=labels, values=values)


if __name__ == "__main__":
    app.run()
