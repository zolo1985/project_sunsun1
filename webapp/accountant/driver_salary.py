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

accountant_driver_salary_blueprint = Blueprint('accountant_driver_salary', __name__)

@accountant_driver_salary_blueprint.route('/accountant/driver-salary', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_driver_salary():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    drivers_datas = []
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()

    if current_date.day < 15:
        for driver in drivers:
            data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 15))):
                day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_dropoffs = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="dropoff";', {"day": i.date(), "driver_id": driver.id}).scalar()
                driver_remaing_balance = connection.execute('SELECT sum(sap.remaining_amount) FROM sunsundatabase1.accountant_payment_history as sap where DATE(sap.payment_of_date)=:day and sap.driver_id=:driver_id;', {"day": i.date(), "driver_id": driver.id}).scalar()
                
                day_format = (i.day,day_orders,day_pickups, day_dropoffs, int(driver_remaing_balance) if driver_remaing_balance is not None else 0)
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            data_format.insert(3, driver.fee)
            drivers_datas.append(data_format)

    else:
        for driver in drivers:
            data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]))):
                day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_dropoffs = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="dropoff";', {"day": i.date(), "driver_id": driver.id}).scalar()
                driver_remaing_balance = connection.execute('SELECT sum(sap.remaining_amount) FROM sunsundatabase1.accountant_payment_history as sap where DATE(sap.payment_of_date)=:day and sap.driver_id=:driver_id;', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_format = (i.day, day_orders, day_pickups, day_dropoffs, int(driver_remaing_balance) if driver_remaing_balance is not None else 0)
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            data_format.insert(3, driver.fee)
            drivers_datas.append(data_format)

    form = DateSelect()

    if form.select_date.data is not None and form.validate_on_submit():
        drivers_datas = []
        drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()

        if (form.select_date.data.day) <= 15:
            for driver in drivers:
                data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 15))):
                    day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_dropoffs = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="dropoff";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    driver_remaing_balance = connection.execute('SELECT sum(sap.remaining_amount) FROM sunsundatabase1.accountant_payment_history as sap where DATE(sap.payment_of_date)=:day and sap.driver_id=:driver_id;', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_format = (i.day,day_orders,day_pickups, day_dropoffs,int(driver_remaing_balance) if driver_remaing_balance is not None else 0)
                    days_list.append(day_format)
                    days_data.append(i.day)

                data_format.insert(2, (days_list))
                data_format.insert(3, driver.fee)
                drivers_datas.append(data_format)
        else:
            for driver in drivers:
                data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]))):
                    day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_dropoffs = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="dropoff";', {"day": i.date(), "driver_id": driver.id}).scalar()
                    driver_remaing_balance = connection.execute('SELECT sum(sap.remaining_amount) FROM sunsundatabase1.accountant_payment_history as sap where DATE(sap.payment_of_date)=:day and sap.driver_id=:driver_id;', {"day": i.date(), "driver_id": driver.id}).scalar()
                    day_format = (i.day,day_orders,day_pickups, day_dropoffs, int(driver_remaing_balance) if driver_remaing_balance is not None else 0)
                    days_list.append(day_format)
                    days_data.append(i.day)

                data_format.insert(2, (days_list))
                data_format.insert(3, driver.fee)
                drivers_datas.append(data_format)

        return render_template('/accountant/driver_salary.html', current_date=form.select_date.data, datas = drivers_datas, day_list=days_data, form=form)

    return render_template('/accountant/driver_salary.html', current_date=current_date, datas = drivers_datas, day_list=days_data, form=form)


