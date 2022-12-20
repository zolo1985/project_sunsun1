from flask import (Blueprint, render_template, request, redirect, abort, url_for, flash)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp import models
from sqlalchemy import func, or_
from .forms import DeliveryStatusForm, DeliveryPostphonedForm, DeliveryCancelledForm, DateSelect
from datetime import datetime
import pytz

driver_job_blueprint = Blueprint('driver_job', __name__)

initial_delivery_status = ['Хүргэлтийг эхлүүлэх', 'Хүргэсэн', 'Цуцалсан', 'Хойшилсон']

def switch_status(status):
    if status == "Хувиарласан":
        return "assigned"
    elif status == "Хүргэлтийг эхлүүлэх":
        return "started"
    elif status == "Хүргэсэн":
        return "completed"
    elif status == "Цуцалсан":
        return "cancelled"
    elif status == "Хойшилсон":
        return "postphoned"
    elif status == "Хувиарлагдаагүй":
        return "unassigned"

@driver_job_blueprint.route('/driver/jobs')
@login_required
@has_role('driver')
def driver_jobs():
    connection = Connection()
    jobs = connection.query(models.Delivery).filter(models.Delivery.assigned_driver_id==current_user.id).filter(or_(models.Delivery.status == "assigned", models.Delivery.status =="started")).order_by(models.Delivery.status.desc()).all()
    return render_template('/driver/jobs.html', jobs=jobs)


@driver_job_blueprint.route('/driver/jobs/history', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_jobs_history():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = DateSelect()

    jobs = connection.query(models.Delivery).filter(models.Delivery.assigned_driver_id==current_user.id, func.date(models.Delivery.created_date) == cur_date.date()).order_by(models.Delivery.delivered_date.desc()).all()

    if form.validate_on_submit():
        jobs = connection.query(models.Delivery).filter(models.Delivery.assigned_driver_id==current_user.id, func.date(models.Delivery.created_date) == form.select_date.data).order_by(models.Delivery.delivered_date.desc()).all()
        return render_template('/driver/jobs_history.html', jobs=jobs, form=form)

    return render_template('/driver/jobs_history.html', jobs=jobs, form=form)


@driver_job_blueprint.route('/driver/jobs/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_job_detail(order_id):

    connection = Connection()
    form = DeliveryStatusForm()
    form.current_status.choices = [(status) for status in initial_delivery_status]
    
    job = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != job.assigned_driver_id:
        connection.close()
        abort(403)

    if form.validate_on_submit():

        if switch_status(form.current_status.data) == "postphoned":
            return redirect(url_for('driver_job.driver_job_detail_postphoned', order_id=job.id))
        elif switch_status(form.current_status.data) == "cancelled":
            return redirect(url_for('driver_job.driver_job_detail_cancelled', order_id=job.id))
        elif switch_status(form.current_status.data) == "completed":
            return redirect(url_for('driver_job.driver_job_detail_completed', order_id=job.id))

        elif switch_status(form.current_status.data) == "started":
            try:
                # job_tp_update = connection.query(models.Delivery).filter_by(id=job.id).first()
                job.status = "started"
                job.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                connection.commit()
            except Exception as ex:
                flash('Алдаа гарлаа', 'danger')
                connection.rollback()
                connection.close()
                return redirect(url_for('driver_job.driver_jobs'))
            else:
                connection.close()
                return redirect(url_for('driver_job.driver_jobs'))
    return render_template('/driver/job.html', job=job, form=form)


@driver_job_blueprint.route('/driver/jobs/postphoned/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_job_detail_postphoned(order_id):

    connection = Connection()
    form = DeliveryPostphonedForm()
    
    job = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != job.assigned_driver_id:
        connection.close()
        abort(403)

    if form.validate_on_submit():
        try:
            job.status = "postphoned"
            job.postphoned_date = form.postphoned_date.data
            job.delivery_date = form.postphoned_date.data
            job.driver_comment = form.driver_comment.data
            job.is_postphoned = True
            job.is_delivered = False
            job.delivery_attempts = job.delivery_attempts + 1
            job.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            job_history = models.DriverOrderHistory()
            job_history.driver_id = current_user.id
            job_history.delivery_id = job.id
            job_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            job_history.delivery_status = "postphoned"
            job_history.supplier_name = job.supplier_company_name
            job_history.address = job_history.address = f'%s, %s, %s,'%(job.addresses.district, job.addresses.khoroo, job.addresses.address)
            connection.add(job_history)

            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('driver_job.driver_jobs'))
        else:
            flash('Хүргэлт хойшлогдлоо', 'info')
            connection.close()
            return redirect(url_for('driver_job.driver_jobs'))

    return render_template('/driver/job_postphoned.html', job=job, form=form)


@driver_job_blueprint.route('/driver/jobs/cancelled/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_job_detail_cancelled(order_id):

    connection = Connection()
    form = DeliveryCancelledForm()
    
    job = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != job.assigned_driver_id:
        connection.close()
        abort(403)

    if form.validate_on_submit():
        try:
            job.status = "cancelled"
            job.driver_comment = form.driver_comment.data
            job.is_cancelled = True
            job.is_delivered = False
            job.is_ready = False
            job.delivery_attempts = job.delivery_attempts + 1
            job.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            job_history = models.DriverOrderHistory()
            job_history.driver_id = current_user.id
            job_history.delivery_id = job.id
            job_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            job_history.delivery_status = "cancelled"
            job_history.supplier_name = job.supplier_company_name
            job_history.address = job_history.address = f'%s, %s, %s,'%(job.addresses.district, job.addresses.khoroo, job.addresses.address)
            connection.add(job_history)
            
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('driver_job.driver_jobs'))
        else:
            flash('Хүргэлт цуцлагдлаа', 'info')
            connection.close()
            return redirect(url_for('driver_job.driver_jobs'))

    return render_template('/driver/job_cancelled.html', job=job, form=form)


@driver_job_blueprint.route('/driver/jobs/completed/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_job_detail_completed(order_id):

    connection = Connection()
    form = DeliveryCancelledForm()
    
    job = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != job.assigned_driver_id:
        connection.close()
        abort(403)

    if form.validate_on_submit():
        job.status = "completed"
        job.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        job.delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        job.delivery_attempts = job.delivery_attempts + 1
        job.is_delivered = True
        job.is_ready = False

        job_history = models.DriverOrderHistory()
        job_history.driver_id = current_user.id
        job_history.delivery_id = job.id
        job_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        job_history.delivery_status = "completed"
        job_history.supplier_name = job.supplier_company_name

        if job.destination_type == "local":
            job_history.address = job_history.address = f'%s, %s, %s, %s'%(job.addresses.district, job.addresses.khoroo, job.addresses.address, job.addresses.phone)
        elif job.destination_type == "long":
            job_history.address = job_history.address = f'%s, %s, %s'%(job.addresses.aimag, job.addresses.address, job.addresses.phone)
        
        connection.add(job_history)

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('driver_job.driver_jobs'))
        else:
            connection.close()
            return redirect(url_for('driver_job.driver_jobs'))
    
    return render_template('/driver/job_cancelled.html', job=job, form=form)


@driver_job_blueprint.route('/driver/jobs/accepted/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_job_accept(order_id):
    connection = Connection()

    order = connection.query(models.Delivery).get(order_id)

    if not order:
        flash('Хүргэлт олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('driver_job.driver_jobs'))
    else:
        if order.assigned_driver_id == current_user.id:
            order.is_received_from_clerk = True
            order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        
            try:    
                connection.commit()
            except Exception as ex:
                flash('Алдаа гарлаа', 'danger')
                connection.rollback()
                connection.close()
                return redirect(url_for('driver_job.driver_jobs'))
            else:
                flash('Хүргэлт хүлээж авлаа', 'success')
                connection.close()
                return redirect(url_for('driver_job.driver_jobs'))
        else:
            flash('Хувиарлагдсан жолооч ч өөрчлөх боломжтой', 'info')
            connection.close()
            return redirect(url_for('driver_job.driver_jobs'))


    
