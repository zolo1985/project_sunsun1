from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp import models
from webapp.accountant.forms import SearchForm
from datetime import datetime
import pytz

accountant_search_blueprint = Blueprint('accountant_search', __name__)

@accountant_search_blueprint.route('/accountant/search', methods=["GET","POST"])
@login_required
@has_role('accountant')
def search():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = SearchForm()
    orders = []
    if form.validate_on_submit():
        connection = Connection()
        orders = connection.query(models.Delivery).filter(models.Delivery.addresses.has(models.Address.phone.like('%' + form.search_text.data + '%'))).limit(20)
        return render_template('/accountant/results.html', orders=orders, form=form, cur_date=cur_date)
    return render_template('/accountant/results.html', orders=orders, form=form, cur_date=cur_date)