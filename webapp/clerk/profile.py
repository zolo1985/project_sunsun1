from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required

clerk_profile_blueprint = Blueprint('clerk_profile', __name__)

@clerk_profile_blueprint.route('/clerk/profile')
@login_required
@has_role('clerk')
def profile():
    return render_template('/shared/profile.html')