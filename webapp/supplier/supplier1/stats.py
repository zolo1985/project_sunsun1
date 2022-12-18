from flask import (Blueprint, render_template, request)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import SelectOption, DateSelect
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from dateutil.rrule import DAILY,rrule
import calendar
import pytz


supplier1_stats_blueprint = Blueprint('supplier1_stats', __name__)

initial_options = ["Өдрөөр", "Долоо хоногоор", "Сараар", "Жилээр"]

@supplier1_stats_blueprint.route('/supplier1/stats', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_stats():
    connection = Connection()

    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    completed = []
    cancelled = []
    total_monthly_orders = []
  
    yearly_orders_chart_tuple = connection.execute("SELECT MONTH(driver_order_history.delivery_date) as month, COUNT(*) as total, driver_order_history.delivery_status as status FROM driver_order_history as driver_order_history join sunsundatabase1.delivery as ob on driver_order_history.delivery_id=ob.id WHERE driver_order_history.delivery_date <= NOW() AND driver_order_history.delivery_date >= Date_add(Now(),interval - 12 month) and ob.user_id=:current_user and driver_order_history.delivery_status!='postphoned' GROUP BY YEAR(driver_order_history.delivery_date), MONTH(driver_order_history.delivery_date), driver_order_history.delivery_status;", {"current_user": current_user.id}).all()
    for i, month in enumerate(months):
        completed.insert(i, 0)
        cancelled.insert(i, 0)

    for month in months:
        for i, data in enumerate(yearly_orders_chart_tuple):
            if data["month"] == month:
                if data["status"] == "completed":
                    completed[int(data["month"] - 1)] = int(data["total"])
                elif data["status"] == "cancelled":
                    cancelled[int(data["month"] - 1)] = int(data["total"])
            else:
                continue

    for i, month in enumerate(months):
        total_monthly_orders.insert(i, 0)

    for month in months:
        for i, data in enumerate(yearly_orders_chart_tuple):
            if data["month"] == month:
                if data["status"] == "completed":
                    total_monthly_orders[int(data["month"] - 1)] = int(total_monthly_orders[int(data["month"] - 1)]) + int(data["total"])
                elif data["status"] == "cancelled":
                    total_monthly_orders[int(data["month"] - 1)] = int(total_monthly_orders[int(data["month"] - 1)]) + int(data["total"])
            else:
                continue

    form = SelectOption()
    form.select_option.choices = [(option) for option in initial_options]

    if form.validate_on_submit():
        return render_template('/shared/stats.html', title='Хүргэлт стастистик', data1=completed, data2=cancelled, data_total=total_monthly_orders, form=form)

    return render_template('/shared/stats.html', title='Хүргэлт стастистик', data1=completed, data2=cancelled, data_total=total_monthly_orders, form=form)



@supplier1_stats_blueprint.route('/supplier1/balance', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_balance():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    supplier_datas = []
    connection = Connection()
    supplier = connection.query(models.User).get(current_user.id)

    if current_date.day <= 15:
        supplier_format = [supplier.company_name, supplier.id, supplier.fee, supplier.is_invoiced]
        daily_data = []
        days_data = []
        for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 15))):
            day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
            day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
            day_format = (i.day, 0 if i.day >= current_date.day else int(day_orders) if day_orders is not None else 0, 0 if i.day >= current_date.day else int(day_total_amount) if day_total_amount is not None else 0)
            daily_data.append(day_format)
            days_data.append(i.day)

        supplier_format.insert(4, (daily_data))
        supplier_datas.append(supplier_format)
    else:
        supplier_format = [supplier.company_name, supplier.id, supplier.fee, supplier.is_invoiced]
        daily_data = []
        days_data = []
        for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]))):
            day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
            day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
            day_format = (i.day, 0 if i.day >= current_date.day else int(day_orders) if day_orders is not None else 0, 0 if i.day >= current_date.day else int(day_total_amount) if day_total_amount is not None else 0)
            daily_data.append(day_format)
            days_data.append(i.day)

        supplier_format.insert(4, (daily_data))
        supplier_datas.append(supplier_format)

    form = DateSelect()

    if form.select_date.data is not None and form.validate_on_submit():
        supplier_datas = []
        if (form.select_date.data.day) <= 15:
            supplier_format = [supplier.company_name, supplier.id, supplier.fee, supplier.is_invoiced]
            daily_data = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 15))):
                day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                day_format = (i.day, 0 if i.day >= current_date.day else int(day_orders) if day_orders is not None else 0, 0 if i.day >= current_date.day else int(day_total_amount) if day_total_amount is not None else 0)
                daily_data.append(day_format)
                days_data.append(i.day)

            supplier_format.insert(4, (daily_data))
            supplier_datas.append(supplier_format)
        else:
            supplier_format = [supplier.company_name, supplier.id, supplier.fee, supplier.is_invoiced]
            daily_data = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]))):
                day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                day_format = (i.day, 0 if i.day >= current_date.day else int(day_orders) if day_orders is not None else 0, 0 if i.day >= current_date.day else int(day_total_amount) if day_total_amount is not None else 0)
                daily_data.append(day_format)
                days_data.append(i.day)

            supplier_format.insert(4, (daily_data))
            supplier_datas.append(supplier_format)

        return render_template('/supplier/supplier1/supplier_calculations.html', supplier_datas=supplier_datas, current_date=current_date, day_list=days_data, form=form)

    return render_template('/supplier/supplier1/supplier_calculations.html', supplier_datas=supplier_datas, current_date=current_date, day_list=days_data, form=form)