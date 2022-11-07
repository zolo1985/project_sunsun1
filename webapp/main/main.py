from flask import (Blueprint, render_template)

main_blueprint = Blueprint('main', __name__,)

@main_blueprint.route('/')
def home():
    return render_template('/main/home.html')