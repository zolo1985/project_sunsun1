from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from webapp.database import Connection
from webapp import models
from datetime import datetime, timezone
from sqlalchemy import and_, or_, func
from dateutil import tz
import pytz
import json

pickups_api = Blueprint('pickups_api', __name__)

@pickups_api.route('/api/pickups', methods = ["GET", "POST"])
@jwt_required()
def pickups():
    connection = Connection()
    pickups = connection.query(models.PickupTask).filter(models.PickupTask.driver_id==current_user.id).filter(models.PickupTask.is_completed==False).all()
    dropoffs = connection.query(models.DropoffTask).filter(models.DropoffTask.driver_id==current_user.id).filter(models.DropoffTask.is_completed==False).all()

    payload = []
    for pickup in pickups:
        if pickup.supplier_type == "supplier1":
            payload.append({
            "id": pickup.id,
            "company_name": pickup.supplier_company,
            "quantity": len(pickup.pickup_details),
            "pickup_date": pickup.pickup_date.strftime("%Y-%m-%d"),
            "status": pickup.status,
            "type": pickup.supplier_type,
            "products": [{
                "name": task.product.name,
                "quantity": task.quantity,
                "size": str(task.product.sizes[0]),
                "color": str(task.product.colors[0]),
                } for task in pickup.pickup_details]})

        elif pickup.supplier_type == "supplier2":
            payload.append({
            "id": pickup.id,
            "company_name": pickup.supplier_company,
            "quantity": len(pickup.pickup_details),
            "pickup_date": pickup.pickup_date.strftime("%Y-%m-%d"),
            "status": pickup.status,
            "type": pickup.supplier_type,
            "products": [{
                "name": task.phone,
                "quantity": 1,
                } for task in pickup.pickup_details]})
    
    return jsonify(payload), 200
