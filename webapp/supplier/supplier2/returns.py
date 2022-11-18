from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier2.forms import OrderDetailLocalAddForm, OrderDetailLongDistanceAddForm, TransferForm, DateSelectForm
from datetime import datetime, time, timedelta
from sqlalchemy import func
from webapp.utils import is_time_between
import pytz

supplier2_return_blueprint = Blueprint('supplier2_return', __name__)

@supplier2_return_blueprint.route('/supplier2/returns', methods=['GET'])
@login_required
@has_role('supplier2')
def supplier2_returns():
    connection = Connection()
    returned_orders = connection.query(models.Delivery).filter(models.Delivery.user_id==current_user.id, models.Delivery.status=="cancelled", models.Delivery.is_cancelled==True).all()

    return render_template('/supplier/supplier2/returns.html', returned_orders=returned_orders)