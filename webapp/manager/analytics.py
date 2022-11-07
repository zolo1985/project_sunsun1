from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import DriversSelect, SelectOption
from datetime import datetime
from sqlalchemy import func
import pytz

manager_analytics_blueprint = Blueprint('manager_analytics', __name__)

@manager_analytics_blueprint.route('/manager/orders-stats', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_orders_stats():
    connection = Connection()
    initial_options = ["Долоо хоногоор", "Сараар", "Жилээр"]
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    completed = []
    postphoned = []
    cancelled = []
    total_monthly_orders = []
  
    yearly_orders_chart_tuple = connection.execute("SELECT MONTH(driver_order_history.delivery_date) as month, COUNT(*) as total, driver_order_history.delivery_status as status FROM sunsundatabase1.driver_order_history WHERE driver_order_history.delivery_date <= NOW() AND driver_order_history.delivery_date >= Date_add(Now(),interval - 12 month) and driver_order_history.type='delivery' GROUP BY YEAR(driver_order_history.delivery_date), MONTH(driver_order_history.delivery_date), driver_order_history.delivery_status;").all()
    for i, month in enumerate(months):
        completed.insert(i, 0)
        cancelled.insert(i, 0)
        postphoned.insert(i, 0)

    for month in months:
        for i, data in enumerate(yearly_orders_chart_tuple):
            if data["month"] == month:
                if data["status"] == "completed":
                    completed[int(data["month"] - 1)] = int(data["total"])
                elif data["status"] == "cancelled":
                    cancelled[int(data["month"] - 1)] = int(data["total"])
                elif data["status"] == "postphoned":
                    postphoned[int(data["month"] - 1)] = int(data["total"])
            else:
                continue

    for i, month in enumerate(months):
        total_monthly_orders.insert(i, 0)

    for month in months:
        for i, data in enumerate(yearly_orders_chart_tuple):
            if data["month"] == month:
                if data["status"] == "completed":
                    total_monthly_orders[int(data["month"] - 1)] = int(total_monthly_orders[int(data["month"] - 1)]) + int(data["total"])
                elif data["status"] == "cancelled":
                    total_monthly_orders[int(data["month"] - 1)] = int(total_monthly_orders[int(data["month"] - 1)]) + int(data["total"])
                elif data["status"] == "postphoned":
                    total_monthly_orders[int(data["month"] - 1)] = int(total_monthly_orders[int(data["month"] - 1)]) + int(data["total"])
            else:
                continue

    form = SelectOption()
    form.select_option.choices = [(option) for option in initial_options]

    if form.validate_on_submit():
        return render_template('/manager/orders_stats.html', title='Хүргэлт стастистик', data1=completed, data2=cancelled, data3=postphoned, data_total=total_monthly_orders, form=form)

    return render_template('/manager/orders_stats.html', title='Хүргэлт стастистик', data1=completed, data2=cancelled, data3=postphoned, data_total=total_monthly_orders, form=form)