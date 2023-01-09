from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import accountant, has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp.accountant.forms import SupplierDateSelect, DateSelect
from webapp import models
from sqlalchemy import func, or_
from datetime import datetime
from dateutil.rrule import DAILY,rrule
import calendar
import pytz

accountant_supplier_calculation_blueprint = Blueprint('accountant_supplier_calculation', __name__)

@accountant_supplier_calculation_blueprint.route('/accountant/supplier/calculations', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_supplier_calculations():
    connection = Connection()
    suppliers_total = []

    form = SupplierDateSelect()
    
    if form.validate_on_submit():
        suppliers_total = connection.execute('SELECT supplier.company_name as supplier_name, count(delivery.id) as total_delivery_count, sum(delivery.total_amount) as total_amount, supplier.is_invoiced as is_invoiced, supplier.fee as fee FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where DATE(delivery.delivered_date) = DATE(:date) and delivery.is_delivered=true group by supplier.company_name, supplier.is_invoiced, supplier.fee;', {"date": form.select_date.data}).all()
        return render_template('/accountant/supplier_calculation.html', form=form, suppliers_total=suppliers_total)

    return render_template('/accountant/supplier_calculation.html', form=form, suppliers_total=suppliers_total)


@accountant_supplier_calculation_blueprint.route('/accountant/supplier/calculations/history', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_supplier_calculations_history():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    suppliers_datas = []
    connection = Connection()
    suppliers = connection.query(models.User).filter(or_(models.User.roles.any(models.Role.name=="supplier1"), models.User.roles.any(models.Role.name=="supplier2"))).all()
    days_data = []

    if current_date.day <= 15:
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


        return render_template('/accountant/supplier_calculations.html', suppliers_datas=suppliers_datas, current_date=current_date, day_list=days_data, form=form)

    return render_template('/accountant/supplier_calculations.html', suppliers_datas=suppliers_datas, current_date=current_date, day_list=days_data, form=form)

    