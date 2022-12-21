from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier2.forms import OrderAddForm, TransferForm, OrderEditForm, DateSelectForm
from datetime import datetime, time, timedelta
from sqlalchemy import func, or_
from webapp.utils import is_time_between
import pytz

supplier2_order_blueprint = Blueprint('supplier2_order', __name__)

@supplier2_order_blueprint.route('/supplier2/orders', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_orders():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    orders1 = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id).filter(func.date(models.Delivery.created_date) == cur_date.date()).order_by(models.Delivery.created_date).all()
    post_orders = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id).filter(func.date(models.Delivery.postphoned_date) == cur_date.date()).filter(models.Delivery.is_postphoned == True).all()
    orders = orders1 + post_orders

    form = DateSelectForm()

    if form.date.data is not None and form.validate_on_submit():
        orders1 = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id).filter(func.date(models.Delivery.created_date) == form.date.data).order_by(models.Delivery.created_date).all()
        post_orders = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id).filter(func.date(models.Delivery.postphoned_date) == form.date.data).filter(models.Delivery.is_postphoned == True).all()

        for post_order in post_orders:
            if post_order in orders1:
                continue
            else:
                orders1.append(post_order)
        orders = orders1

        return render_template('/supplier/supplier2/orders.html', cur_date=cur_date, orders=orders, form=form)

    return render_template('/supplier/supplier2/orders.html', cur_date=cur_date, orders=orders, form=form)


@supplier2_order_blueprint.route('/supplier2/orders/add', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_add():

    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    order_window = is_time_between(time(16,00), time(20,00))
    connection = Connection()
    districts = connection.query(models.District).all()
    aimags = connection.query(models.Aimag).all()

    form = OrderAddForm()
    form.district.choices = [(district) for district in districts]
    form.district.choices.insert(0,'Дүүрэг сонгох')
    form.khoroo.choices = [(f'%s'%(khoroo_num+1)) for khoroo_num in range(50)]
    form.khoroo.choices.insert(0,'Хороо сонгох')
    form.aimag.choices = [(aimag) for aimag in aimags]
    form.aimag.choices.insert(0,'Аймаг сонгох')

    todays_order_count = connection.execute('SELECT count(*) FROM sunsundatabase1.delivery as order_table join sunsundatabase1.user as user on order_table.user_id=user.id where DATE(order_table.created_date) = CURDATE() and user.id=:current_user;', {'current_user': current_user.id}).scalar()

    if form.validate_on_submit():
        line_phone = request.form.getlist("phone_value")
        line_phone_more = request.form.getlist("phone_more_value")
        line_district = request.form.getlist("district_value")
        line_khoroo = request.form.getlist("khoroo_value")
        line_address = request.form.getlist("address_value")
        line_total_amount = request.form.getlist("total_amount_value")
        line_aimag = request.form.getlist("aimag_value")
        line_order_type = request.form.getlist("order_type_value")

        pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id).filter(or_(models.PickupTask.status=="waiting", models.PickupTask.status=="enroute")).filter(models.PickupTask.is_completed==False).filter(models.PickupTask.created_date).first()

        if pickup_task:
            pickup_task.supplier_id = current_user.id
            pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            for i, phone in enumerate(line_phone):
                if line_order_type[i] == "true":
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.district = line_district[i]
                    pickup_task_detail.khoroo = line_khoroo[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.destination_type = "local"
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    pickup_task.pickup_details.append(pickup_task_detail)

                elif line_order_type[i] == "false":
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.aimag = line_aimag[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.destination_type = "long"
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    pickup_task.pickup_details.append(pickup_task_detail)

        else:
            pickup_task = models.PickupTask()
            pickup_task.supplier_company = current_user.company_name
            pickup_task.is_ready = True
            pickup_task.is_completed = False
            pickup_task.status = "waiting"
            pickup_task.supplier_type = "supplier2"
            pickup_task.supplier_id = current_user.id
            pickup_task.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            current_user.pickups.append(pickup_task)
        
            for i, phone in enumerate(line_phone):
                if line_order_type[i] == "true":
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.district = line_district[i]
                    pickup_task_detail.khoroo = line_khoroo[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.destination_type = "local"
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    pickup_task.pickup_details.append(pickup_task_detail)

                elif line_order_type[i] == "false":
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.aimag = line_aimag[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.destination_type = "long"
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    pickup_task.pickup_details.append(pickup_task_detail)

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('supplier2_order.supplier2_order_add'))
        else:
            connection.close()
            if is_time_between(time(22,30), time(00,00)):
                flash('Маргаашийн хүргэлтэнд нэмэгдлээ.', 'success')
            else:
                flash('Хүргэлт нэмэгдлээ.', 'success')
                
            return redirect(url_for('supplier2_order.supplier2_orders_ready'))

    return render_template('/supplier/supplier2/order_add.html', form=form, cur_date=cur_date, order_window=order_window, todays_order_count=todays_order_count)


@supplier2_order_blueprint.route('/supplier2/orders/cancel/<int:pickup_task_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_cancel(pickup_task_id):
    connection = Connection()

    task = connection.query(models.PickupTask).get(pickup_task_id)

    if task is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        connection.close()
        return redirect(url_for('supplier2_order.supplier2_orders_ready'))

    if task.status == "completed" or task.status == "pickedup":
        flash('Цуцлах боломжгүй', 'danger')
        connection.close()
        return redirect(url_for('supplier2_order.supplier2_orders_ready'))

    if current_user.id != task.supplier_id:
        abort(403)

    if task:
        try:
            connection.query(models.PickupTask).filter_by(id=task.id).delete()
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('supplier2_order.supplier2_orders_ready'))
        else:
            connection.close()
            return redirect(url_for('supplier2_order.supplier2_orders_ready'))

    return redirect(url_for('supplier2_order.supplier2_orders_ready'))


@supplier2_order_blueprint.route('/supplier2/orders/edit/<int:pickup_task_id>/<int:pickup_task_detail_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_edit(pickup_task_id, pickup_task_detail_id):

    connection = Connection()
    task = connection.query(models.PickupTask).get(pickup_task_id)
    task_detail = connection.query(models.PickupTaskDetail).get(pickup_task_detail_id)

    if task is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        connection.close()
        return redirect(url_for('supplier2_order.supplier2_orders'))

    if task_detail is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        connection.close()
        return redirect(url_for('supplier2_order.supplier2_orders'))

    if current_user.id != task.supplier_id:
        abort(403)

    form = OrderEditForm()

    districts = connection.query(models.District).all()
    aimags = connection.query(models.Aimag).all()
    form.district.choices = [(district) for district in districts]
    form.khoroo.choices = [(f'%s'%(district+1)) for district in range(50)]
    form.aimag.choices = [(district) for district in aimags]

    if form.validate_on_submit():
        
        task_detail.phone = form.phone.data
        task_detail.phone_more = form.phone_more.data

        if task_detail.destination_type == "local":
            task_detail.district = form.district.data
            task_detail.khoroo = form.khoroo.data
        
        if task_detail.destination_type == "long":
            task_detail.aimag = form.aimag.data
        
        task_detail.address = form.address.data
        task_detail.total_amount = form.total_amount.data

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('supplier2_order.supplier2_orders_ready'))
        else:
            flash('Хүргэлт өөрчлөгдлөө', 'info')
            return redirect(url_for('supplier2_order.supplier2_orders_ready'))

    elif request.method == 'GET':
        form.phone.data = task_detail.phone
        form.phone_more.data = task_detail.phone_more
        form.district.data = task_detail.district
        form.khoroo.data = task_detail.khoroo
        form.aimag.data = task_detail.aimag
        form.address.data = task_detail.address
        form.total_amount.data = task_detail.total_amount
        return render_template('/supplier/supplier2/order_edit.html', form=form, task_detail=task_detail)

    return render_template('/supplier/supplier2/order_edit.html', form=form, task_detail=task_detail)



@supplier2_order_blueprint.route('/supplier2/orders/delete/<int:pickup_task_id>/<int:pickup_task_detail_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_delete(pickup_task_id, pickup_task_detail_id):

    connection = Connection()
    task = connection.query(models.PickupTask).get(pickup_task_id)
    task_detail = connection.query(models.PickupTaskDetail).get(pickup_task_detail_id)

    if task is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        connection.close()
        return redirect(url_for('supplier2_order.supplier2_orders_ready'))

    if task_detail is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        connection.close()
        return redirect(url_for('supplier2_order.supplier2_orders_ready'))

    if current_user.id != task.supplier_id:
        abort(403)

    if task.status != "waiting" or task.status != "enroute":
        task.pickup_details.remove(task_detail)
        connection.query(models.PickupTaskDetail).filter_by(id=task_detail.id).delete()

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('supplier2_order.supplier2_orders_ready'))
        else:
            flash('Хүргэлт өөрчлөгдлөө', 'info')
            return redirect(url_for('supplier2_order.supplier2_orders_ready'))

    else:
        return redirect(url_for('supplier2_order.supplier2_orders_ready'))



@supplier2_order_blueprint.route('/supplier2/orders/ready', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_orders_ready():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    form = TransferForm()
    orders = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id).filter(models.PickupTask.is_ready==True).order_by(models.PickupTask.created_date).all()
    
    if form.validate_on_submit():
        line_order_id = request.form.getlist("order_id")

        try:
            for i, order in enumerate(line_order_id):
                pickup_task = connection.query(models.PickupTask).get(order)

                if pickup_task.status == "waiting":
                    continue
                elif pickup_task.status == "enroute":
                    for pickup_task_detail in pickup_task.pickup_details:
                        inventory = models.Inventory()
                        inventory.status = True
                        inventory.quantity = 1
                        inventory.inventory_type = "unstored"
                        inventory.is_received_from_driver = True
                        inventory.driver_name = pickup_task.driver_name
                        inventory.driver_id = pickup_task.driver_id
                        inventory.supplier_id = current_user.id
                        inventory.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                        new_delivery = models.Delivery()
                        new_delivery.status = "unassigned"
                        new_delivery.destination_type = pickup_task_detail.destination_type
                        new_delivery.order_type = "unstored"
                        new_delivery.is_ready = True
                        new_delivery.delivery_attempts = 0
                        new_delivery.supplier_company_name = current_user.company_name
                        new_delivery.total_amount = pickup_task_detail.total_amount

                        if is_time_between(time(22,30), time(00,00)):
                            new_delivery.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) + timedelta(hours=+24)
                            new_delivery.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) + timedelta(hours=+24)
                            new_delivery.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) + timedelta(hours=+24)
                        else:
                            new_delivery.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                            new_delivery.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                            new_delivery.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                        delivery_detail = models.DeliveryDetail()
                        delivery_detail.quantity = 1
                        delivery_detail.phone = pickup_task_detail.phone
                        delivery_detail.phone_more = pickup_task_detail.phone_more
                        delivery_detail.district = pickup_task_detail.district
                        delivery_detail.khoroo = pickup_task_detail.khoroo
                        delivery_detail.aimag = pickup_task_detail.aimag
                        delivery_detail.address = pickup_task_detail.address
                        delivery_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        delivery_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                        delivery_address = models.Address()
                        delivery_address.phone = pickup_task_detail.phone
                        delivery_address.phone_more = pickup_task_detail.phone_more
                        delivery_address.district = pickup_task_detail.district
                        delivery_address.khoroo = pickup_task_detail.khoroo
                        delivery_address.aimag = pickup_task_detail.aimag
                        delivery_address.address = pickup_task_detail.address
                        delivery_address.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        delivery_address.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        
                        new_delivery.delivery_details.append(delivery_detail)
                        new_delivery.addresses = delivery_address
                        current_user.deliveries.append(new_delivery)
                        connection.add(inventory)
                        connection.flush()
                        pickup_task_detail.inventory_id = inventory.id

                    pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task.pickup_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task.status = "pickedup"

                    pickup_history = models.DriverOrderHistory()
                    pickup_history.driver_id = pickup_task.driver_id
                    pickup_history.delivery_status = "pickedup"
                    pickup_history.address = pickup_task.supplier_company
                    pickup_history.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_history.type = "pickup"
                    pickup_history.task_id = pickup_task.id
                    pickup_history.supplier_name = pickup_task.supplier_company

                    connection.add(pickup_history)
                    connection.commit()

        except Exception as e:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(request.url)
        else:
            flash('Жолоочид хүлээлгэж өглөө.', 'success')
            return render_template('/supplier/supplier2/ready_orders.html', orders=orders, cur_date=cur_date, form=form)

    return render_template('/supplier/supplier2/ready_orders.html', orders=orders, cur_date=cur_date, form=form)