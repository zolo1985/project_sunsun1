from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required

accountant_profile_blueprint = Blueprint('accountant_profile', __name__)

@accountant_profile_blueprint.route('/accountant/profile')
@login_required
@has_role('accountant')
def profile():
    return render_template('/shared/profile.html')