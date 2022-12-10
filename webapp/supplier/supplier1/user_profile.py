from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required

supplier1_profile_blueprint = Blueprint('supplier1_profile', __name__)

@supplier1_profile_blueprint.route('/supplier1/profile')
@login_required
@has_role('supplier1')
def profile():
    return render_template('/shared/profile.html')