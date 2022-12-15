from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import accountant, has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp.accountant.forms import FiltersForm, ReceivePaymentForm, DateSelect
from webapp import models
from datetime import datetime, timedelta
import pytz

accountant_driver_payment_blueprint = Blueprint('accountant_driver_payment', __name__)

@accountant_driver_payment_blueprint.route('/accountant/driver-payments', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_driver_payments():
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
    managers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="manager")).all()
    
    form = FiltersForm()
    form.drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers + managers]
    form.drivers.choices.insert(0,(0,'Жолооч сонгох'))

    orders = []

    unprocessed_orders = connection.execute('SELECT count(delivery.id) as total_count, delivery.assigned_driver_name as driver_name FROM sunsundatabase1.delivery as delivery WHERE delivery.is_processed_by_accountant=false and delivery.is_delivered=true and delivery.status="completed" group by delivery.assigned_driver_name;').all()

    form1 = ReceivePaymentForm()

    if form.validate_on_submit():
        orders = connection.query(models.Delivery).filter(models.Delivery.assigned_driver_id==form.drivers.data).filter(models.Delivery.is_delivered==True).filter(models.Delivery.is_processed_by_accountant==False).filter(models.Delivery.status=="completed").all()
        return render_template('/accountant/driver_payments.html', form=form, orders=orders, form1=form1)

    if form1.validate_on_submit():
        line_order_id_values = request.form.getlist("orderIdValue")
        line_orders_total = request.form.getlist("ordersTotal")

        print(line_order_id_values)
        print(line_orders_total)

        return redirect(url_for("accountant_driver_payment.accountant_driver_payments"))


        # if int(form1.card_amount.data) + int(form1.cash_amount.data) + int(form1.remaining_amount.data) == int(form1.net_amount.data):
        #     line_order_id = request.form.getlist("order_id")

        #     driver_name = ""
        #     driver_id = 0

        #     for line_order in line_order_id:
        #         order_to_update = connection.query(models.Delivery).get(int(line_order))
        #         driver_name = order_to_update.assigned_driver_name
        #         driver_id = order_to_update.assigned_driver_id

        #         if order_to_update.is_processed_by_accountant == False:
        #             order_to_update.is_processed_by_accountant = True
        #             order_to_update.processed_accountant_id = current_user.id
        #             order_to_update.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        #         else:
        #             continue

        #     accountant_order_history = models.AccountantPaymentHistory()
        #     accountant_order_history.cash_amount = form1.cash_amount.data
        #     accountant_order_history.card_amount = form1.card_amount.data
        #     accountant_order_history.remaining_amount = form1.remaining_amount.data
        #     accountant_order_history.date_of_payment = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) - timedelta(hours=+24)
        #     accountant_order_history.comment = form1.comment.data
        #     accountant_order_history.delivery_ids = str(line_order_id)
        #     accountant_order_history.accountant_id = current_user.id
        #     accountant_order_history.driver_id = driver_id
        #     accountant_order_history.driver_name = driver_name
        #     accountant_order_history.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        #     accountant_order_history.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        #     accountant_order_history.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        #     connection.add(accountant_order_history)

        #     try:
        #         connection.commit()
        #     except Exception as e:
        #         connection.rollback()
        #         connection.close()
        #         flash('Алдаа гарлаа!', 'danger')
        #         return redirect(url_for("accountant_driver_payment.accountant_driver_payments"))
        #     else:
        #         return redirect(url_for("accountant_driver_payment.accountant_driver_payments"))

        # else:
        #     flash('Нийлбэр дүн таарахгүй байна!', 'danger')
        #     return redirect(url_for("accountant_driver_payment.accountant_driver_payments"))

    return render_template('/accountant/driver_payments.html', form=form, orders=orders, form1=form1, unprocessed_orders=unprocessed_orders)