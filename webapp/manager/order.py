from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import FilterOrderByDistrict, FiltersForm, OrderEditForm, AssignRegionAndDriverForm, DriversSelect, DriversHistoriesForm, FilterDateForm, EditCommentForm, EditAddressForm, EditTotalAmountForm, ShowCommentStatusForm, OrderAddForm, OrderDetailEditForm, SelectDriverForm, UnassignForm
from datetime import datetime
from sqlalchemy import func, or_
import pytz

manager_order_blueprint = Blueprint('manager_order', __name__)

initial_delivery_status = ['Хувиарласан', 'Одоо хүргэгдэж байгаа', 'Хүргэсэн', 'Цуцалсан', 'Хойшилсон', 'Хувиарлагдаагүй']
order_edit_order_status = ['Хувиарласан', 'Хувиарлагдаагүй']

def switch_status(status):
    if status == "Хувиарласан":
        return "assigned"
    elif status == "Одоо хүргэгдэж байгаа":
        return "started"
    elif status == "Хүргэсэн":
        return "completed"
    elif status == "Цуцалсан":
        return "cancelled"
    elif status == "Хойшилсон":
        return "postphoned"
    elif status == "Хувиарлагдаагүй":
        return "unassigned"

@manager_order_blueprint.route('/manager/orders', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_orders():
    
    connection = Connection()
    delivery_regions = connection.query(models.Region).all()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    
    orders1 = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.created_date) == cur_date.date()).order_by(models.Address.district).all()
    post_orders = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.postphoned_date) == cur_date.date()).filter(models.Delivery.is_postphoned == True).order_by(models.Address.district).all()

    for post_order in post_orders:
        if post_order in orders1:
            continue
        else:
            orders1.append(post_order)
    orders = orders1

    total_orders_count_by_district = connection.execute('SELECT count(address.district) as total_count, address.district FROM sunsundatabase1.delivery as delivery join sunsundatabase1.address address on delivery.id=address.delivery_id WHERE DATE(delivery.created_date) = CURDATE() group by address.district HAVING count(address.district) > 0 order by address.district;').all()
    total_orders_count_by_driver = connection.execute('SELECT count(delivery.assigned_driver_name) as total_count, delivery.assigned_driver_name as driver FROM sunsundatabase1.delivery as delivery WHERE DATE(delivery.created_date) = CURDATE() group by delivery.assigned_driver_name HAVING count(delivery.assigned_driver_name) > 0;').all()
    total_postphoned_count_by_driver = connection.execute('SELECT count(delivery.postphoned_driver_name) as total_count, delivery.postphoned_driver_name as driver FROM sunsundatabase1.delivery as delivery WHERE DATE(delivery.created_date) = CURDATE() group by delivery.postphoned_driver_name HAVING count(delivery.postphoned_driver_name) > 0;').all()
    total_postphoned_count_by_driver_from_previous_days = connection.execute('SELECT count(delivery.postphoned_driver_name) as total_count, delivery.postphoned_driver_name as driver FROM sunsundatabase1.delivery as delivery WHERE DATE(delivery.postphoned_date) = CURDATE() group by delivery.postphoned_driver_name HAVING count(delivery.postphoned_driver_name) > 0;').all()
    total_orders_count_by_aimag = connection.execute('SELECT count(address.aimag) as total_count, address.aimag FROM sunsundatabase1.delivery as delivery join sunsundatabase1.address address on delivery.id=address.delivery_id WHERE DATE(delivery.created_date) = CURDATE() group by address.aimag HAVING count(address.aimag) > 0 order by address.aimag;').all()

    total_orders = connection.execute('SELECT count(*) as total_orders FROM sunsundatabase1.delivery as delivery where date(delivery.created_date)=curdate() or date(delivery.postphoned_date)=curdate();').scalar()
    unassigned_orders = connection.execute('SELECT (SELECT count(*) as unassigned_orders FROM sunsundatabase1.delivery as delivery where date(delivery.created_date)=curdate() and delivery.status="unassigned" and delivery.is_postphoned=false)+(SELECT count(*) as unassigned_orders FROM sunsundatabase1.delivery as delivery where date(delivery.delivery_date)=curdate() and delivery.status="unassigned" and delivery.is_postphoned=true) AS unassigned_orders;').scalar()
    delivered_orders = connection.execute('SELECT count(*) as delivered_orders FROM sunsundatabase1.delivery as delivery where (date(delivery.created_date)=curdate() or date(delivery.postphoned_date)=date(curdate())) and delivery.status="completed" and delivery.is_delivered=true;').scalar()
    postphoned_orders = connection.execute('SELECT count(*) as postphoned_orders FROM sunsundatabase1.delivery as delivery where date(delivery.created_date)=curdate() and delivery.status="unassigned" and delivery.is_postphoned=true;').scalar()
    cancelled_orders = connection.execute('SELECT (SELECT count(*) as cancelled_orders FROM sunsundatabase1.delivery as delivery where date(delivery.created_date)=curdate() and delivery.status="cancelled" and delivery.is_cancelled=true)+(SELECT count(*) as cancelled_orders FROM sunsundatabase1.delivery as delivery where date(delivery.delivered_date)=curdate() and delivery.status="cancelled" and delivery.is_cancelled=true and delivery.is_postphoned=true) AS cancelled_orders').scalar()

    form = FiltersForm()
    form.regions.choices = [(region) for region in delivery_regions]
    form.regions.choices.insert(0,'Бүс сонгох')
    form.status.choices = [(status) for status in initial_delivery_status]
    form.status.choices.insert(0,'Төлөв сонгох')

    if form.validate_on_submit():
  
        if form.status.data != 'Төлөв сонгох' and form.date.data is None and form.regions.data == 'Бүс сонгох':
            if switch_status(form.status.data)=="postphoned":
                orders1 = connection.query(models.Delivery).filter(models.Delivery.status == "unassigned").filter(models.Delivery.is_postphoned==True).filter(func.date(models.Delivery.created_date) == cur_date.date()).all()
                orders = orders1
            elif switch_status(form.status.data)=="unassigned":
                orders1 = connection.query(models.Delivery).filter(models.Delivery.status == "unassigned").filter(models.Delivery.is_postphoned==False).filter(func.date(models.Delivery.created_date) == cur_date.date()).all()
                orders = orders1
            else:
                orders1 = connection.query(models.Delivery).filter(models.Delivery.status == switch_status(form.status.data)).filter(func.date(models.Delivery.created_date) == cur_date.date()).all()
                orders = orders1

        elif form.status.data != 'Төлөв сонгох' and form.date.data is not None and form.regions.data == 'Бүс сонгох':
            orders1 = connection.query(models.Delivery).filter(func.date(models.Delivery.created_date) == form.date.data).filter(models.Delivery.status == switch_status(form.status.data)).all()
            post_orders = connection.query(models.Delivery).filter(func.date(models.Delivery.postphoned_date) == form.date.data).filter(models.Delivery.is_postphoned == True).all()

            for post_order in post_orders:
                if post_order in orders1:
                    continue
                else:
                    orders1.append(post_order)
            orders = orders1

        elif form.status.data != 'Төлөв сонгох' and form.date.data is None and form.regions.data != 'Бүс сонгох':
            orders1 = connection.query(models.Delivery).filter(models.Delivery.delivery_region == form.regions.data).filter(func.date(models.Delivery.created_date) == cur_date.date()).filter(models.Delivery.status == switch_status(form.status.data)).all()
            orders = orders1

        elif form.status.data == 'Төлөв сонгох' and form.date.data is None and form.regions.data != 'Бүс сонгох':
            orders1 = connection.query(models.Delivery).filter(models.Delivery.delivery_region == form.regions.data).filter(func.date(models.Delivery.created_date) == cur_date.date()).all()
            orders = orders1

        elif form.status.data == 'Төлөв сонгох' and form.date.data is not None and form.regions.data == 'Бүс сонгох':
            orders1 = connection.query(models.Delivery).filter(func.date(models.Delivery.created_date) == form.date.data).all()
            post_orders = connection.query(models.Delivery).filter(func.date(models.Delivery.postphoned_date) == form.date.data).filter(models.Delivery.is_postphoned == True).all()

            for post_order in post_orders:
                if post_order in orders1:
                    continue
                else:
                    orders1.append(post_order)
            orders = orders1

        elif form.status.data == 'Төлөв сонгох' and form.date.data is not None and form.regions.data != 'Бүс сонгох':
            orders1 = connection.query(models.Delivery).filter(func.date(models.Delivery.created_date) == form.date.data).all()
            post_orders = connection.query(models.Delivery).filter(func.date(models.Delivery.postphoned_date) == form.date.data).filter(models.Delivery.is_postphoned == True).all()

            for post_order in post_orders:
                if post_order in orders1:
                    continue
                else:
                    orders1.append(post_order)
            orders = orders1
        
        elif form.status.data != 'Төлөв сонгох' and form.date.data is not None and form.regions.data != 'Бүс сонгох':
            orders1 = connection.query(models.Delivery).filter(func.date(models.Delivery.created_date) == form.date.data).filter(models.Delivery.delivery_region == form.regions.data).filter(models.Delivery.status == switch_status(form.status.data)).all()
            post_orders = connection.query(models.Delivery).filter(func.date(models.Delivery.postphoned_date) == form.date.data).filter(models.Delivery.is_postphoned == True).all()

            for post_order in post_orders:
                if post_order in orders1:
                    continue
                else:
                    orders1.append(post_order)
            orders = orders1

        else:
            return redirect(url_for('manager_order.manager_orders'))

    return render_template('/manager/orders.html', orders=orders, form=form, total_orders_count_by_district=total_orders_count_by_district, total_orders_count_by_driver=total_orders_count_by_driver, total_orders_count_by_aimag=total_orders_count_by_aimag, total_postphoned_count_by_driver=total_postphoned_count_by_driver, total_postphoned_count_by_driver_from_previous_days=total_postphoned_count_by_driver_from_previous_days, cur_date=cur_date, unassigned_orders=unassigned_orders, total_orders=total_orders, delivered_orders=delivered_orders, postphoned_orders=postphoned_orders, cancelled_orders=cancelled_orders)



@manager_order_blueprint.route('/manager/orders/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_detail(order_id):

    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    delivery_regions = connection.query(models.Region).all()
    form = OrderEditForm()

    form.select_drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    form.select_regions.choices = [(delivery_region.id, f'%s'%(delivery_region.name)) for delivery_region in delivery_regions]
    form.select_regions.choices.insert(0,(0,'Бүс сонгох'))
    order = connection.query(models.Delivery).filter_by(id=order_id).first()

    if order is None:
        flash('Хүргэлт олдсонгүй', 'danger')
        return redirect(url_for('manager_order.manager_orders_drivers_histories'))

    if form.validate_on_submit():

        if form.date.data is not None and form.select_regions.data == "0" and form.select_drivers.data == "0":
            if order.is_received_from_clerk == True:
                flash('Жолооч ачааг нярваас авсан байна. Жолооч ачааг няравт буцааж өгөөгүй бол өөрчлөх боломжгүй байна', 'info')
                return redirect(url_for('manager_order.manager_orders'))
            else:
                try:
                    order.assigned_manager_id = current_user.id
                    if order.status == "unassigned":
                        order.assigned_driver_id = None
                        order.assigned_driver_name = None
                        order.delivery_region = None
                    order.delivery_date = form.date.data
                    order.created_date = form.date.data
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа1', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_orders'))
                else:
                    flash('Хүргэлт шинэчлэгдлээ', 'success')
                    return redirect(url_for('manager_order.manager_orders'))

        elif form.date.data is not None and form.select_regions.data != "0" and form.select_drivers.data == "0":
            if order.is_received_from_clerk == True:
                flash('Жолооч ачааг нярваас авсан байна. Жолооч ачааг няравт буцааж өгөөгүй бол өөрчлөх боломжгүй байна', 'info')
                return redirect(url_for('manager_order.manager_orders'))
            else:
                try:
                    region = connection.query(models.Region).get(form.select_regions.data)
                    order.assigned_manager_id = current_user.id
                    order.assigned_driver_id = None
                    order.assigned_driver_name = None
                    order.delivery_date = form.date.data
                    order.created_date = form.date.data
                    order.delivery_region = region.name
                    order.delivery_regions.clear()
                    order.delivery_regions.append(region)
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа2', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_orders'))
                else:
                    flash('Хүргэлт шинэчлэгдлээ', 'success')
                    return redirect(url_for('manager_order.manager_orders'))
        elif form.date.data is not None and form.select_regions.data != "0" and form.select_drivers.data != "0":
            if order.is_received_from_clerk == True:
                flash('Жолооч ачааг нярваас авсан байна. Жолооч ачааг няравт буцааж өгөөгүй бол өөрчлөх боломжгүй байна', 'info')
                return redirect(url_for('manager_order.manager_orders'))
            else:
                try:
                    driver_name = connection.query(models.User).get(form.select_drivers.data)
                    region = connection.query(models.Region).get(form.select_regions.data)
                    order.assigned_manager_id = current_user.id
                    order.assigned_driver_id = form.select_drivers.data
                    order.assigned_driver_name = f'%s %s'%(driver_name.lastname, driver_name.firstname)
                    order.delivery_date = form.date.data
                    order.created_date = form.date.data
                    order.delivery_region = region.name
                    order.delivery_regions.clear()
                    order.delivery_regions.append(region)
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа31', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_orders'))
                else:
                    flash('Хүргэлт шинэчлэгдлээ', 'success')
                    return redirect(url_for('manager_order.manager_orders'))

        elif form.date.data is None and form.select_regions.data != "0" and form.select_drivers.data != "0":
            if order.is_received_from_clerk == True:
                flash('Жолооч ачааг нярваас авсан байна. Жолооч ачааг няравт буцааж өгөөгүй бол өөрчлөх боломжгүй байна', 'info')
                return redirect(url_for('manager_order.manager_orders'))
            else:
                try:
                    driver_name = connection.query(models.User).get(form.select_drivers.data)
                    region = connection.query(models.Region).get(form.select_regions.data)
                    if order.status == "unassigned":
                        order.status = "assigned"
                    order.assigned_manager_id = current_user.id
                    order.assigned_driver_id = form.select_drivers.data
                    order.assigned_driver_name = f'%s %s'%(driver_name.lastname, driver_name.firstname)
                    order.delivery_region = region.name
                    order.delivery_regions.clear()
                    order.delivery_regions.append(region)
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа4', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_orders'))
                else:
                    flash('Хүргэлт шинэчлэгдлээ', 'success')
                    return redirect(url_for('manager_order.manager_orders'))

        elif form.date.data is None and form.select_regions.data == "0" and form.select_drivers.data != "0":
            if order.is_received_from_clerk == True:
                flash('Жолооч ачааг нярваас авсан байна. Жолооч ачааг няравт буцааж өгөөгүй бол өөрчлөх боломжгүй байна', 'info')
                return redirect(url_for('manager_order.manager_orders'))
            else:
                try:
                    driver_name = connection.query(models.User).get(form.select_drivers.data)
                    region = connection.query(models.Region).get(form.select_regions.data)
                    order.assigned_manager_id = current_user.id
                    order.assigned_driver_id = form.select_drivers.data
                    order.assigned_driver_name = f'%s %s'%(driver_name.lastname, driver_name.firstname)
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа5', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_orders'))
                else:
                    flash('Хүргэлт шинэчлэгдлээ', 'success')
                    return redirect(url_for('manager_order.manager_orders'))

        elif form.date.data is None and form.select_regions.data != "0" and form.select_drivers.data == "0":
            if order.is_received_from_clerk == True:
                flash('Жолооч ачааг нярваас авсан байна. Жолооч ачааг няравт буцааж өгөөгүй бол өөрчлөх боломжгүй байна', 'info')
                return redirect(url_for('manager_order.manager_orders'))
            else:
                try:
                    region = connection.query(models.Region).get(form.select_regions.data)
                    order.assigned_manager_id = current_user.id
                    order.delivery_region = region.name
                    order.delivery_regions.clear()
                    order.delivery_regions.append(region)
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа6', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_orders'))
                else:
                    flash('Хүргэлт шинэчлэгдлээ', 'success')
                    return redirect(url_for('manager_order.manager_orders'))

        elif form.date.data is None and form.select_regions.data == "0" and form.select_drivers.data == "0":
            if order.is_received_from_clerk == True:
                flash('Жолооч ачааг нярваас авсан байна. Жолооч ачааг няравт буцааж өгөөгүй бол өөрчлөх боломжгүй байна', 'info')
                return redirect(url_for('manager_order.manager_orders'))
            else:
                try:
                    region = connection.query(models.Region).get(form.select_regions.data)
                    order.assigned_manager_id = None
                    order.delivery_region = None
                    order.assigned_driver_id = None
                    order.assigned_driver_name = None
                    order.delivery_regions.clear()
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа6', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_orders'))
                else:
                    flash('Хүргэлт шинэчлэгдлээ', 'success')
                    return redirect(url_for('manager_order.manager_orders'))

    return render_template('/manager/order.html', order=order, form=form)



@manager_order_blueprint.route('/manager/orders/region', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_assign_region():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    connection = Connection()
    delivery_regions = connection.query(models.Region).all()
    districts = connection.query(models.District).all()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    orders1 = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == cur_date.date()).filter(models.Delivery.status == "unassigned").filter(models.Delivery.destination_type == "local").filter(models.Delivery.is_ready==True).order_by(models.Address.district).all()
    long_destination_orders = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == cur_date.date()).filter(models.Delivery.status == "unassigned").filter(models.Delivery.destination_type == "long").filter(models.Delivery.destination_type == "long").filter(models.Delivery.is_ready==True).order_by(models.Address.aimag).all()
    orders = orders1 + long_destination_orders

    total_orders_count_by_district = connection.execute('SELECT count(address.district) as total_count, address.district FROM sunsundatabase1.delivery as order_t join sunsundatabase1.address address on order_t.id=address.delivery_id WHERE DATE(order_t.created_date) = CURDATE() and order_t.is_postphoned=false and order_t.is_cancelled=false and order_t.assigned_driver_name is null group by address.district HAVING count(address.district) > 0 order by address.district;')
    total_orders_count_by_driver = connection.execute('SELECT count(order_t.assigned_driver_name) as total_count, order_t.assigned_driver_name as driver FROM sunsundatabase1.delivery as order_t WHERE  DATE(order_t.created_date) = CURDATE() group by order_t.assigned_driver_name HAVING count(order_t.assigned_driver_name) > 0;')
    total_postphoned_count_by_driver = connection.execute('SELECT count(delivery.postphoned_driver_name) as total_count, delivery.postphoned_driver_name as driver FROM sunsundatabase1.delivery as delivery WHERE DATE(delivery.created_date) = CURDATE() group by delivery.postphoned_driver_name HAVING count(delivery.postphoned_driver_name) > 0;')
    total_postphoned_count_by_driver_from_previous_days = connection.execute('SELECT count(delivery.postphoned_driver_name) as total_count, delivery.postphoned_driver_name as driver FROM sunsundatabase1.delivery as delivery WHERE DATE(delivery.postphoned_date) = CURDATE() group by delivery.postphoned_driver_name HAVING count(delivery.postphoned_driver_name) > 0;')
    total_orders_count_by_aimag = connection.execute('SELECT count(address.aimag) as total_count, address.aimag FROM sunsundatabase1.delivery as order_t join sunsundatabase1.address address on order_t.id=address.delivery_id WHERE DATE(order_t.created_date) = CURDATE() and order_t.assigned_driver_name is null group by address.aimag HAVING count(address.aimag) > 0 order by address.aimag;')
    
    form = AssignRegionAndDriverForm()
    form.select_regions.choices = [(delivery_region) for delivery_region in delivery_regions]
    form.select_drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    
    form1 = FilterOrderByDistrict()
    form1.district_names.choices = [(district) for district in districts]
    form1.district_names.choices.insert(0,'Дүүрэг сонгох')
    form1.khoroo_names.choices = [(f'%s'%(district+1)) for district in range(32)]
    form1.khoroo_names.choices.insert(0,'Хороо сонгох')

    if form1.validate():
        if form1.district_names.data != 'Дүүрэг сонгох' and form1.khoroo_names.data == 'Хороо сонгох':
            orders1 = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == cur_date.date()).filter(models.Delivery.status == "unassigned").filter(models.Address.district==form1.district_names.data).filter(models.Delivery.is_ready==True).order_by(models.Address.district).all()
            orders = orders1
            return render_template('/manager/assign_regions_and_drivers.html', orders=orders, total_orders_count_by_district=total_orders_count_by_district, form=form, form1=form1, cur_date=cur_date.date())
        elif form1.district_names.data != 'Дүүрэг сонгох' and form1.khoroo_names.data != 'Хороо сонгох':
            orders1 = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == cur_date.date()).filter(models.Delivery.status == "unassigned").filter(models.Address.district==form1.district_names.data).filter(models.Address.khoroo==str(form1.khoroo_names.data)).filter(models.Delivery.is_ready==True).order_by(models.Address.district).all()
            orders = orders1
            return render_template('/manager/assign_regions_and_drivers.html', orders=orders, total_orders_count_by_district=total_orders_count_by_district, form=form, form1=form1, cur_date=cur_date.date())
        else:
            return redirect(url_for('manager_order.manager_order_assign_region'))

    if form.validate_on_submit():
        line_order_id = request.form.getlist("order_id")
        line_order_id_values = request.form.getlist("order_id_value")

        if form.select_drivers.data == "0":

            selected_region = connection.query(models.Region).filter_by(name=form.select_regions.data).first()

            if len(line_order_id) <= 0:
                    return redirect(url_for('manager_order.manager_order_assign_region'))

            if len(line_order_id_values) > 0:
                for i, order_id in enumerate(line_order_id_values):
                    order = connection.query(models.Delivery).get(order_id)
                    order.delivery_region = form.select_regions.data
                    order.assigned_manager_id = current_user.id
                    order.status = "unassigned"
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    order.delivery_regions.append(selected_region)

                try:
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_order_assign_region'))
                else:
                    connection.close()
                    flash('Бүсчлэгдлээ.', 'success')    
                    return redirect(url_for('manager_order.manager_order_assign_region'))

            else: 
                for i, order_id in enumerate(line_order_id):
                    order = connection.query(models.Delivery).get(order_id)
                    order.delivery_region = form.select_regions.data
                    order.assigned_manager_id = current_user.id
                    order.status = "unassigned"
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    order.delivery_regions.append(selected_region)

                try:
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_order_assign_region'))
                else:
                    connection.close()
                    flash('Бүсчлэгдлээ.', 'success')    
                    return redirect(url_for('manager_order.manager_order_assign_region'))

        elif form.select_drivers.data != "0":

            selected_region = connection.query(models.Region).filter_by(name=form.select_regions.data).first()

            if len(line_order_id) <= 0:
                return redirect(url_for('manager_order.manager_order_assign_region'))

            if len(line_order_id_values) > 0:
                for i, order_id in enumerate(line_order_id_values):
                    driver_name = connection.query(models.User).get(form.select_drivers.data)
                    order = connection.query(models.Delivery).get(order_id)
                    order.delivery_region = form.select_regions.data
                    order.assigned_manager_id = current_user.id
                    order.assigned_driver_name = f'%s %s'%(driver_name.lastname, driver_name.firstname)
                    order.assigned_driver_id = form.select_drivers.data
                    order.status = "assigned"
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    order.delivery_attempts = 0
                    order.delivery_regions.append(selected_region)

                try:
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа2', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_order_assign_region'))
                else:
                    connection.close()
                    flash('Бүс, жолооч хувиарлагдлаа.', 'success')    
                    return redirect(url_for('manager_order.manager_order_assign_region'))

            else:
                for i, order_id in enumerate(line_order_id):
                    driver_name = connection.query(models.User).get(form.select_drivers.data)
                    order = connection.query(models.Delivery).get(order_id)
                    order.delivery_region = form.select_regions.data
                    order.assigned_manager_id = current_user.id
                    order.assigned_driver_name = f'%s %s'%(driver_name.lastname, driver_name.firstname)
                    order.assigned_driver_id = form.select_drivers.data
                    order.status = "assigned"
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    order.delivery_attempts = 0
                    order.delivery_regions.append(selected_region)

                try:
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа2', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_order_assign_region'))
                else:
                    connection.close()
                    flash('Бүс, жолооч хувиарлагдлаа.', 'success')    
                    return redirect(url_for('manager_order.manager_order_assign_region'))

    return render_template('/manager/assign_regions_and_drivers.html', orders=orders, total_orders_count_by_district=total_orders_count_by_district, form=form, form1=form1, total_orders_count_by_driver=total_orders_count_by_driver, total_postphoned_count_by_driver=total_postphoned_count_by_driver, total_postphoned_count_by_driver_from_previous_days=total_postphoned_count_by_driver_from_previous_days, total_orders_count_by_aimag=total_orders_count_by_aimag, cur_date=cur_date.date())



@manager_order_blueprint.route('/manager/orders/drivers', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_orders_drivers():

    connection = Connection()
    cur_date1 = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    form = DriversSelect()
    
    form.select_drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    orders = []

    if form.validate_on_submit() and form.select_drivers.data != "0":
        user = connection.query(models.User).filter_by(id=form.select_drivers.data).first()
        order_ids = user.current_orders_list

        for i, order_id in enumerate(order_ids):
            order = connection.query(models.Delivery).filter(models.Delivery.id==order_id).first()

            if order:
                orders.append(order)

    return render_template('/manager/driver_current_orders.html', form=form, orders=orders, cur_date1=cur_date1)


@manager_order_blueprint.route('/manager/orders/drivers/histories', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_orders_drivers_histories():

    connection = Connection()
    cur_date1 = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    form = DriversHistoriesForm()
    
    form.select_drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    orders = []

    if form.validate_on_submit() and form.select_drivers.data != "0" and form.date.data is not None:
        orders = connection.query(models.DriverOrderHistory).filter(func.date(models.DriverOrderHistory.delivery_date) == form.date.data).filter(models.DriverOrderHistory.driver_id==form.select_drivers.data).all()
        return render_template('/manager/drivers_orders_histories.html', form=form, orders=orders, cur_date1=cur_date1)

    return render_template('/manager/drivers_orders_histories.html', form=form, orders=orders, cur_date1=cur_date1)



@manager_order_blueprint.route('/manager/commented/orders', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_commented_orders():

    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    orders = connection.query(models.Delivery).filter(func.date(models.Delivery.delivered_date) == cur_date.date(), models.Delivery.driver_comment!=None, models.Delivery.show_comment==False).all()

    form = FilterDateForm()
    form1 = ShowCommentStatusForm()

    if form.validate_on_submit() and form.date.data is not None:
        orders = connection.query(models.Delivery).filter(func.date(models.Delivery.delivered_date) == form.date.data, models.Delivery.driver_comment!=None).all()
        return render_template('/manager/orders_comments.html', form=form, orders=orders, cur_date=cur_date, form1=form1)

    if form1.validate_on_submit():
        orders = connection.query(models.Delivery).filter(models.Delivery.show_status==False).all()

        for order in orders:
            order.show_status = True
            order.show_comment = True

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_order.manager_commented_orders'))
        else:
            connection.close()
            flash('Бүх хүргэлтйин төлөв, комментууд харилцагчид харагддаг боллоо.', 'success')    
            return redirect(url_for('manager_order.manager_commented_orders'))

    return render_template('/manager/orders_comments.html', form=form, orders=orders, cur_date=cur_date, form1=form1)



@manager_order_blueprint.route('/manager/order/comment/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_comment(order_id):

    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    order = connection.query(models.Delivery).get(order_id)

    if order is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('manager_order.manager_commented_orders'))

    form = EditCommentForm()

    if form.validate_on_submit():
        comment_to_update = connection.query(models.Delivery).filter(models.Delivery.id==order.id).first()
        comment_to_update.driver_comment = form.comment.data
        comment_to_update.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_order.manager_commented_orders'))
        else:
            connection.close()
            flash('Коммент өөрчлөгдлөө', 'success')    
            return redirect(url_for('manager_order.manager_commented_orders'))

    elif request.method == 'GET':
        form.comment.data = order.driver_comment
        return render_template('/manager/edit_comment.html', form=form, order=order, cur_date=cur_date)

    return render_template('/manager/edit_comment.html', form=form, order=order, cur_date=cur_date)



@manager_order_blueprint.route('/manager/order/address/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_address(order_id):

    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    order = connection.query(models.Delivery).get(order_id)

    if order is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('manager_order.manager_commented_orders'))

    form = EditAddressForm()

    if form.validate_on_submit():
        comment_to_update = connection.query(models.Delivery).filter(models.Delivery.id==order.id).first()
        comment_to_update.addresses.address = form.address.data
        comment_to_update.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_order.manager_commented_orders'))
        else:
            connection.close()
            flash('Коммент өөрчлөгдлөө', 'success')    
            return redirect(url_for('manager_order.manager_commented_orders'))

    elif request.method == 'GET':
        form.address.data = order.addresses.address
        return render_template('/manager/edit_address.html', form=form, order=order, cur_date=cur_date)

    return render_template('/manager/edit_address.html', form=form, order=order, cur_date=cur_date)



@manager_order_blueprint.route('/manager/order/total-amount/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_total_amount(order_id):

    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    order = connection.query(models.Delivery).get(order_id)

    if order is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('manager_order.manager_commented_orders'))

    form = EditTotalAmountForm()

    if form.validate_on_submit():
        comment_to_update = connection.query(models.Delivery).filter(models.Delivery.id==order.id).first()
        comment_to_update.total_amount = form.total_amount.data
        comment_to_update.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_order.manager_orders_edit', order_id=order.id))
        else:
            connection.close()
            flash('Коммент өөрчлөгдлөө', 'success')    
            return redirect(url_for('manager_order.manager_orders_edit', order_id=order.id))

    elif request.method == 'GET':
        form.total_amount.data = order.total_amount
        return render_template('/manager/edit_total_amount.html', form=form, order=order, cur_date=cur_date)

    return render_template('/manager/edit_total_amount.html', form=form, order=order, cur_date=cur_date)



@manager_order_blueprint.route('/manager/orders/add', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_add():
    connection = Connection()
    districts = connection.query(models.District).all()
    suppliers = connection.query(models.User).filter(or_(models.User.roles.any(models.Role.name=="supplier1"), models.User.roles.any(models.Role.name=="supplier2"))).all()
    aimags = connection.query(models.Aimag).all()

    form = OrderAddForm()

    form.suppliers.choices = [(supplier.id, supplier.company_name) for supplier in suppliers]
    form.suppliers.choices.insert(0, (0,'Харилцагч сонгох'))
    form.district.choices = [(district) for district in districts]
    form.district.choices.insert(0,'Дүүрэг сонгох')
    form.khoroo.choices = [(f'%s'%(district+1)) for district in range(32)]
    form.khoroo.choices.insert(0,'Хороо сонгох')
    form.aimag.choices = [(aimag) for aimag in aimags]
    form.aimag.choices.insert(0,'Аймаг сонгох')

    if form.validate_on_submit():
        line_suppliers = request.form.getlist("supplier")
        line_products = request.form.getlist("product")
        line_quantities = request.form.getlist("quantity")

        if form.delivery_type.data == "0" and form.order_type.data == "0":
            # local delivery
            supplier = connection.query(models.User).filter(models.User.id==line_suppliers[0]).first()

            order = models.Delivery()
            order.status = "unassigned"
            order.destination_type = "local"
            order.order_type = "stored"
            order.is_ready = True
            order.is_manager_created = True
            order.delivery_attempts = 0
            order.total_amount = form.total_amount.data
            
            order.supplier_company_name = supplier.company_name
            order.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            supplier.deliveries.append(order)
            connection.flush()

            address = models.Address()
            address.phone = form.phone.data
            address.phone_more = form.phone_more.data
            address.district = form.district.data
            address.khoroo = form.khoroo.data
            address.address = form.address.data
            address.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            address.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            order.addresses = address

            for i, product in enumerate(line_products):
                order_detail = models.DeliveryDetail()
                order_detail.quantity = int(line_quantities[i])
                order_detail.product_id = int(line_products[i])
                order_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                order_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                total_inventory_product = connection.query(models.TotalInventory).filter_by(product_id=int(line_products[i])).first()
                total_inventory_product.quantity = total_inventory_product.quantity-int(line_quantities[i])
                total_inventory_product.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                is_detail = connection.query(models.DeliveryDetail).filter(models.DeliveryDetail.delivery_id==order.id, models.DeliveryDetail.product_id==int(line_products[i])).first()

                if is_detail:
                    is_detail.quantity = is_detail.quantity + int(line_quantities[i])
                else:
                    order.delivery_details.append(order_detail)
                    connection.flush()

            try:
                connection.commit()
            except:
                flash('Алдаа гарлаа!', 'danger')
                connection.rollback()
                return redirect(url_for('manager_order.manager_order_add'))
            else:
                flash('Хүргэлт нэмэгдлээ.', 'success')
                return redirect(url_for('manager_order.manager_order_add'))

        elif form.delivery_type.data == "0" and form.order_type.data == "1":
            # long delivery
            supplier = connection.query(models.User).filter(models.User.id==line_suppliers[0]).first()

            order = models.Delivery()
            order.status = "unassigned"
            order.destination_type = "long"
            order.order_type = "stored"
            order.is_ready = True
            order.is_manager_created = True
            order.delivery_attempts = 0
            order.total_amount = form.total_amount.data
            
            order.supplier_company_name = supplier.company_name
            order.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            supplier.deliveries.append(order)
            connection.flush()

            address = models.Address()
            address.phone = form.phone.data
            address.phone_more = form.phone_more.data
            address.aimag = form.aimag.data
            address.address = form.address.data
            address.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            address.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            order.addresses = address

            for i, product in enumerate(line_products):
                order_detail = models.DeliveryDetail()
                order_detail.quantity = int(line_quantities[i])
                order_detail.product_id = int(line_products[i])
                order_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                order_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                total_inventory_product = connection.query(models.TotalInventory).filter_by(product_id=int(line_products[i])).first()
                total_inventory_product.quantity = total_inventory_product.quantity-int(line_quantities[i])
                total_inventory_product.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                is_detail = connection.query(models.DeliveryDetail).filter(models.DeliveryDetail.delivery_id==order.id, models.DeliveryDetail.product_id==int(line_products[i])).first()

                if is_detail:
                    is_detail.quantity = is_detail.quantity + int(line_quantities[i])
                else:
                    order.delivery_details.append(order_detail)
                    connection.flush()

            try:
                connection.commit()
            except:
                flash('Алдаа гарлаа!', 'danger')
                connection.rollback()
                return redirect(url_for('manager_order.manager_order_add'))
            else:
                flash('Хүргэлт нэмэгдлээ.', 'success')
                return redirect(url_for('manager_order.manager_order_add'))

        elif form.delivery_type.data == "1":
            # warehouse
            supplier = connection.query(models.User).filter(models.User.id==line_suppliers[0]).first()

            order = models.Delivery()
            order.status = "completed"
            order.destination_type = "local"
            order.order_type = "stored"
            order.is_ready = False
            order.is_manager_created = True
            order.is_warehouse_pickup = True
            order.delivery_attempts = 0
            order.driver_comment = request.form.get("commentInput")
            order.assigned_driver_id = current_user.id
            order.assigned_driver_name = f'%s %s'%(current_user.lastname, current_user.firstname)
            order.assigned_manager_id = current_user.id
            order.delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.delivery_region = "Зүүн"
            
            order.supplier_company_name = supplier.company_name
            order.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            supplier.deliveries.append(order)
            connection.flush()

            address = models.Address()
            address.phone = form.phone.data
            address.phone_more = form.phone_more.data
            address.district = form.district.data
            address.khoroo = form.khoroo.data
            address.address = form.address.data
            address.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            address.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            order.addresses = address

            for i, product in enumerate(line_products):
                order_detail = models.DeliveryDetail()
                order_detail.quantity = int(line_quantities[i])
                order_detail.product_id = int(line_products[i])
                order_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                order_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                product_price = connection.query(models.Product.price).filter(models.Product.id==int(line_products[i])).scalar()

                order.total_amount = order.total_amount + (product_price * int(line_quantities[i]))

                total_inventory_product = connection.query(models.TotalInventory).filter_by(product_id=int(line_products[i])).first()
                total_inventory_product.quantity = total_inventory_product.quantity-int(line_quantities[i])
                total_inventory_product.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                is_detail = connection.query(models.DeliveryDetail).filter(models.DeliveryDetail.delivery_id==order.id, models.DeliveryDetail.product_id==int(line_products[i])).first()

                if is_detail:
                    is_detail.quantity = is_detail.quantity + int(line_quantities[i])
                else:
                    order.delivery_details.append(order_detail)
                    connection.flush()

            payment_detail = models.PaymentDetail()
            payment_detail.card_amount = int(request.form.get("cardInput"))
            payment_detail.cash_amount = int(request.form.get("cashInput"))
            payment_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            payment_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            payment_detail.delivery_id = order.id

            connection.add(payment_detail)

            try:
                connection.commit()
            except:
                flash('Алдаа гарлаа!', 'danger')
                connection.rollback()
                return redirect(url_for('manager_order.manager_order_add'))
            else:
                flash('Хүргэлт нэмэгдлээ.', 'success')
                return redirect(url_for('manager_order.manager_order_add'))

        return render_template('/manager/order_add.html', form=form)

    return render_template('/manager/order_add.html', form=form)


@manager_order_blueprint.route("/manager/orders/search/products/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_search_products(supplier_id):
    query = request.form.get("term")
    connection = Connection()
    search = "%{}%".format(query)
    products = connection.query(models.Product).filter(models.Product.supplier_id==supplier_id,models.Product.name.like(search)).all()
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'supplier': product.supplier.company_name,
            'color': str(product.colors[0]),
            'size': str(product.sizes[0]),
            'quantity': int(connection.query(models.TotalInventory.quantity).filter(models.TotalInventory.product_id==product.id).scalar()),
            'price': int(product.price),
        })
    return jsonify(results)



@manager_order_blueprint.route("/manager/orders/assigned", methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_unassign_orders():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    connection = Connection()
    orders = []
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name == "driver")).filter_by(is_authorized = True).all()
    form = SelectDriverForm()
    form.selected_driver.choices = [(driver.id, driver.firstname) for driver in drivers]
    form1 = UnassignForm()
    if form.validate_on_submit():
        orders = connection.query(models.Delivery).filter(func.date(models.Delivery.created_date) == cur_date.date(), models.Delivery.status=="assigned", models.Delivery.assigned_driver_id==form.selected_driver.data).all()
        return render_template('/manager/assigned_orders.html', form=form, orders=orders, form1=form1)

    if form1.validate_on_submit():
        line_order_id = request.form.getlist("order_id")

        for i, order_id in enumerate(line_order_id):
            order_to_unassigned = connection.query(models.Delivery).filter(models.Delivery.id==order_id).first()
            if order_to_unassigned.is_received_from_clerk == False:
                order_to_unassigned.status = "unassigned"
                order_to_unassigned.assigned_driver_id = None
                order_to_unassigned.assigned_driver_name = None
                order_to_unassigned.delivery_region = None

        try:
            connection.commit()
        except:
            connection.rollback()
        else:
            return redirect(url_for('manager_order.manager_order_assign_region'))
    return render_template('/manager/assigned_orders.html', form=form, orders=orders, form1=form1)



@manager_order_blueprint.route("/manager/orders/edit/<int:order_id>", methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_orders_edit(order_id):
    connection = Connection()
    order = connection.query(models.Delivery).get(order_id)

    if order is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('manager_order.manager_orders'))

    form = OrderDetailEditForm(obj=order)

    if form.validate_on_submit():
        line_products = request.form.getlist("product")
        line_quantities = request.form.getlist("quantity")

        if order.order_type == "unstored":
            flash('Өөрчлөх боложгүй', 'info')
            connection.close()
            return redirect(url_for('manager_order.manager_orders_edit', order_id=order.id))

        for i, product in enumerate(line_products):
            is_product = connection.query(models.Product).filter(models.Product.id==int(product)).first()

            if is_product:
                order_detail = models.DeliveryDetail()
                order_detail.quantity = int(line_quantities[i])
                order_detail.product_id = product
                order_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                order_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                total_inventory_product = connection.query(models.TotalInventory).filter_by(product_id=product).first()
                total_inventory_product.quantity = total_inventory_product.quantity-int(line_quantities[i])
                total_inventory_product.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                is_detail = connection.query(models.DeliveryDetail).filter(models.DeliveryDetail.delivery_id==order.id, models.DeliveryDetail.product_id==int(product)).first()

                total_inventory = connection.query(models.TotalInventory).filter(models.TotalInventory.product_id==is_product.id).first()
                total_inventory.quantity = total_inventory.quantity - int(line_quantities[i])

                order.total_amount = order.total_amount + (int(line_quantities[i]) * is_product.price)

                if is_detail:
                    is_detail.quantity = is_detail.quantity + int(line_quantities[i])
                else:
                    order.delivery_details.append(order_detail)

            else:
                flash('Зарим бараа нэмэх боломжгүй байна', 'info')
                continue
        try:
            connection.commit()
        except:
            connection.rollback()
        else:
            flash('Өөрчлөгдлөө', 'info')
            return redirect(url_for('manager_order.manager_orders_edit', order_id=order.id))

    return render_template('/manager/edit_order_details.html', order=order, form=form)


@manager_order_blueprint.route("/manager/orders/remove-detail/<int:order_detail_id>", methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_orders_remove_detail(order_detail_id):
    connection = Connection()
    detail = connection.query(models.DeliveryDetail).get(order_detail_id)

    if detail is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('manager_order.manager_orders'))

    order = connection.query(models.Delivery).get(detail.delivery_id)

    if order.order_type == "unstored":
        flash('Өөрчлөх боложгүй', 'info')
        connection.close()
        return redirect(url_for('manager_order.manager_orders'))

    
    if order.status == "unassigned":
        total_inventory = connection.query(models.TotalInventory).filter(models.TotalInventory.product_id==detail.product_id).first()
        total_inventory.quantity = total_inventory.quantity + detail.quantity

        if (detail.quantity * detail.products.price) > order.total_amount:
            order.total_amount = 0
        else:
            order.total_amount = order.total_amount - (detail.quantity * detail.products.price)

    elif order.status == "assigned" and order.is_driver_received == False and order.is_received_from_clerk == False:
        total_inventory = connection.query(models.TotalInventory).filter(models.TotalInventory.product_id==detail.product_id).first()
        total_inventory.substracted_quantity = total_inventory.substracted_quantity + detail.quantity

        if (detail.quantity * detail.products.price) > order.total_amount:
            order.total_amount = 0
        else:
            order.total_amount = order.total_amount - (detail.quantity * detail.products.price)

        driver_product_return = models.DriverProductReturn()
        driver_product_return.driver_name = order.assigned_driver_name
        driver_product_return.driver_id = current_user.id
        driver_product_return.delivery_id = order.id
        driver_product_return.product_id = detail.product_id
        driver_product_return.driver_comment = "Менежер хассан байна"
        driver_product_return.product_quantity = detail.quantity
        driver_product_return.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        driver_product_return.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        connection.add(driver_product_return)

    order.delivery_details.remove(detail)

    try:
        connection.commit()
    except Exception as e:
        connection.rollback()
    else:
        return redirect(url_for('manager_order.manager_orders_edit', order_id=order.id))

    
