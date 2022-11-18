from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp.accountant.forms import DateSelect
from webapp import models
from datetime import datetime
import calendar
import pytz
from dateutil.rrule import DAILY,rrule

accountant_drivers_blueprint = Blueprint('accountant_drivers', __name__)

@accountant_drivers_blueprint.route('/accountant/drivers', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_drivers():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    drivers_datas = []
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()

    if (calendar.monthrange(current_date.year, current_date.month)[1]) < 15:
        for driver in drivers:
            data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%s-%s'%(current_date.year, current_date.month, 1)), until=datetime.fromisoformat(f'%s-%s-%s'%(current_date.year, current_date.month, 15))):
                day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_format = (i.day,day_orders,day_pickups)
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            drivers_datas.append(data_format)
    else:
        for driver in drivers:
            data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%s-%s'%(current_date.year, current_date.month, 16)), until=datetime.fromisoformat(f'%s-%s-%s'%(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]))):
                day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_format = (i.day,day_orders,day_pickups)
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            drivers_datas.append(data_format)

    payment_amount = connection.query(models.PaymentType.amount).filter(models.PaymentType.name=="Үндсэн үнэ").scalar()

    form = DateSelect()

    if form.select_date.data is not None and form.validate_on_submit():
        drivers_datas = []
        payment_amount = connection.query(models.PaymentType.amount).filter(models.PaymentType.name=="Үндсэн үнэ").scalar()
        drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()

        if (form.select_date.data.day) <= 15:
            for driver in drivers:
                data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%s-%s'%(form.select_date.data.year, form.select_date.data.month, "01")), until=datetime.fromisoformat(f'%s-%s-%s'%(form.select_date.data.year, form.select_date.data.month, 15))):
                    day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_format = (i.day,day_orders,day_pickups)
                    days_list.append(day_format)
                    days_data.append(i.day)

                data_format.insert(2, (days_list))
                drivers_datas.append(data_format)
        else:
            for driver in drivers:
                data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
                days_list = []
                print(days_list)
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%s-%s'%(form.select_date.data.year, form.select_date.data.month, 16)), until=datetime.fromisoformat(f'%s-%s-%s'%(form.select_date.data.year, form.select_date.data.month, calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]))):
                    day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_format = (i.day,day_orders,day_pickups)
                    days_list.append(day_format)
                    days_data.append(i.day)

                data_format.insert(2, (days_list))
                drivers_datas.append(data_format)

        return render_template('/accountant/drivers.html', current_date=form.select_date.data, datas = drivers_datas, payment_amount=payment_amount, day_list=days_data, form=form)

    return render_template('/accountant/drivers.html', current_date=current_date, datas = drivers_datas, payment_amount=payment_amount, day_list=days_data, form=form)


