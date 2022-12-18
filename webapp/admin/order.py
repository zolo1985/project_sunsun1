from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.admin.forms import FiltersForm
from datetime import datetime
from sqlalchemy import func, or_
import pytz

admin_order_blueprint = Blueprint('admin_order', __name__)

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

@admin_order_blueprint.route('/admin/orders', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_orders():
    
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
            return redirect(url_for('admin_order.admin_orders'))

    return render_template('/admin/orders.html', orders=orders, form=form, total_orders_count_by_district=total_orders_count_by_district, total_orders_count_by_driver=total_orders_count_by_driver, total_orders_count_by_aimag=total_orders_count_by_aimag, total_postphoned_count_by_driver=total_postphoned_count_by_driver, total_postphoned_count_by_driver_from_previous_days=total_postphoned_count_by_driver_from_previous_days, cur_date=cur_date, unassigned_orders=unassigned_orders, total_orders=total_orders, delivered_orders=delivered_orders, postphoned_orders=postphoned_orders, cancelled_orders=cancelled_orders)