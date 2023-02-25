from flask import Flask, render_template, request, redirect, url_for
from icecream import ic
from flask_wtf import FlaskForm
from wtforms import StringField

app = Flask(__name__)


class LoginForm(FlaskForm):

    username = StringField(label='Username')


@app.route("/", methods=['POST', 'GET'])
def home():

    form = LoginForm

    if request.method == 'POST':

        text_boxes = request.form.getlist('text-box')
        ic(text_boxes)

        if not text_boxes:
            # Handle case where no text boxes were submitted
            return "No text box values submitted"
        else:
            # Process the list of text box values
            return str(text_boxes)

    return render_template("buttons.html", form=form)


if __name__ == "__main__":
    app.run()
