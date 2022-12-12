from flask import (Blueprint, render_template, request)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from flask_paginate import Pagination, get_page_parameter

supplier1_expense_blueprint = Blueprint('supplier1_expense', __name__)

@supplier1_expense_blueprint.route('/supplier1/expenses', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_expenses():
    connection = Connection()

    count = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id).filter(models.Delivery.is_delivered==True).filter(models.Delivery.user_id==current_user.id).order_by(models.Delivery.created_date).count()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 50
    orders = get_expenses(page, per_page)

    pagination = Pagination(page=page, total=count,  per_page=per_page, bs_version='5')
    return render_template('/supplier/supplier1/expenses.html', orders=orders, pagination=pagination)


def get_expenses(page, per_page):
    per_page_orders=per_page
    offset = (page - 1) * per_page_orders
    connection = Connection()
    orders = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id).filter(models.Delivery.is_delivered==True).filter(models.Delivery.user_id==current_user.id).order_by(models.Delivery.created_date).offset(offset).limit(per_page_orders)
    connection.close()
    return orders