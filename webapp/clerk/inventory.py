from flask import (Blueprint, render_template, request)
from webapp import has_role
from flask_login import login_required
from flask_paginate import Pagination, get_page_parameter
from webapp.database import Connection
from webapp import models

clerk_inventory_blueprint = Blueprint('clerk_inventory', __name__)

@clerk_inventory_blueprint.route('/clerk/supplier1/inventories')
@login_required
@has_role('clerk')
def clerk_inventories():
    connection = Connection()
    count = connection.query(models.TotalInventory).count()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 50
    inventories = get_inventories(page, per_page)

    pagination = Pagination(page=page, total=count,  per_page=per_page, bs_version='5')
    return render_template('/clerk/inventories.html', inventories=inventories, pagination=pagination)


def get_inventories(page, per_page):
    per_page_inventories=per_page
    offset = (page - 1) * per_page_inventories
    connection = Connection()
    inventories = connection.query(models.TotalInventory).offset(offset).limit(per_page_inventories)
    connection.close()
    return inventories

@clerk_inventory_blueprint.route('/clerk/supplier2/inventories')
@login_required
@has_role('clerk')
def clerk_inventories_supplier2():
    connection = Connection()
    # returned_orders = connection.query(models.Delivery).filter(models.Delivery.status=="cancelled", models.Delivery.is_cancelled==True, models.Delivery.order_type=="unstored", models.Delivery.is_returned==True).all()
    returned_orders = connection.query(models.DriverReturn).filter(models.DriverReturn.delivery_status=="cancelled", models.DriverReturn.delivery.has(models.Delivery.order_type=="unstored"), models.DriverReturn.delivery.has(models.Delivery.is_returned==True)).all()

    return render_template('/clerk/supplier2_returned_inventories.html', returned_orders=returned_orders)