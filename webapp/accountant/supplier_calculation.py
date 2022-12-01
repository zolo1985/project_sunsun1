from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import accountant, has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp.accountant.forms import FiltersForm, ReceivePaymentForm, DateSelect
from webapp import models
from datetime import datetime
import pytz

accountant_supplier_calculation_blueprint = Blueprint('accountant_supplier_calculation', __name__)

initial_delivery_status = ['started', 'completed', 'cancelled', 'postphoned', 'assigned', 'unassigned']

@accountant_supplier_calculation_blueprint.route('/accountant/supplier/calculations', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_supplier_calculations():
    connection = Connection()
    daily_total = []
    suppliers_total = []

    form = DateSelect()

    if form.validate_on_submit():

        suppliers_total = connection.execute('SELECT supplier.company_name as supplier_name, count(delivery.id) as total_delivery_count, sum(delivery.total_amount) as total_amount, supplier.is_invoiced as is_invoiced, supplier.fee as fee FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) = DATE(:date) and delivery.is_processed_by_accountant=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"date": form.select_date.data}).all()
        return render_template('/accountant/supplier_calculation.html', form=form, suppliers_total=suppliers_total)

    return render_template('/accountant/supplier_calculation.html', form=form, suppliers_total=suppliers_total)