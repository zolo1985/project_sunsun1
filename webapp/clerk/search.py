from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp import models
from webapp.clerk.forms import SearchForm
from datetime import datetime
import pytz

clerk_search_blueprint = Blueprint('clerk_search', __name__)

@clerk_search_blueprint.route('/clerk/search', methods=["GET","POST"])
@login_required
@has_role('clerk')
def search():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = SearchForm()
    orders = []
    if form.validate_on_submit():
        connection = Connection()
        orders = connection.query(models.Delivery).filter(models.Delivery.addresses.has(models.Address.phone.like('%' + form.search_text.data + '%'))).all()
        return render_template('/clerk/results.html', orders=orders, form=form, cur_date=cur_date)
    return render_template('/clerk/results.html', orders=orders, form=form, cur_date=cur_date)