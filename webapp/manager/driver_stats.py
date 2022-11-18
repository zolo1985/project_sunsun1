from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import SelectDriverOption
from datetime import datetime
from sqlalchemy import func
import pytz
from dateutil.rrule import DAILY,rrule

manager_driver_stats_blueprint = Blueprint('manager_driver_stats', __name__)

@manager_driver_stats_blueprint.route('/manager/drivers-stats', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_drivers_stats():
    connection = Connection()
    
    initial_options = ["Өдөр", "Долоо хоног", "Сар", "Жил"]
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()

    form = SelectDriverOption()
    form.select_option.choices = [(option) for option in initial_options]
    form.select_driver.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]
    form.select_driver.choices.insert(0,(0,'Жолооч сонгох'))

    completed = []
    postphoned = []
    cancelled = []
    weekly_days = []
    monthly_days = []
    months = []
    completed_rate=[]
    cancelled_rate=[]
    postphoned_rate=[]

    if form.validate_on_submit():

        if form.select_option.data=="Өдөр":
            print("day")
            daily_orders_chart_tuple = connection.execute("SELECT DAY(driver_order_history.delivery_date) as selected_day, COUNT(*) as daily_total, driver_order_history.delivery_status as order_status FROM sunsundatabase1.driver_order_history WHERE DATE(driver_order_history.delivery_date) =:selected_date and driver_order_history.type='delivery' and driver_order_history.driver_id=:driver_id GROUP BY DAY(driver_order_history.delivery_date), driver_order_history.delivery_status;", {"selected_date": form.date.data, "driver_id": form.select_driver.data}).all()
            for i, result in enumerate(daily_orders_chart_tuple):
                if result["order_status"] == "completed":
                    completed.append(result["daily_total"])
                elif result["order_status"] == "cancelled":
                    cancelled.append(result["daily_total"])
                elif result["order_status"] == "postphoned":
                    postphoned.append(result["daily_total"])

            for i in range(1):
                total = sum(completed + cancelled + postphoned)

                if total > 0:
                    if not completed:
                        completed_rate.insert(0,0)
                    else:
                        completed_rate.insert(i, round((completed[i]/total)*100, 1))

                    if not cancelled:
                        cancelled_rate.insert(0,0)
                    else:
                        cancelled_rate.insert(i, round((cancelled[i]/total)*100, 1))

                    if not postphoned:
                        postphoned_rate.insert(0,0)
                    else:
                        postphoned_rate.insert(i, round((postphoned[i]/total)*100, 1))
                else:
                    completed_rate.insert(i, 0)
                    cancelled_rate.insert(i, 0)
                    postphoned_rate.insert(i, 0)

            return render_template('/manager/stats/daily_stats.html', data1=completed, data2=cancelled, data3=postphoned, data4=form.date.data.strftime('%Y-%m-%d'), title='Хүргэлт стастистик', form=form, selected_date=form.date.data.strftime('%Y-%m-%d'), completed_rate=completed_rate, cancelled_rate=cancelled_rate, postphoned_rate=postphoned_rate)

        elif form.select_option.data=="Долоо хоног":
            print("week")
            current_week = form.date.data.isocalendar()[1]
            current_period = connection.execute("SELECT CONCAT(Year(curdate()), '-01-01') + INTERVAL :week_number WEEK - INTERVAL WEEKDAY(CONCAT(Year(curdate()), '-01-01')) DAY as first_day_of_week, CONCAT(Year(curdate()), '-01-01') + INTERVAL :week_number WEEK - INTERVAL WEEKDAY(CONCAT(Year(curdate()), '-01-01')) - 6 DAY as last_day_of_week;", {"week_number": current_week}).first()

            weekly_orders_chart_tuple = connection.execute("SELECT DATE(driver_order_history.delivery_date) as week_day, COUNT(*) as weekly_total, driver_order_history.delivery_status as order_status FROM sunsundatabase1.driver_order_history WHERE (driver_order_history.delivery_date BETWEEN DATE(:first_day) AND DATE(:last_day)) and driver_order_history.type='delivery' and driver_order_history.driver_id=:driver_id GROUP BY DATE(driver_order_history.delivery_date), driver_order_history.delivery_status;", {"first_day": current_period.first_day_of_week, "last_day": current_period.last_day_of_week, "driver_id": form.select_driver.data}).all()

            for i in rrule(DAILY , dtstart=datetime.fromisoformat(current_period.first_day_of_week), until=datetime.fromisoformat(current_period.last_day_of_week)):
                weekly_days.append(i.strftime('%Y-%m-%d'))

            for i, week in enumerate(weekly_days):
                completed.insert(i, 0)
                cancelled.insert(i, 0)
                postphoned.insert(i, 0)

            for j, week_day in enumerate(weekly_days):
                for i, data in enumerate(weekly_orders_chart_tuple):
                    if data["week_day"].strftime('%Y-%m-%d') == week_day:
                        if data["order_status"] == "completed":
                            completed[j] = int(data["weekly_total"])
                        elif data["order_status"] == "cancelled":
                            cancelled[j] = int(data["weekly_total"])
                        elif data["order_status"] == "postphoned":
                            postphoned[j] = int(data["weekly_total"])
                    else:
                        continue

            for i, week_day in enumerate(weekly_days):
                total = completed[i] + cancelled[i] + postphoned[i]

                if total > 0:
                    completed_rate.insert(i, round((completed[i]/total)*100, 1))
                    cancelled_rate.insert(i, round((cancelled[i]/total)*100, 1))
                    postphoned_rate.insert(i, round((postphoned[i]/total)*100, 1))
                else:
                    completed_rate.insert(i, 0)
                    cancelled_rate.insert(i, 0)
                    postphoned_rate.insert(i, 0)
            
            return render_template('/manager/stats/weekly_stats.html', data1=completed, data2=cancelled, data3=postphoned, data4=weekly_days, title='Хүргэлт стастистик', form=form, selected_date=form.date.data.strftime('%Y-%m-%d'), first_day_of_week=current_period.first_day_of_week, last_day_of_week=current_period.last_day_of_week, completed_rate=completed_rate, cancelled_rate=cancelled_rate, postphoned_rate=postphoned_rate)

        elif form.select_option.data=="Сар":
            print("month")
            month_period = connection.execute("select date_sub(:selected_period, interval day(:selected_period)-1 day) as first_day_of_month, date_sub(date_add(:selected_period, interval 1 month), interval day(:selected_period) day) as last_day_of_month;", {"selected_period": form.date.data}).first()

            monthly_orders_chart_tuple = connection.execute("SELECT DAY(driver_order_history.delivery_date) as month_day, COUNT(*) as monthly_total, driver_order_history.delivery_status as order_status FROM sunsundatabase1.driver_order_history WHERE (driver_order_history.delivery_date BETWEEN DATE(:first_day) AND DATE(:last_day)) and driver_order_history.type='delivery' and driver_order_history.driver_id=:driver_id GROUP BY DAY(driver_order_history.delivery_date), driver_order_history.delivery_status;", {"first_day": month_period.first_day_of_month, "last_day": month_period.last_day_of_month, "driver_id": form.select_driver.data}).all()

            for i in rrule(DAILY , dtstart=datetime.fromisoformat(month_period.first_day_of_month), until=datetime.fromisoformat(month_period.last_day_of_month)):
                monthly_days.append(i.day)

            for i, month in enumerate(monthly_days):
                completed.insert(i, 0)
                cancelled.insert(i, 0)
                postphoned.insert(i, 0)

            for j, month_day in enumerate(monthly_days):
                for i, data in enumerate(monthly_orders_chart_tuple):
                    if data["month_day"] == month_day:
                        if data["order_status"] == "completed":
                            completed[j] = int(data["monthly_total"])
                        elif data["order_status"] == "cancelled":
                            cancelled[j] = int(data["monthly_total"])
                        elif data["order_status"] == "postphoned":
                            postphoned[j] = int(data["monthly_total"])
                    else:
                        continue

            for i, month_day in enumerate(monthly_days):
                total = completed[i] + cancelled[i] + postphoned[i]

                if total > 0:
                    completed_rate.insert(i, round((completed[i]/total)*100, 1))
                    cancelled_rate.insert(i, round((cancelled[i]/total)*100, 1))
                    postphoned_rate.insert(i, round((postphoned[i]/total)*100, 1))
                else:
                    completed_rate.insert(i, 0)
                    cancelled_rate.insert(i, 0)
                    postphoned_rate.insert(i, 0)

            return render_template('/manager/stats/monthly_stats.html', data1=completed, data2=cancelled, data3=postphoned, data4=monthly_days, title='Хүргэлт стастистик', form=form, selected_date=form.date.data.month, completed_rate=completed_rate, cancelled_rate=cancelled_rate, postphoned_rate=postphoned_rate)

        elif form.select_option.data == "Жил":
            print("year")
            monthly_orders_chart_tuple = connection.execute("SELECT MONTH(driver_order_history.delivery_date) as month_number, COUNT(*) as monthly_total, driver_order_history.delivery_status as order_status FROM sunsundatabase1.driver_order_history WHERE driver_order_history.delivery_date <= NOW() AND driver_order_history.delivery_date >= Date_add(Now(),interval - 12 month) and driver_order_history.type='delivery' and driver_order_history.driver_id=:driver_id GROUP BY YEAR(driver_order_history.delivery_date), MONTH(driver_order_history.delivery_date), driver_order_history.delivery_status;", {"driver_id": form.select_driver.data}).all()

            for i in range(12):
                completed.insert(i, 0)
                cancelled.insert(i, 0)
                postphoned.insert(i, 0)
                months.append(i+1)

            for j, month_day in enumerate(months):
                for i, data in enumerate(monthly_orders_chart_tuple):
                    if data["month_number"] == month_day:
                        if data["order_status"] == "completed":
                            completed[j] = int(data["monthly_total"])
                        elif data["order_status"] == "cancelled":
                            cancelled[j] = int(data["monthly_total"])
                        elif data["order_status"] == "postphoned":
                            postphoned[j] = int(data["monthly_total"])
                    else:
                        continue

            for i, month_day in enumerate(months):
                total = completed[i] + cancelled[i] + postphoned[i]

                if total > 0:
                    completed_rate.insert(i, round((completed[i]/total)*100, 1))
                    cancelled_rate.insert(i, round((cancelled[i]/total)*100, 1))
                    postphoned_rate.insert(i, round((postphoned[i]/total)*100, 1))
                else:
                    completed_rate.insert(i, 0)
                    cancelled_rate.insert(i, 0)
                    postphoned_rate.insert(i, 0)

            return render_template('/manager/stats/yearly_stats.html', data1=completed, data2=cancelled, data3=postphoned, data4=months, title='Хүргэлт стастистик', form=form, selected_date=form.date.data.month, completed_rate=completed_rate, cancelled_rate=cancelled_rate, postphoned_rate=postphoned_rate)
        
    return render_template('/manager/stats/drivers_stats.html', title='Хүргэлт стастистик', form=form)