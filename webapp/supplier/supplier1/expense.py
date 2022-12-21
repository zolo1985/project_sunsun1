from flask import (Blueprint, render_template, request)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from datetime import datetime
from webapp.supplier.supplier1.forms import SelectOption
from sqlalchemy import func
import pytz

supplier1_expense_blueprint = Blueprint('supplier1_expense', __name__)

@supplier1_expense_blueprint.route('/supplier1/expenses', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_expenses():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    connection = Connection()
    orders = connection.query(models.Delivery).filter(models.Delivery.is_delivered==True, models.Delivery.user_id==current_user.id, func.date(models.Delivery.created_date)==cur_date.date()).all()
    form = SelectOption()

    if form.validate_on_submit():
        orders = connection.query(models.Delivery).filter(models.Delivery.is_delivered==True, models.Delivery.user_id==current_user.id, func.date(models.Delivery.created_date)==form.select_option.data).all()
        return render_template('/supplier/supplier1/expenses.html', orders=orders, form=form)

    return render_template('/supplier/supplier1/expenses.html', orders=orders, form=form)