from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import SearchForm
from datetime import datetime, timedelta
from sqlalchemy import func
import pytz

manager_search_blueprint = Blueprint('manager_search', __name__)

@manager_search_blueprint.route('/manager/search', methods=["GET","POST"])
@login_required
@has_role('manager')
def search():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = SearchForm()
    orders = []
    if form.validate_on_submit():
        connection = Connection()
        orders = connection.query(models.Delivery).filter(models.Delivery.addresses.has(models.Address.phone.like('%' + form.search_text.data + '%')))
        return render_template('/manager/results.html', orders=orders, form=form, cur_date=cur_date)
    return render_template('/manager/results.html', orders=orders, form=form, cur_date=cur_date)