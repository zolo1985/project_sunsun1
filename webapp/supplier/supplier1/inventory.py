from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import InventoryAddForm, ChooseType, InventoryPickupAddForm, DriverPickupForm
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter
import pytz

supplier1_inventory_blueprint = Blueprint('supplier1_inventory', __name__)

@supplier1_inventory_blueprint.route('/supplier1/inventories')
@login_required
@has_role('supplier1')
def supplier1_inventories():
    connection = Connection()
    inventories = connection.query(models.TotalInventory).filter_by(user_id=current_user.id)
    return render_template('/supplier/supplier1/inventories.html', inventories=inventories)


@supplier1_inventory_blueprint.route('/supplier1/inventories/add', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_add():
    initial_choices = ["Жолооч дуудах","Хүргэж өгөх"]

    form = ChooseType()
    form.choose_type.choices = [choice for choice in initial_choices]

    if form.validate_on_submit():

        if form.choose_type.data == "Жолооч дуудах":
            return redirect(url_for('supplier1_inventory.supplier1_inventory_pickup_add'))
        elif form.choose_type.data == "Хүргэж өгөх":
            return redirect(url_for('supplier1_inventory.supplier1_inventory_dropoff_add'))
        else:
            return render_template('/supplier/supplier1/inventory_add.html', form=form)

    return render_template('/supplier/supplier1/inventory_add.html', form=form)

@supplier1_inventory_blueprint.route('/supplier1/inventories/pickup/add', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_pickup_add():
    connection = Connection()
    form = InventoryPickupAddForm()
    form.product.choices = [(product.id, f'%s (хэмжээ: %s, өнгө: %s, үнэ: %s₮)'%(product.name, str(product.sizes).replace('[','').replace(']',''), str(product.colors).replace('[','').replace(']',''), str(product.price).replace('[','').replace(']',''))) for product in current_user.products]
    
    if form.validate_on_submit():
        line_quantity = request.form.getlist("quantity")
        line_product = request.form.getlist("product")

        try:
            pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id).filter(models.PickupTask.status=="waiting").filter(models.PickupTask.is_completed==False).first()

            if pickup_task:
                pickup_task.supplier_id = current_user.id
                pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                for i, quantity in enumerate(line_quantity):
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.quantity = quantity
                    pickup_task_detail.product_id = line_product[i]
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    pickup_task.pickup_details.append(pickup_task_detail)
            else:
                pickup_task = models.PickupTask()
                pickup_task.is_ready = True
                pickup_task.is_completed = False
                pickup_task.supplier_company = current_user.company_name
                pickup_task.status = "waiting"
                pickup_task.is_completed = False
                pickup_task.supplier_type = "supplier1"
                pickup_task.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                current_user.pickups.append(pickup_task)

                for i, quantity in enumerate(line_quantity):
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.quantity = quantity
                    pickup_task_detail.product_id = line_product[i]
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    pickup_task.pickup_details.append(pickup_task_detail)

            connection.commit()

        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(request.url)
        else:
            connection.close()
            flash('Барааг нэмлээ. Жолооч ирж авна.', 'success')
            return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups'))

    return render_template('/supplier/supplier1/inventory_add_pickup.html', form=form)


@supplier1_inventory_blueprint.route('/supplier1/inventories/pickup/delete/<int:task_id>', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_pickup_remove(task_id):
    connection = Connection()
    task = connection.query(models.PickupTask).get(task_id)
    connection.execute("delete from pickup_task where id=:id",{"id": task.id})
    connection.commit()
    return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups'))



@supplier1_inventory_blueprint.route('/supplier1/inventories/dropoff/add', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_dropoff_add():
    connection = Connection()
    form = InventoryAddForm()
    form.product.choices = [(product.id, f'%s (хэмжээ: %s, өнгө: %s, үнэ: %s₮)'%(product.name, str(product.sizes).replace('[','').replace(']',''), str(product.colors).replace('[','').replace(']',''), str(product.price).replace('[','').replace(']',''))) for product in current_user.products]
    receivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name == "clerk")).filter_by(is_authorized = True).all()
    form.choose_receiver.choices = [(receiver.id, receiver.firstname) for receiver in receivers]
    
    if form.validate_on_submit():
        line_quantity = request.form.getlist("quantity")
        line_product = request.form.getlist("product")

        received_by = connection.query(models.User).get(form.choose_receiver.data)

        try:
            if received_by.has_role("clerk"):
                for i, quantity in enumerate(line_quantity):
                    total_product_inventory = connection.query(models.TotalInventory).filter_by(product_id=line_product[i]).first()
                    inventory = models.Inventory()
                    inventory.quantity = quantity
                    inventory.inventory_type = "stored"
                    inventory.product_id = line_product[i]
                    inventory.clerk_name = f'%s %s'%(received_by.lastname, received_by.firstname)
                    inventory.clerk_id = received_by.id
                    inventory.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    total_product_inventory.quantity = total_product_inventory.quantity+int(quantity)
                    total_product_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    total_product_inventory.total_inventories.append(inventory)
                    connection.commit()
            else:
                flash('Барааг хүлээж авах эрхгүй ажилтан байна!', 'danger')
                raise Exception()
        
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(request.url)
        else:
            connection.close()
            flash('Бараа амжилттай хүлээлгэж өглөө. Хэрвээ жолоочид өгсөн бол нярав хүлээлгэж өгтөл хүлээгдэхийг анхаарна уу! Баярлалаа', 'success')
            return redirect(url_for('supplier1_inventory.supplier1_inventories'))

    return render_template('/supplier/supplier1/inventory_add_dropoff.html', form=form)


@supplier1_inventory_blueprint.route('/supplier1/inventories/pickups', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_pickups():
    connection = Connection()
    form = DriverPickupForm()

    count = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id == current_user.id).count()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    pickups = get_pickups(page, per_page)

    pagination = Pagination(page=page, total=count,  per_page=per_page, bs_version='5')

    if form.validate_on_submit():
        line_pickup_ids = request.form.getlist("pickup_id")
        for i, pickup_id in enumerate(line_pickup_ids):
            pickup = connection.query(models.PickupTask).get(pickup_id)
            if pickup.status == "enroute":
                pickup.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                pickup.status = "pickedup"

                # warehoused
                if pickup.supplier_type == "supplier1":
                    for i, pickup_detail in enumerate(pickup.pickup_details):
                        total_product_inventory = connection.query(models.TotalInventory).filter_by(product_id=pickup_detail.product_id).first()
                        inventory_in_transit = models.Inventory()
                        inventory_in_transit.status = True
                        inventory_in_transit.quantity = pickup_detail.quantity
                        inventory_in_transit.inventory_type = "stored"
                        inventory_in_transit.product_id = pickup_detail.product.id
                        inventory_in_transit.is_received_from_driver = True
                        inventory_in_transit.driver_name = pickup.driver_name
                        inventory_in_transit.driver_id = pickup.driver_id
                        inventory_in_transit.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        inventory_in_transit.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        
                        total_product_inventory.quantity = total_product_inventory.quantity+int(pickup_detail.quantity)
                        total_product_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        total_product_inventory.total_inventories.append(inventory_in_transit)
                        
                        connection.commit()
                        pickup_detail.inventory_id = inventory_in_transit.id
                        connection.commit()

                    pickup_history = models.DriverOrderHistory()
                    pickup_history.driver_id = pickup.driver_id
                    pickup_history.delivery_status = "pickedup"
                    pickup_history.address = pickup.supplier_company
                    pickup_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_history.type = "pickup"
                    pickup_history.task_id = pickup.id
                        
                    try:
                        connection.add(pickup_history)
                        connection.commit()
                    except Exception as e:
                        flash('Алдаа гарлаа!', 'danger')
                        connection.rollback()
                        connection.close()
                        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups'))
                    else:
                        connection.close()
                        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups'))

                #not warehoused
                elif pickup.supplier_type == "supplier2":
                    for i, pickup_detail in enumerate(pickup.pickup_details):
                        print(pickup_detail.quantity)
            else:
                continue

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(request.url)
        else:
            connection.close()
            flash('Жолоочид барааг хүлээлгэж өглөө', 'success')
            return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups'))

    return render_template('/supplier/supplier1/pickup_inventories.html', pickups=pickups, form=form, pagination=pagination)



def get_pickups(page, per_page):
    per_page_pickups=per_page
    offset = (page - 1) * per_page_pickups
    connection = Connection()
    pickups = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id == current_user.id).order_by(models.PickupTask.created_date.desc()).offset(offset).limit(per_page_pickups)
    connection.close()
    return pickups
