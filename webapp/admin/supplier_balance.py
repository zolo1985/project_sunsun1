from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp.admin.forms import DateSelect
from webapp import models
from sqlalchemy import func, or_
from datetime import datetime
from dateutil.rrule import DAILY,rrule
import calendar
import pytz

admin_supplier_balance_blueprint = Blueprint('admin_supplier_balance', __name__)

@admin_supplier_balance_blueprint.route('/admin/supplier-balance', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_supplier_balances():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    suppliers_datas = []
    revenue_data = []
    connection = Connection()
    suppliers = connection.query(models.User).filter(or_(models.User.roles.any(models.Role.name=="supplier1"), models.User.roles.any(models.Role.name=="supplier2"))).all()

    if current_date.day <= 15:
        revenue = connection.execute("SELECT (count(delivery.id)*supplier.fee) as revenue, supplier.company_name as revenue_from FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (DATE(delivery.delivered_date)  BETWEEN DATE(:start_date) AND DATE(:end_date)) and delivery.is_delivered=true group by supplier.id;", {"start_date": datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, "01")), "end_date": datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 15))}).all()
        revenue_data = revenue
        for supplier in suppliers:
            supplier_format = [supplier.company_name, supplier.id, supplier.fee, supplier.is_invoiced]
            daily_data = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 15))):
                day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                day_format = (i.day, int(day_orders) if day_orders is not None else 0, int(day_total_amount) if day_total_amount is not None else 0)
                daily_data.append(day_format)
                days_data.append(i.day)

            supplier_format.insert(4, (daily_data))
            suppliers_datas.append(supplier_format)
    else:
        revenue = connection.execute("SELECT (count(delivery.id)*supplier.fee) as revenue, supplier.company_name as revenue_from FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (DATE(delivery.delivered_date) BETWEEN DATE(:start_date) AND DATE(:end_date)) and delivery.is_delivered=true group by supplier.id;", {"start_date": datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 16)), "end_date": datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1])),}).all()
        revenue_data = revenue
        for supplier in suppliers:
            supplier_format = [supplier.company_name, supplier.id, supplier.fee, supplier.is_invoiced]
            daily_data = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]))):
                day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                day_format = (i.day, int(day_orders) if day_orders is not None else 0, int(day_total_amount) if day_total_amount is not None else 0)
                daily_data.append(day_format)
                days_data.append(i.day)

            supplier_format.insert(4, (daily_data))
            suppliers_datas.append(supplier_format)

    form = DateSelect()

    if form.select_date.data is not None and form.validate_on_submit():
        suppliers_datas = []
        if (form.select_date.data.day) <= 15:
            revenue = connection.execute("SELECT (count(delivery.id)*supplier.fee) as revenue, supplier.company_name as revenue_from FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (DATE(delivery.delivered_date)  BETWEEN DATE(:start_date) AND DATE(:end_date)) and delivery.is_delivered=true group by supplier.id;", {"start_date": datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, "01")), "end_date": datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 15))}).all()
            revenue_data = revenue
            for supplier in suppliers:
                supplier_format = [supplier.company_name, supplier.id, supplier.fee, supplier.is_invoiced]
                daily_data = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 15))):
                    day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                    day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                    day_format = (i.day, int(day_orders) if day_orders is not None else 0, int(day_total_amount) if day_total_amount is not None else 0)
                    daily_data.append(day_format)
                    days_data.append(i.day)

                supplier_format.insert(4, (daily_data))
                suppliers_datas.append(supplier_format)
        else:
            revenue = connection.execute("SELECT (count(delivery.id)*supplier.fee) as revenue, supplier.company_name as revenue_from FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (DATE(delivery.delivered_date)  BETWEEN DATE(:start_date) AND DATE(:end_date)) and delivery.is_delivered=true group by supplier.id;", {"start_date": datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 16)), "end_date": datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]))}).all()
            revenue_data = revenue
            for supplier in suppliers:
                supplier_format = [supplier.company_name, supplier.id, supplier.fee, supplier.is_invoiced]
                daily_data = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]))):
                    day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                    day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) =:day and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"day": i.date(), "supplier_id": supplier.id}).scalar()
                    day_format = (i.day, int(day_orders) if day_orders is not None else 0, int(day_total_amount) if day_total_amount is not None else 0)
                    daily_data.append(day_format)
                    days_data.append(i.day)

                supplier_format.insert(4, (daily_data))
                suppliers_datas.append(supplier_format)


        return render_template('/admin/supplier_calculations.html', suppliers_datas=suppliers_datas, current_date=current_date, day_list=days_data, form=form, revenue_data=revenue_data)

    return render_template('/admin/supplier_calculations.html', suppliers_datas=suppliers_datas, current_date=current_date, day_list=days_data, form=form, revenue_data=revenue_data)