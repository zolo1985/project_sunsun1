from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp.accountant.forms import DateSelect
from webapp import models
from sqlalchemy import func
from datetime import datetime
import calendar
from dateutil.rrule import DAILY,rrule
import pytz


accountant_payment_history_blueprint = Blueprint('accountant_payment_history', __name__)

@accountant_payment_history_blueprint.route('/accountant/driver-payment-histories', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_payment_histories():
    connection = Connection()
    
    payment_histories = []

    form = DateSelect()

    if form.validate_on_submit():
        payment_histories = connection.query(models.AccountantPaymentHistory).filter(func.date(models.AccountantPaymentHistory.created_date) == form.select_date.data).all()
        return render_template('/accountant/payment_histories.html', form=form, payment_histories=payment_histories)

    return render_template('/accountant/payment_histories.html', form=form, payment_histories=payment_histories)



@accountant_payment_history_blueprint.route('/accountant/driver-payment-histories/two-week', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_payment_histories_two_week():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
    payment_datas = []

    if current_date.day <= 15:
        for driver in drivers:
            driver_format = [f'%s %s'%(driver.lastname, driver.firstname) , driver.id]
            daily_data = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 15))):
                day_info = connection.execute('SELECT COALESCE(sum(aph.card_amount),0) as card_amount, COALESCE(sum(aph.cash_amount),0) as cash_amount, COALESCE(sum(aph.remaining_amount),0) as remaining_amount FROM sunsundatabase1.accountant_payment_history as aph where aph.driver_id=:driver_id and DATE(aph.date_of_payment)=:day;', {"day": i.date(), "driver_id": driver.id}).first()
                day_format = (i.day, int(day_info.card_amount + day_info.cash_amount) if day_info is not None else 0, int(day_info.remaining_amount) if day_info is not None else 0)
                daily_data.append(day_format)
                days_data.append(i.day)

            driver_format.insert(2, (daily_data))
            payment_datas.append(driver_format)

    else:
        for driver in drivers:
            driver_format = [f'%s %s'%(driver.lastname, driver.firstname) , driver.id]
            daily_data = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]))):
                day_info = connection.execute('SELECT COALESCE(sum(aph.card_amount),0) as card_amount, COALESCE(sum(aph.cash_amount),0) as cash_amount, COALESCE(sum(aph.remaining_amount),0) as remaining_amount FROM sunsundatabase1.accountant_payment_history as aph where aph.driver_id=:driver_id and DATE(aph.date_of_payment)=:day;', {"day": i.date(), "driver_id": driver.id}).first()
                day_format = (i.day, int(day_info.card_amount + day_info.cash_amount) if day_info is not None else 0, int(day_info.remaining_amount) if day_info is not None else 0)
                daily_data.append(day_format)
                days_data.append(i.day)

            driver_format.insert(2, (daily_data))
            payment_datas.append(driver_format)

    form = DateSelect()

    if form.select_date.data is not None and form.validate_on_submit():
        payment_datas = []
        if (form.select_date.data.day) <= 15:
            for driver in drivers:
                driver_format = [f'%s %s'%(driver.lastname, driver.firstname) , driver.id]
                daily_data = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 15))):
                    day_info = connection.execute('SELECT COALESCE(sum(aph.card_amount),0) as card_amount, COALESCE(sum(aph.cash_amount),0) as cash_amount, COALESCE(sum(aph.remaining_amount),0) as remaining_amount FROM sunsundatabase1.accountant_payment_history as aph where aph.driver_id=:driver_id and DATE(aph.date_of_payment)=:day;', {"day": i.date(), "driver_id": driver.id}).first()
                    day_format = (i.day, int(day_info.card_amount + day_info.cash_amount) if day_info is not None else 0, int(day_info.remaining_amount) if day_info is not None else 0)
                    daily_data.append(day_format)
                    days_data.append(i.day)

                driver_format.insert(2, (daily_data))
                payment_datas.append(driver_format)

        else:
            for driver in drivers:
                driver_format = [f'%s %s'%(driver.lastname, driver.firstname) , driver.id]
                daily_data = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.select_date.data.year, form.select_date.data.month, calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]))):
                    day_info = connection.execute('SELECT COALESCE(sum(aph.card_amount),0) as card_amount, COALESCE(sum(aph.cash_amount),0) as cash_amount, COALESCE(sum(aph.remaining_amount),0) as remaining_amount FROM sunsundatabase1.accountant_payment_history as aph where aph.driver_id=:driver_id and DATE(aph.date_of_payment)=:day;', {"day": i.date(), "driver_id": driver.id}).first()
                    day_format = (i.day, int(day_info.card_amount + day_info.cash_amount) if day_info is not None else 0, int(day_info.remaining_amount) if day_info is not None else 0)
                    daily_data.append(day_format)
                    days_data.append(i.day)

                driver_format.insert(2, (daily_data))
                payment_datas.append(driver_format)

        return render_template('/accountant/payment_histories_two_week.html', payment_datas=payment_datas, current_date=current_date, day_list=days_data, form=form)

    return render_template('/accountant/payment_histories_two_week.html', payment_datas=payment_datas, current_date=current_date, day_list=days_data, form=form)
