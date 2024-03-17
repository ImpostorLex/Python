# The init.py file make this importing of bp possible.
from app.main import bp
from flask import render_template


@bp.route('/')
def index():
    return render_template('index.html')
