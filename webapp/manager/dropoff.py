from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import DriversSelect, FilterDateForm
from datetime import datetime, timedelta
from sqlalchemy import func
import pytz

manager_dropoff_blueprint = Blueprint('manager_dropoff', __name__)

@manager_dropoff_blueprint.route('/manager/dropoffs', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_dropoffs():
    connection = Connection()
    form = DriversSelect()
    receivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name == "driver")).filter_by(is_authorized = True).all()
    form.select_drivers.choices = [(receiver.id, receiver.firstname) for receiver in receivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))

    dropoffs = connection.query(models.DropoffTask).filter(models.DropoffTask.is_ready==True).order_by(models.DropoffTask.created_date.desc()).all()

    if form.validate_on_submit():
        line_task_id = request.form.getlist("task_id")
        line_select_drivers_id = request.form.getlist("select_drivers")

        for i, task in enumerate(line_task_id):
            if line_select_drivers_id[i] == "0" or line_select_drivers_id[i] is None:
                continue

            driver_name = connection.query(models.User).get(int(line_select_drivers_id[i]))
            task = connection.query(models.DropoffTask).get(task)

            task.driver_id = int(line_select_drivers_id[i])
            task.driver_name = f'%s %s'%(driver_name.lastname, driver_name.firstname)
            task.status = "pickedup"
            task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            task.assigned_manager_id = current_user.id

            dropoff_history = models.DriverOrderHistory()
            dropoff_history.driver_id = int(line_select_drivers_id[i])
            dropoff_history.delivery_status = "pickedup"
            dropoff_history.address = task.supplier_company
            dropoff_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            dropoff_history.type = "dropoff"
            dropoff_history.dropoff_id = task.id
            dropoff_history.supplier_name = task.supplier_company
            
            try:
                connection.add(dropoff_history)
                connection.commit()
            except Exception:
                connection.rollback()
                connection.close()
            else:
                connection.close()

        return redirect(url_for('manager_dropoff.manager_dropoffs'))

    return render_template('/manager/dropoffs.html', dropoffs=dropoffs, form=form)


@manager_dropoff_blueprint.route('/manager/dropoffs/history', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_dropoffs_history():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    dropoffs = connection.query(models.DropoffTask).filter(func.date(models.DropoffTask.created_date) == cur_date).all()

    form = FilterDateForm()

    if form.validate_on_submit() and form.date.data is not None:
        dropoffs = connection.query(models.DropoffTask).filter(func.date(models.DropoffTask.created_date) == form.date.data).all()
        return render_template('/manager/dropoff_histories.html', dropoffs=dropoffs, form=form)

    return render_template('/manager/dropoff_histories.html', dropoffs=dropoffs, form=form)