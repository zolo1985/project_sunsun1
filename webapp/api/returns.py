from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from webapp.database import Connection
from webapp import models
from datetime import datetime, timezone
from sqlalchemy import and_, or_, func
from dateutil import tz
import pytz
import json

returns_api = Blueprint('returns_api', __name__)

@returns_api.route('/api/returns', methods = ["GET", "POST"])
@jwt_required()
def returns():
    connection = Connection()
    driver_returns = connection.query(models.DriverReturn).filter(models.DriverReturn.is_returned==False, models.DriverReturn.driver_id==current_user.id).order_by(models.DriverReturn.created_date).all()
    substracted_products = connection.query(models.DriverProductReturn).filter(models.DriverProductReturn.is_returned==False, models.DriverProductReturn.driver_id==current_user.id).all()

    payload = []

    for driver_return in driver_returns:
        if driver_return.delivery.order_type == "unstored":
            payload.append({
            "id": driver_return.id,
            "company_name": driver_return.delivery.supplier_company_name,
            "status": driver_return.is_returned,
            "supplier_type": "unstored",
            "type": "delivery",
            "products": [{
                "name": driver_return.delivery.delivery_details[0].phone,
                "quantity": 1,
                }]})

        elif driver_return.delivery.order_type == "stored":
            payload.append({
            "id": driver_return.id,
            "company_name": driver_return.delivery.supplier_company_name,
            "status": driver_return.is_returned,
            "supplier_type": "stored",
            "type": "delivery",
            "products": [{
                "name": detail.products.name,
                "quantity": detail.quantity,
                "size": str(detail.products.sizes[0]),
                "color": str(detail.products.colors[0]),
                } for detail in driver_return.delivery.delivery_details]})


    for substracted_product in substracted_products:
        payload.append({
            "id": substracted_product.id,
            "company_name": substracted_product.delivery.supplier_company_name,
            "status": substracted_product.is_returned,
            "supplier_type": "stored",
            "type": "substracted",
            "products": [{
                "name": detail.products.name,
                "quantity": substracted_product.product_quantity,
                "size": str(detail.products.sizes[0]),
                "color": str(detail.products.colors[0]),
                } for detail in substracted_product.delivery.delivery_details]})
                

    return jsonify(payload), 200

        
        


