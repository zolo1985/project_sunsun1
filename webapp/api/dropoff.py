from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from webapp.database import Connection
from webapp import models
from datetime import datetime, timezone
from sqlalchemy import and_, or_, func
from dateutil import tz
import pytz
import json

dropoffs_api = Blueprint('dropoffs_api', __name__)

@dropoffs_api.route('/api/dropoffs', methods = ["GET", "POST"])
@jwt_required()
def dropoffs():
    connection = Connection()
    dropoffs = connection.query(models.DropoffTask).filter(models.DropoffTask.driver_id==current_user.id).filter(models.DropoffTask.is_completed==False).all()

    payload = []
    for dropoff in dropoffs:
        payload.append({
        "id": dropoff.id,
        "company_name": dropoff.supplier_company,
        "quantity": len(dropoff.dropoff_details),
        "dropoff_date": dropoff.created_date.strftime("%Y-%m-%d"),
        "status": dropoff.status,
        "products": [{
            "name": task.phone,
            "quantity": 1,
            } for task in dropoff.dropoff_details]})
    
    return jsonify(payload), 200