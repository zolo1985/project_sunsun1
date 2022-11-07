from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import DriversSelect
from datetime import datetime
from sqlalchemy import func
import pytz

manager_driver_stats_blueprint = Blueprint('manager_driver_stats', __name__)

@manager_driver_stats_blueprint.route('/manager/drivers-stats', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_drivers_stats():
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
    form = DriversSelect()
    form.select_drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]

    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    completed = []
    postphoned = []
    cancelled = []
    total_monthly_jobs = []

    if form.validate_on_submit():
        yearly_driver_chart_tuple = connection.execute("SELECT MONTH(driver_order_history.delivery_date) as month, COUNT(*) as total, driver_order_history.delivery_status as status FROM sunsundatabase1.driver_order_history WHERE driver_order_history.delivery_date <= NOW() AND driver_order_history.delivery_date >= Date_add(Now(),interval - 12 month) and driver_order_history.driver_id=:driver_id and driver_order_history.type='delivery' GROUP BY YEAR(driver_order_history.delivery_date), MONTH(driver_order_history.delivery_date), driver_order_history.delivery_status;", {'driver_id': form.select_drivers.data}).all()
        for i, month in enumerate(months):
            completed.insert(i, 0)
            cancelled.insert(i, 0)
            postphoned.insert(i, 0)

        for month in months:
            for i, data in enumerate(yearly_driver_chart_tuple):
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
            total_monthly_jobs.insert(i, 0)

        for month in months:
            for i, data in enumerate(yearly_driver_chart_tuple):
                if data["month"] == month:
                    if data["status"] == "completed":
                        total_monthly_jobs[int(data["month"] - 1)] = int(total_monthly_jobs[int(data["month"] - 1)]) + int(data["total"])
                    elif data["status"] == "cancelled":
                        total_monthly_jobs[int(data["month"] - 1)] = int(total_monthly_jobs[int(data["month"] - 1)]) + int(data["total"])
                    elif data["status"] == "postphoned":
                        total_monthly_jobs[int(data["month"] - 1)] = int(total_monthly_jobs[int(data["month"] - 1)]) + int(data["total"])
                else:
                    continue

        return render_template('/manager/drivers_stats.html', title='Шинжилгээ', data1=completed, data2=cancelled, data3=postphoned, data_total=total_monthly_jobs, form=form)

    return render_template('/manager/drivers_stats.html', title='Шинжилгээ', data1=completed, data2=cancelled, data3=postphoned, data_total=total_monthly_jobs, form=form)