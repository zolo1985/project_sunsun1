from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import accountant, has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from sqlalchemy import func
from webapp.accountant.forms import FiltersForm, ReceivePaymentForm, DateSelect
from webapp import models
from datetime import datetime
import pytz

accountant_payment_history_blueprint = Blueprint('accountant_payment_history', __name__)

@accountant_payment_history_blueprint.route('/accountant/driver-payment-histories', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_payment_histories():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    connection = Connection()
    
    payment_histories = connection.query(models.AccountantPaymentHistory).filter(func.date(models.Delivery.created_date) == cur_date.date()).all()

    form = DateSelect()

    if form.validate_on_submit():
        payment_histories = connection.query(models.AccountantPaymentHistory).filter(func.date(models.Delivery.created_date) == form.select_date.data).all()
        return render_template('/accountant/payment_histories.html', form=form, payment_histories=payment_histories)

    return render_template('/accountant/payment_histories.html', form=form, payment_histories=payment_histories)