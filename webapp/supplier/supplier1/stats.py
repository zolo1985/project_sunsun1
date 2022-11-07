from flask import (Blueprint, render_template, request)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import SelectOption


supplier1_stats_blueprint = Blueprint('supplier1_stats', __name__)

initial_options = ["Өдрөөр", "Долоо хоногоор", "Сараар", "Жилээр"]

@supplier1_stats_blueprint.route('/supplier1/stats', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_stats():
    connection = Connection()

    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    completed = []
    cancelled = []
    total_monthly_orders = []
  
    yearly_orders_chart_tuple = connection.execute("SELECT MONTH(driver_order_history.delivery_date) as month, COUNT(*) as total, driver_order_history.delivery_status as status FROM driver_order_history as driver_order_history join sunsundatabase1.delivery as ob on driver_order_history.delivery_id=ob.id WHERE driver_order_history.delivery_date <= NOW() AND driver_order_history.delivery_date >= Date_add(Now(),interval - 12 month) and ob.user_id=:current_user and driver_order_history.delivery_status!='postphoned' GROUP BY YEAR(driver_order_history.delivery_date), MONTH(driver_order_history.delivery_date), driver_order_history.delivery_status;", {"current_user": current_user.id}).all()
    for i, month in enumerate(months):
        completed.insert(i, 0)
        cancelled.insert(i, 0)

    for month in months:
        for i, data in enumerate(yearly_orders_chart_tuple):
            if data["month"] == month:
                if data["status"] == "completed":
                    completed[int(data["month"] - 1)] = int(data["total"])
                elif data["status"] == "cancelled":
                    cancelled[int(data["month"] - 1)] = int(data["total"])
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
            else:
                continue

    form = SelectOption()
    form.select_option.choices = [(option) for option in initial_options]

    if form.validate_on_submit():
        return render_template('/shared/stats.html', title='Хүргэлт стастистик', data1=completed, data2=cancelled, data_total=total_monthly_orders, form=form)

    return render_template('/shared/stats.html', title='Хүргэлт стастистик', data1=completed, data2=cancelled, data_total=total_monthly_orders, form=form)