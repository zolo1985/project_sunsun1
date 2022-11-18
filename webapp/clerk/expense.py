from flask import (Blueprint, render_template, redirect, url_for, flash, request)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp import models
from datetime import datetime
from .forms import FiltersForm, DriverOrders
from sqlalchemy import func
import pytz

clerk_expense_blueprint = Blueprint('clerk_expense', __name__)

@clerk_expense_blueprint.route('/clerk/expenses', methods=['GET','POST'])
@login_required
@has_role('clerk')
def clerk_driver_orders():
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    # cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    # orders = connection.query(models.Delivery).filter(func.date(models.Delivery.delivery_date) == cur_date).filter(models.Delivery.status!="cancelled").filter(models.Delivery.is_driver_received==False).all()
    orders = []

    form = FiltersForm()
    form.drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]
    form.drivers.choices.insert(0,(0,'Жолооч сонгох'))

    unassigned_orders = connection.execute('SELECT count(delivery.id) as total_count, delivery.assigned_driver_name as driver_name FROM sunsundatabase1.delivery as delivery WHERE DATE(delivery.delivery_date) = CURDATE() and delivery.is_delivered=false and delivery.status="assigned" and delivery.received_from_clerk_id is null group by delivery.assigned_driver_name;').all()

    form1 = DriverOrders()
    
    if form.drivers.data is not None and form.validate():
        if form.drivers.data!="0":
            user = connection.query(models.User).filter(models.User.id==form.drivers.data).first()
            if user is not None:
                orders = connection.query(models.Delivery).filter(models.Delivery.is_ready==True).filter(models.Delivery.status=="assigned").filter(models.Delivery.assigned_driver_id==user.id).all()
            return render_template('/clerk/expenses.html', form=form, orders=orders, form1=form1)
        else:
            unassigned_orders = connection.execute('SELECT count(delivery.id) as total_count, delivery.assigned_driver_name as driver_name FROM sunsundatabase1.delivery as delivery WHERE DATE(delivery.delivery_date) = CURDATE() and delivery.is_delivered=false and delivery.status="assigned" and delivery.received_from_clerk_id is null group by delivery.assigned_driver_name;').all()
            return render_template('/clerk/expenses.html', form=form, form1=form1, unassigned_orders=unassigned_orders)

    if form1.validate_on_submit():
        line_order_id = request.form.getlist("order_id")

        for i, order_id in enumerate(line_order_id):
            order = connection.query(models.Delivery).get(order_id)

            if order.is_driver_received==False and order.is_received_from_clerk==True:
                try:
                    order.received_from_clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
                    order.received_from_clerk_id = current_user.id
                    order.is_driver_received = True
                    order.received_from_clerk_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('clerk_expense.clerk_driver_orders'))
            else:
                continue
            
        flash('Бараа хүлээлгэж өглөө', 'success')
        return redirect(url_for('clerk_expense.clerk_driver_orders'))

    return render_template('/clerk/expenses.html', form=form, orders=orders, form1=form1, unassigned_orders=unassigned_orders)

@clerk_expense_blueprint.route('/clerk/expenses/<int:order_id>')
@login_required
@has_role('clerk')
def clerk_driver_orders_expense(order_id):
    connection = Connection()
    order_to_expense = connection.query(models.Delivery).filter(models.Delivery.id==order_id).first()

    if order_to_expense.received_from_clerk_id is not None:
        flash(f'Хүргэлт хувиарлагдсан байна(өгсөн нярав: %s)'%(order_to_expense.received_from_clerk_name), 'danger')
        connection.close()
        return redirect(url_for('clerk_expense.clerk_driver_orders'))
    else:
        try:
            order_to_expense.received_from_clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
            order_to_expense.received_from_clerk_id = current_user.id
            order_to_expense.received_from_clerk_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            connection.commit()
        except Exception():
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(request.url)
        else:
            flash('Хүргэлт амжилттай хүлээлгэж өглөө!', 'success')
            connection.close()
            return redirect(request.url)