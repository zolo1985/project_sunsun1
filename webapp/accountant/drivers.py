from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.api.orders import order_histories
from webapp.database import Connection
from webapp.accountant.forms import SalaryDataDateSelect
from webapp import models
from datetime import datetime, timedelta
from sqlalchemy.sql import text
import pytz
from dateutil.rrule import DAILY,rrule
import calendar

from webapp.manager.forms import DriversDateSelect

accountant_drivers_blueprint = Blueprint('accountant_drivers', __name__)

@accountant_drivers_blueprint.route('/accountant/drivers', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_drivers():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()

    drivers_datas = []

    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()

    current_period = connection.execute("select date_sub(curdate(), interval day(curdate())-1 day) as first_day, date_sub(date_add(curdate(), interval 1 month), interval day(curdate()) day) as last_day;").first()
    for driver in drivers:
        data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
        days_list = []
        days_data = []
        for i in rrule(DAILY , dtstart=current_period.first_day, until=current_period.last_day):
            day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
            day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
            day_format = (i.day,day_orders,day_pickups)
            days_list.append(day_format)
            days_data.append(i.day)

        data_format.insert(2, (days_list))
        drivers_datas.append(data_format)

    payment_amount = connection.query(models.PaymentType.amount).filter(models.PaymentType.name=="Үндсэн үнэ").scalar()

    form = SalaryDataDateSelect()

    if form.select_date.data is not None and form.validate_on_submit():
        drivers_datas = []
        payment_amount = connection.query(models.PaymentType.amount).filter(models.PaymentType.name=="Үндсэн үнэ").scalar()
        drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
        selected_period = connection.execute("select date_sub(:selected_period, interval day(:selected_period)-1 day) as first_day, date_sub(date_add(:selected_period, interval 1 month), interval day(:selected_period) day) as last_day;", {"selected_period": form.select_date.data}).first()

        for driver in drivers:
            data_format = [f"%s %s"%(driver.lastname, driver.firstname), driver.id]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.strptime(selected_period.first_day, '%Y-%m-%d'), until=datetime.strptime(selected_period.last_day, '%Y-%m-%d') ):
                day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_format = (i.day,day_orders,day_pickups)
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            drivers_datas.append(data_format)
        print(drivers_datas)
        print(drivers)
        return render_template('/accountant/drivers.html', current_date=form.select_date.data, datas = drivers_datas, payment_amount=payment_amount, day_list=days_data, form=form)

    return render_template('/accountant/drivers.html', current_date=current_date, datas = drivers_datas, payment_amount=payment_amount, day_list=days_data, form=form)


# @accountant_drivers_blueprint.route('/accountant/drivers', methods=['GET','POST'])
# @login_required
# @has_role('accountant')
# def accountant_drivers():
#     connection = Connection()
#     current_week_number = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date().isocalendar()[1]
#     current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
#     # drivers_datas = []

#     if (int(current_week_number) % 2) == 0:
#         current_week_number = current_week_number
#     else:
#         current_week_number = current_week_number - 1

#     drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
#     current_period = connection.execute("SELECT CONCAT(Year(curdate()), '-01-01') + INTERVAL :week_number WEEK - INTERVAL WEEKDAY(CONCAT(Year(curdate()), '-01-01')) DAY as first_day_of_week, CONCAT(Year(curdate()), '-01-01') + INTERVAL :week_number WEEK - INTERVAL WEEKDAY(CONCAT(Year(curdate()), '-01-01')) - 13 DAY as last_day_of_week;", {"week_number": current_week_number}).first()

#     for driver in drivers:
#         data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
#         days_list = []
#         days_data = []
#         for i in rrule(DAILY , dtstart=datetime.fromisoformat(current_period.first_day_of_week), until=datetime.fromisoformat(current_period.last_day_of_week)):
#             day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
#             day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
#             day_format = (i.day,day_orders,day_pickups)
#             days_list.append(day_format)
#             days_data.append(i.day)

#         data_format.insert(2, (days_list))
#         drivers_datas.append(data_format)

#     payment_amount = connection.query(models.PaymentType.amount).filter(models.PaymentType.name=="Үндсэн үнэ").scalar()

#     form = SalaryDataDateSelect()

#     if form.select_date.data is not None and form.validate_on_submit():
#         drivers_datas = []
#         current_week_number1 = form.select_date.data.isocalendar()[1]
#         if (int(current_week_number1) % 2) == 0:
#             current_week_number1 = current_week_number1
#         else:
#             current_week_number1 = current_week_number1 - 1

#         current_period = connection.execute("SELECT CONCAT(Year(curdate()), '-01-01') + INTERVAL :week_number WEEK - INTERVAL WEEKDAY(CONCAT(Year(curdate()), '-01-01')) DAY as first_day_of_week, CONCAT(Year(curdate()), '-01-01') + INTERVAL :week_number WEEK - INTERVAL WEEKDAY(CONCAT(Year(curdate()), '-01-01')) - 13 DAY as last_day_of_week;", {"week_number": current_week_number1}).first()
        
#         for driver in drivers:
#             data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
#             days_list = []
#             days_data = []
#             for i in rrule(DAILY , dtstart=datetime.fromisoformat(current_period.first_day_of_week), until=datetime.fromisoformat(current_period.last_day_of_week)):
#                 day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
#                 day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
#                 day_format = (i.day,day_orders,day_pickups)
#                 days_list.append(day_format)
#                 days_data.append(i.day)

#             data_format.insert(2, (days_list))
#             drivers_datas.append(data_format)

#         print(drivers_datas)

#         return render_template('/accountant/drivers.html', datas = drivers_datas, current_period_start=current_period.first_day_of_week.rsplit('-', 1)[1], current_period_end=current_period.last_day_of_week.rsplit('-', 1)[1], current_date=form.select_date.data, payment_amount=payment_amount, form=form, day_list=days_data)

#     print(drivers_datas)

#     return render_template('/accountant/drivers.html', datas = drivers_datas, current_period_start=current_period.first_day_of_week.rsplit('-', 1)[1], current_period_end=current_period.last_day_of_week.rsplit('-', 1)[1], current_date=current_date, payment_amount=payment_amount, form=form, day_list=days_data)