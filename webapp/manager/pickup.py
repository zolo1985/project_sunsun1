from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from flask_paginate import Pagination, get_page_parameter
from webapp.manager.forms import DriversDateSelect, FilterDateForm
from datetime import datetime, timedelta
from sqlalchemy import func
import pytz

manager_pickup_blueprint = Blueprint('manager_pickup', __name__)

@manager_pickup_blueprint.route('/manager/pickups', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_pickups():
    connection = Connection()
    form = DriversDateSelect()
    receivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name == "driver")).filter_by(is_authorized = True).all()
    form.select_drivers.choices = [(receiver.id, receiver.firstname) for receiver in receivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))

    days = ["Өнөөдөр","Маргааш"]

    form.select_day.choices = [day for day in days]
    pickups = connection.query(models.PickupTask).filter(models.PickupTask.status!="completed").order_by(models.PickupTask.created_date.desc()).all()

    if form.validate_on_submit():
        line_task_id = request.form.getlist("task_id")
        line_select_drivers_id = request.form.getlist("select_drivers")
        line_select_day = request.form.getlist("select_day")

        for i, task in enumerate(line_task_id):
            if line_select_drivers_id[i] == "0" or line_select_drivers_id[i] is None:
                continue

            driver_name = connection.query(models.User).get(int(line_select_drivers_id[i]))
            task = connection.query(models.PickupTask).get(task)

            task.driver_id = int(line_select_drivers_id[i])
            task.driver_name = f'%s %s'%(driver_name.lastname, driver_name.firstname)
            task.pickup_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) if line_select_day[i] == "Өнөөдөр" else datetime.now(pytz.timezone("Asia/Ulaanbaatar")) + timedelta(days=1)
            task.status = "enroute"
            task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            task.assigned_manager_name = current_user.firstname
            
            try:
                connection.commit()
            except Exception:
                connection.rollback()
                connection.close()
            else:
                connection.close()

        return redirect(url_for('manager_pickup.manager_pickups'))
    return render_template('/manager/pickups.html', pickups=pickups, form=form)


@manager_pickup_blueprint.route('/manager/pickups/history', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_pickups_history():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    pickups = connection.query(models.PickupTask).filter(func.date(models.PickupTask.created_date) == cur_date).order_by(models.PickupTask.created_date.desc()).all()

    form = FilterDateForm()

    if form.validate_on_submit() and form.date.data is not None:
        pickups = connection.query(models.PickupTask).filter(func.date(models.PickupTask.created_date) == form.date.data).order_by(models.PickupTask.created_date.desc()).all()
        return render_template('/manager/pickup_histories.html', pickups=pickups, form=form)

    return render_template('/manager/pickup_histories.html', pickups=pickups, form=form)



@manager_pickup_blueprint.route('/manager/pickups/<int:pickup_id>', methods=['GET'])
@login_required
@has_role('manager')
def manager_pickup(pickup_id):
    connection = Connection()
    pickup = connection.query(models.PickupTask).get(pickup_id)

    if pickup is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('manager_pickup.manager_pickups'))

    return render_template('/manager/pickup.html', pickup=pickup)