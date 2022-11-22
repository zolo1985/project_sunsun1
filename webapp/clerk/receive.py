from flask import (Blueprint, flash, redirect, render_template, url_for, request)
from webapp import has_role
from flask_login import current_user, login_required
from flask_paginate import Pagination, get_page_parameter
from webapp import models
from webapp.database import Connection
from datetime import datetime
from webapp.clerk.forms import ReceiveInventoryForm
from sqlalchemy import func
import pytz

clerk_receive_blueprint = Blueprint('clerk_receive', __name__)

@clerk_receive_blueprint.route('/clerk/pickup-receive', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_receive_pickup_inventories():
    connection = Connection()
    form = ReceiveInventoryForm()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    pickups = connection.query(models.PickupTask).filter(func.date(models.PickupTask.created_date) == cur_date).order_by(models.PickupTask.is_received).all()

    if form.validate_on_submit():
        pickups = connection.query(models.PickupTask).filter(func.date(models.PickupTask.created_date) == form.date.data).order_by(models.PickupTask.is_received).all()
        return render_template('/clerk/receive_pickup_inventories.html', pickups=pickups, form=form)

    return render_template('/clerk/receive_pickup_inventories.html', pickups=pickups, form=form)



@clerk_receive_blueprint.route('/clerk/dropoff-receive', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_receive_dropoff_inventories():
    connection = Connection()
    form = ReceiveInventoryForm()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    inventories = connection.query(models.Inventory).filter(models.Inventory.is_received_from_driver == False).filter(func.date(models.Inventory.received_date) == cur_date).order_by(models.Inventory.id.desc()).all()

    if form.validate_on_submit():
        inventories = connection.query(models.Inventory).filter(models.Inventory.is_received_from_driver == False).filter(func.date(models.Inventory.received_date) == form.date.data).order_by(models.Inventory.id.desc()).all()
        return render_template('/clerk/receive_dropoff_inventories.html', inventories=inventories, form=form)

    return render_template('/clerk/receive_dropoff_inventories.html', inventories=inventories, form=form)


@clerk_receive_blueprint.route('/clerk/dropoff-receive/<int:inventory_id>', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_accept_dropoff_inventories(inventory_id):
    connection = Connection()
    inventory = connection.query(models.Inventory).get(inventory_id)

    if inventory is None:
        flash('Олдонгүй')
        connection.close()
        return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))

    if inventory.clerk_id is not None and inventory.clerk_id != current_user.id:
        flash("Ачааг зөвхөн харилцагч хүлээгэж өгсөн нярав авах эрхтэй!", 'warning')
        connection.close()
        return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))
    else:
        inventory.status = True
        inventory.clerk_accepted_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception as ex:
            flash("Алдаа гарлаа!", 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))
        else:
            flash("Бараа агуулахад нэмэгдлээ.", 'success')
            connection.close()
            return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))


@clerk_receive_blueprint.route('/clerk/pickup-receive/<int:pickup_task_id>', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_accept_pickup_inventories(pickup_task_id):
    connection = Connection()
    pickup_task = connection.query(models.PickupTask).get(pickup_task_id)
    driver_pickup_history = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.task_id==pickup_task.id).first()

    if pickup_task is None:
        flash('Олдонгүй', 'danger')
        connection.close()
        return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))

    if pickup_task.is_received == True:
        flash('Барааг хүлээж авсан байна!', 'danger')
        connection.close()
        return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))

    pickup_task.is_received = True
    pickup_task.is_completed = True
    pickup_task.status = "completed"
    pickup_task.received_clerk_id = current_user.id
    pickup_task.delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    pickup_task.clerk_received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    driver_pickup_history.delivery_status = "completed"
    driver_pickup_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    if pickup_task.supplier_type == "supplier1":
        for detail in pickup_task.pickup_details:
            inventory_to_update = connection.query(models.Inventory).get(detail.inventory_id)
            inventory_to_update.clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
            inventory_to_update.clerk_id = current_user.id
            inventory_to_update.clerk_accepted_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            inventory_to_update.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception as ex:
            flash("Алдаа гарлаа!", 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))
        else:
            flash("Бараа хүлээж авлаа.", 'success')
            connection.close()
            return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))

    elif pickup_task.supplier_type == "supplier2":
        for detail in pickup_task.pickup_details:
            inventory_to_update = connection.query(models.Inventory).get(detail.inventory_id)
            inventory_to_update.clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
            inventory_to_update.clerk_id = current_user.id
            inventory_to_update.clerk_accepted_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            inventory_to_update.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception as ex:
            flash("Алдаа гарлаа!", 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))
        else:
            flash("Бараа хүлээж авлаа.", 'success')
            connection.close()
            return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))


# @clerk_receive_blueprint.route('/clerk/receive/driver/add/<int:inventory_in_transit_id>', methods=['GET','POST'])
# @login_required
# @has_role('clerk')
# def clerk_receive_inventories_from_driver(inventory_in_transit_id):

#     connection = Connection()
#     inventory = connection.query(models.Inventory).get(inventory_in_transit_id)

#     if inventory is None:
#         flash('Олдонгүй')
#         connection.close()
#         return redirect(url_for('clerk_receive.clerk_receive_inventories'))

#     if inventory.receiver_id is not None and inventory.receiver_id != current_user.id:
#         flash("Ачааг зөвхөн харилцагч хүлээгэж өгсөн нярав авах эрхтэй!", 'warning')
#         connection.close()
#         return redirect(url_for('clerk_receive.clerk_receive_inventories'))
#     else:
#         try:
#             transit_inventory = connection.query(models.Inventory).get(inventory_in_transit_id)
#             driver = connection.query(models.User).get(transit_inventory.driver_id)
#             transit_inventory.status = True
#             transit_inventory.is_received_from_driver = True
#             transit_inventory.driver_name = f'%s %s'%(driver.lastname, driver.firstname)
#             transit_inventory.receiver_id = current_user.id
#             transit_inventory.clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
#             transit_inventory.clerk_accepted_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#             transit_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

#             pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.is_ready==True).filter(models.PickupTask.is_completed==False).filter(models.PickupTask.status=="pickedup").filter(models.PickupTask.driver_id == driver.id).first()

#             if pickup_task:
#                 pickup_task.status = "completed"
#                 pickup_task.is_completed = True
#                 pickup_task.is_ready = False
#                 pickup_task.delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#                 pickup_task.receiver_id = current_user.id

#                 pickup_history = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.task_id==pickup_task.id).first()
#                 pickup_history.delivery_status = "completed"
#                 pickup_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            
#             connection.commit()

#         except Exception as ex:
#             flash("Алдаа гарлаа!", 'danger')
#             connection.rollback()
#             connection.close()
#         else:
#             flash("Бараа агуулахад нэмэгдлээ.", 'success')
#             connection.close()

#     return redirect(url_for('clerk_inventory.clerk_driver_inventories'))


# @clerk_receive_blueprint.route('/clerk/receive/<int:inventory_in_transit_id>/<int:order_id>/<int:account_order_id>', methods=['GET','POST'])
# @login_required
# @has_role('clerk')
# def clerk_receive_inventories_from_supplier2_driver(inventory_in_transit_id, order_id, account_order_id):
#     connection = Connection()
#     inventory = connection.query(models.Inventory).get(inventory_in_transit_id)

#     if inventory is None:
#         flash('Олдонгүй')
#         connection.close()
#         return redirect(url_for('clerk_receive.clerk_receive_inventories'))

#     if inventory.receiver_id is not None and inventory.receiver_id != current_user.id:
#         flash("Ачааг зөвхөн харилцагч хүлээгэж өгсөн нярав авах эрхтэй!", 'warning')
#         connection.close()
#         return redirect(url_for('clerk_receive.clerk_receive_inventories'))
#     else:
#         account_order = connection.query(models.Supplier2Order).get(account_order_id)
#         account_order.received_clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
#         account_order.received_clerk_id = current_user.id
#         account_order.status = "received"

#         pickup_task = connection.query(models.PickupTask).get(account_order.driver_pickup_task_id)
#         pickup_task.order_status = "completed"
#         pickup_task.is_completed = True
#         pickup_task.is_ready = False
#         pickup_task.order_delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#         pickup_task.receiver_id = current_user.id

#         pickup_history = connection.query(models.DriverOrderHistory).get(pickup_task.id)
#         pickup_history.delivery_status = "completed"
#         pickup_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

#         transit_inventory = connection.query(models.Inventory).get(inventory_in_transit_id)
#         driver = connection.query(models.User).get(transit_inventory.driver_id)
#         transit_inventory.status = True

#         transit_inventory.is_received_from_driver = True
#         transit_inventory.driver_name = f'%s %s'%(driver.lastname, driver.firstname)
#         transit_inventory.clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)

#         transit_inventory.receiver_id = current_user.id
#         transit_inventory.clerk_accepted_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#         transit_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

#         order = connection.query(models.OrderTable).get(order_id)
#         order.is_ready = True
#         order.is_in_inventory = True

#         try:
#             connection.add(pickup_history)
#             connection.commit()

#         except Exception as ex:
#             flash("Алдаа гарлаа!", 'danger')
#             connection.rollback()
#             connection.close()
#         else:
#             flash("Бараа агуулахад нэмэгдлээ.", 'success')
#             connection.close()

#         return redirect(url_for('clerk_inventory.clerk_driver_inventories'))


# @clerk_receive_blueprint.route('/clerk/receive/add/<int:inventory_id>', methods=['GET','POST'])
# @login_required
# @has_role('clerk')
# def clerk_receive_inventories_from_supplier1(inventory_id):
    
#     connection = Connection()
#     inventory = connection.query(models.Inventory).get(inventory_id)

#     if inventory is None:
#         flash('Олдонгүй')
#         connection.close()
#         return redirect(url_for('clerk_receive.clerk_receive_inventories'))

#     if inventory.receiver_id is not None and inventory.receiver_id != current_user.id:
#         flash("Ачааг зөвхөн харилцагч хүлээгэж өгсөн нярав авах эрхтэй!", 'warning')
#         connection.rollback()
#         connection.close()
#         return redirect(url_for('clerk_receive.clerk_receive_inventories'))
#     else:
#         try:
#             inventory.status = True
#             inventory.receiver_id == current_user.id
#             inventory.clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
#             inventory.clerk_accepted_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#             inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#             connection.commit()
#         except Exception as ex:
#             flash("Алдаа гарлаа!", 'danger')
#             connection.rollback()
#             connection.close()
#         else:
#             flash("Бараа агуулахад нэмэгдлээ.", 'success')
#             connection.close()

#         return redirect(url_for('clerk_receive.clerk_receive_inventories'))