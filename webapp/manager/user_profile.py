from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required

manager_profile_blueprint = Blueprint('manager_profile', __name__)

@manager_profile_blueprint.route('/manager/profile')
@login_required
@has_role('manager')
def profile():
    return render_template('/shared/profile.html')