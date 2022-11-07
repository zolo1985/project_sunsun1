from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required

supplier2_profile_blueprint = Blueprint('supplier2_profile', __name__)

@supplier2_profile_blueprint.route('/supplier2/profile')
@login_required
@has_role('supplier2')
def profile():
    return render_template('/shared/profile.html')