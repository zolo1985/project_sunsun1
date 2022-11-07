from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier2.forms import OrderDetailLocalAddForm, OrderDetailLongDistanceAddForm, TransferForm, OrderDetailLocalEditForm, OrderDetailLongEditForm, DateSelectForm
from datetime import datetime, time, timedelta
from sqlalchemy import func
from webapp.utils import is_time_between
import pytz

supplier2_order_blueprint = Blueprint('supplier2_order', __name__)

# orders_count = connection.query(models.Delivery).filter(models.Delivery.delivery_regions.any(models.Region.name=="Хойд")).count()

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

    if form.select_date.data is not None and form.validate_on_submit():
        orders1 = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id).filter(func.date(models.Delivery.created_date) == form.select_date.data).order_by(models.Delivery.created_date).all()
        post_orders = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id).filter(func.date(models.Delivery.postphoned_date) == form.select_date.data).filter(models.Delivery.is_postphoned == True).all()

        for post_order in post_orders:
            if post_order in orders1:
                continue
            else:
                orders1.append(post_order)
        orders = orders1

        return render_template('/supplier/supplier2/orders.html', cur_date=cur_date, orders=orders, form=form)

    return render_template('/supplier/supplier2/orders.html', cur_date=cur_date, orders=orders, form=form)


@supplier2_order_blueprint.route('/supplier2/orders/add/<string:destination>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_add(destination):

    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    order_window = is_time_between(time(16,00), time(20,00))

    if destination == 'local':
        connection = Connection()
        todays_order_count = connection.execute('SELECT count(*) FROM sunsundatabase1.delivery as order_table join sunsundatabase1.user as user on order_table.user_id=user.id where DATE(order_table.created_date) = CURDATE() and user.id=:current_user;', {'current_user': current_user.id}).scalar()
        districts = connection.query(models.District).all()
        payment_types = connection.query(models.PaymentType).all()
        form = OrderDetailLocalAddForm()
        form.district.choices = [(district) for district in districts]
        form.khoroo.choices = [(f'%s хороо'%(district+1)) for district in range(32)]
        form.payment_type.choices = [(payment_type) for payment_type in payment_types]

        if form.validate_on_submit():
            line_phone = request.form.getlist("phone")
            line_phone_more = request.form.getlist("phone_more")
            line_district = request.form.getlist("district")
            line_khoroo = request.form.getlist("khoroo")
            line_address = request.form.getlist("address")
            line_total_amount = request.form.getlist("total_amount")
            line_payment_type = request.form.getlist("payment_type")

            pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id).filter(models.PickupTask.status=="waiting").filter(models.PickupTask.is_completed==False).first()

            if pickup_task:
                pickup_task.supplier_id = current_user.id
                pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                for i, phone in enumerate(line_phone):
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.district = line_district[i]
                    pickup_task_detail.khoroo = line_khoroo[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.payment_type = line_payment_type[i]
                    pickup_task_detail.destination_type = "local"
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    
                    inventory = models.Inventory()
                    inventory.inventory_type = "unstored"
                    inventory.quantity = 1
                    inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    inventory.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

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
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.district = line_district[i]
                    pickup_task_detail.khoroo = line_khoroo[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.payment_type = line_payment_type[i]
                    pickup_task_detail.destination_type = "local"
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    
                    inventory = models.Inventory()
                    inventory.inventory_type = "unstored"
                    inventory.quantity = 1
                    inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    inventory.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    pickup_task.pickup_details.append(pickup_task_detail)

            try:
                connection.commit()
        
            except Exception as ex:
                flash('Алдаа гарлаа!', 'danger')
                connection.rollback()
                connection.close()
                return redirect(request.url)
            else:
                connection.close()
                if is_time_between(time(12,00), time(00,00)):
                    flash('Маргаашийн хүргэлтэнд нэмэгдлээ.', 'success')
                else:
                    flash('Хүргэлт нэмэгдлээ.', 'success')
                    
                return redirect(url_for('supplier2_order.supplier2_orders'))
        return render_template('/supplier/supplier2/order_add.html', form=form, cur_date=cur_date, order_window=order_window, todays_order_count=todays_order_count)

    if destination == 'long':

        connection = Connection()
        todays_order_count = connection.execute('SELECT count(*) FROM sunsundatabase1.delivery as order_table join sunsundatabase1.user as user on order_table.user_id=user.id where user.id=:current_user and DATE(order_table.created_date) = CURDATE();', {'current_user': current_user.id}).scalar()
        form1 = OrderDetailLongDistanceAddForm()
        aimags = connection.query(models.Aimag).all()
        payment_types = connection.query(models.PaymentType).all()
        form1.aimag.choices = [(aimag) for aimag in aimags]
        form1.payment_type.choices = [(payment_type) for payment_type in payment_types]

        if form1.validate_on_submit():
            line_phone = request.form.getlist("phone")
            line_phone_more = request.form.getlist("phone_more")
            line_aimag = request.form.getlist("aimag")
            line_address = request.form.getlist("address")
            line_total_amount = request.form.getlist("total_amount")
            line_payment_type = request.form.getlist("payment_type")

            pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id).filter(models.PickupTask.status=="waiting").filter(models.PickupTask.is_completed==False).first()

            if pickup_task:
                pickup_task.supplier_id = current_user.id
                pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                for i, phone in enumerate(line_phone):
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.aimag = line_aimag[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.payment_type = line_payment_type[i]
                    pickup_task_detail.destination_type = "long"
                    pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    
                    inventory = models.Inventory()
                    inventory.inventory_type = "unstored"
                    inventory.quantity = 1
                    inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    inventory.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

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
                pickup_task_detail = models.PickupTaskDetail()
                pickup_task_detail.phone = phone
                pickup_task_detail.phone_more = line_phone_more[i]
                pickup_task_detail.aimag = line_aimag[i]
                pickup_task_detail.address = line_address[i]
                pickup_task_detail.total_amount = line_total_amount[i]
                pickup_task_detail.payment_type = line_payment_type[i]
                pickup_task_detail.destination_type = "long"
                pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                
                inventory = models.Inventory()
                inventory.inventory_type = "unstored"
                inventory.quantity = 1
                inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                inventory.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                pickup_task.pickup_details.append(pickup_task_detail)

            try:
                connection.commit()

            except Exception:
                flash('Алдаа гарлаа!', 'danger')
                connection.rollback()
                connection.close()
                return redirect(request.url)
            else:
                connection.close()
                if is_time_between(time(12,00), time(00,00)):
                    flash('Маргаашийн Хүргэлтд нэмэгдлээ.', 'success')
                else:
                    flash('Хүргэлт нэмэгдлээ.', 'success')
                    
                return redirect(url_for('supplier2_order.supplier2_orders'))
        return render_template('/supplier/supplier2/order_add_long_distance.html', form=form1, cur_date=cur_date, order_window=order_window, todays_order_count=todays_order_count)


@supplier2_order_blueprint.route('/supplier2/orders/delete/<int:pickup_task_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_delete(pickup_task_id):
    connection = Connection()

    task = connection.query(models.PickupTask).get(pickup_task_id)

    if task is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        connection.close()
        return redirect(url_for('supplier2_order.supplier2_orders'))

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
            return redirect(url_for('supplier2_order.supplier2_orders'))
        else:
            connection.close()
            return redirect(url_for('supplier2_order.supplier2_orders'))

    return redirect(url_for('supplier2_order.supplier2_orders'))


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
                        inventory.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                        new_delivery = models.Delivery()
                        new_delivery.status = "unassigned"
                        new_delivery.destination_type = "local"
                        new_delivery.order_type = "unstored"
                        new_delivery.is_ready = True
                        new_delivery.delivery_attempts = 0
                        new_delivery.supplier_company_name = current_user.company_name

                        order_payment_type = connection.query(models.PaymentType).filter_by(name=pickup_task_detail.payment_type).first()
                        new_delivery.payment_types.append(order_payment_type)

                        if order_payment_type.name == "Үндсэн үнэ":
                            new_delivery.total_amount = int(pickup_task_detail.total_amount) + order_payment_type.amount
                        elif order_payment_type.name == "Хүргэлт орсон":
                            new_delivery.total_amount = int(pickup_task_detail.total_amount)
                        elif order_payment_type.name =="Төлбөр авахгүй":
                            new_delivery.total_amount = 0

                        if is_time_between(time(12,00), time(00,00)):
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

                        new_delivery.delivery_details.append(delivery_detail)
                        new_delivery.addresses = delivery_address
                        current_user.deliveries.append(new_delivery)
                        connection.add(inventory)
                        connection.commit()
                        pickup_task_detail.inventory_id = inventory.id
                        connection.commit()

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

                    connection.add(pickup_history)
                    connection.commit()

        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(request.url)
        else:
            flash('Жолоочид хүлээлгэж өглөө.', 'success')
            return render_template('/supplier/supplier2/ready_orders.html', orders=orders, cur_date=cur_date, form=form)

    return render_template('/supplier/supplier2/ready_orders.html', orders=orders, cur_date=cur_date, form=form)