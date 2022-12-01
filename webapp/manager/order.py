from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import FilterOrderByDistrict, FiltersForm, OrderEditForm, AssignRegionAndDriverForm, DriversSelect, DriversHistoriesForm, FilterDateForm, EditCommentForm, EditAddressForm, EditTotalAmountForm, MakeShowCommentForm
from datetime import datetime, timedelta
from sqlalchemy import func
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
    orders = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == cur_date.date()).filter(models.Delivery.status == "unassigned").filter(models.Delivery.destination_type == "local").filter(models.Delivery.is_ready==True).order_by(models.Address.district).all()
    long_destination_orders = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == cur_date.date()).filter(models.Delivery.status == "unassigned").filter(models.Delivery.destination_type == "long").filter(models.Delivery.destination_type == "long").filter(models.Delivery.is_ready==True).order_by(models.Address.aimag).all()

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

    form3 = AssignRegionAndDriverForm()
    form3.select_regions.choices = [(delivery_region) for delivery_region in delivery_regions]
    form3.select_drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]
    form3.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))

    if form1.validate():
        if form1.district_names.data != 'Дүүрэг сонгох' and form1.khoroo_names.data == 'Хороо сонгох':
            orders1 = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == cur_date.date()).filter(models.Delivery.status == "unassigned").filter(models.Address.district==form1.district_names.data).filter(models.Delivery.is_ready==True).order_by(models.Address.district).all()
            orders = orders1
            return render_template('/manager/assign_regions_and_drivers.html', orders=orders, total_orders_count_by_district=total_orders_count_by_district, form=form, form1=form1, form3=form3, cur_date=cur_date.date())
        elif form1.district_names.data != 'Дүүрэг сонгох' and form1.khoroo_names.data != 'Хороо сонгох':
            orders1 = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == cur_date.date()).filter(models.Delivery.status == "unassigned").filter(models.Address.district==form1.district_names.data).filter(models.Address.khoroo==str(form1.khoroo_names.data)).filter(models.Delivery.is_ready==True).order_by(models.Address.district).all()
            orders = orders1
            return render_template('/manager/assign_regions_and_drivers.html', orders=orders, total_orders_count_by_district=total_orders_count_by_district, form=form, form1=form1, form3=form3, cur_date=cur_date.date())
        else:
            return redirect(url_for('manager_order.manager_order_assign_region'))

    if form.validate_on_submit():
        line_order_id = request.form.getlist("order_id")

        if form.select_drivers.data == "0":
            selected_region = connection.query(models.Region).filter_by(name=form.select_regions.data).first()

            if len(line_order_id) <= 0:
                return redirect(url_for('manager_order.manager_order_assign_region'))

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

    if form3.validate_on_submit():

        selected_region = connection.query(models.Region).filter_by(name=form.select_regions.data).first()

        line_order_id = request.form.getlist("order_id")

        if len(line_order_id) <= 0:
            return redirect(url_for('manager_order.manager_order_assign_region'))

        for i, order_id in enumerate(line_order_id):
            
            driver_name = connection.query(models.User).get(form3.select_drivers.data)
            order = connection.query(models.Delivery).get(order_id)
            order.delivery_region = form3.select_regions.data
            order.assigned_manager_id = current_user.id
            order.assigned_driver_name = f'%s %s'%(driver_name.lastname, driver_name.firstname)
            order.assigned_driver_id = form3.select_drivers.data
            order.status = "assigned"
            order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            order.delivery_attempts = 0
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
                flash('Бүслэгдлээ. Хувиарлагдлаа', 'success')    
                return redirect(url_for('manager_order.manager_order_assign_region'))

    return render_template('/manager/assign_regions_and_drivers.html', orders=orders, total_orders_count_by_district=total_orders_count_by_district, form=form, form1=form1, form3=form3, long_destination_orders=long_destination_orders, total_orders_count_by_driver=total_orders_count_by_driver, total_postphoned_count_by_driver=total_postphoned_count_by_driver, total_postphoned_count_by_driver_from_previous_days=total_postphoned_count_by_driver_from_previous_days, total_orders_count_by_aimag=total_orders_count_by_aimag, cur_date=cur_date.date())



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
    form1 = MakeShowCommentForm()

    if form.validate_on_submit() and form.date.data is not None:
        orders = connection.query(models.Delivery).filter(func.date(models.Delivery.delivered_date) == form.date.data, models.Delivery.driver_comment!=None, models.Delivery.show_comment==False).all()
        return render_template('/manager/orders_comments.html', form=form, orders=orders, cur_date=cur_date, form1=form1)

    if form1.validate_on_submit():
        line_order_id = request.form.getlist("order_id")

        for i, order_id in enumerate(line_order_id):
            order = connection.query(models.Delivery).get(order_id)
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
            flash('Комментууд нээгдлээ.', 'success')    
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
        comment_to_update.show_comment = True
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
            return redirect(url_for('manager_order.manager_commented_orders'))
        else:
            connection.close()
            flash('Коммент өөрчлөгдлөө', 'success')    
            return redirect(url_for('manager_order.manager_commented_orders'))

    elif request.method == 'GET':
        form.total_amount.data = order.total_amount
        return render_template('/manager/edit_total_amount.html', form=form, order=order, cur_date=cur_date)

    return render_template('/manager/edit_total_amount.html', form=form, order=order, cur_date=cur_date)