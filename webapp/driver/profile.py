from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required

driver_profile_blueprint = Blueprint('driver_profile', __name__)

@driver_profile_blueprint.route('/driver/profile')
@login_required
@has_role('driver')
def profile():
    return render_template('/shared/profile.html')