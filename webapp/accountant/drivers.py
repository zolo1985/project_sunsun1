from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp.accountant.forms import SalaryDataDateSelect
from webapp import models
from datetime import datetime
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

    current_period = connection.execute("select date_sub(curdate(), interval day(curdate())-1 day) as first_day, date_sub(date_add(curdate(), interval 1 month), interval day(curdate()) day) as last_day;").first()
    for driver in drivers:
        data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
        days_list = []
        days_data = []
        for i in rrule(DAILY , dtstart=current_period.first_day, until=current_period.last_day):
            day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
            day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
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
            data_format = [f"%s.%s"%(driver.lastname[0].capitalize(), driver.firstname), driver.id]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.strptime(selected_period.first_day, '%Y-%m-%d'), until=datetime.strptime(selected_period.last_day, '%Y-%m-%d') ):
                day_orders = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="delivery";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_pickups = connection.execute('SELECT COUNT(*) as total FROM sunsundatabase1.driver_order_history AS doh WHERE DATE(doh.delivery_date)=:day and doh.driver_id=:driver_id and doh.delivery_status="completed" and doh.type="pickup";', {"day": i.date(), "driver_id": driver.id}).scalar()
                day_format = (i.day,day_orders,day_pickups)
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            drivers_datas.append(data_format)
        return render_template('/accountant/drivers.html', current_date=form.select_date.data, datas = drivers_datas, payment_amount=payment_amount, day_list=days_data, form=form)

    return render_template('/accountant/drivers.html', current_date=current_date, datas = drivers_datas, payment_amount=payment_amount, day_list=days_data, form=form)