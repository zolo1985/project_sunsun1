from flask import (Blueprint, flash, redirect, render_template,
                   url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from datetime import datetime
import pytz

supplier2_return_blueprint = Blueprint('supplier2_return', __name__)

@supplier2_return_blueprint.route('/supplier2/returns', methods=['GET'])
@login_required
@has_role('supplier2')
def supplier2_returns():
    connection = Connection()
    dropoff_tasks = connection.query(models.DropoffTask).filter(models.DropoffTask.supplier_id==current_user.id).limit(10)
    return render_template('/supplier/supplier2/returns.html', dropoff_tasks=dropoff_tasks)


@supplier2_return_blueprint.route('/supplier2/returns/receive/<int:dropoff_id>', methods=['GET'])
@login_required
@has_role('supplier2')
def supplier2_returns_receive(dropoff_id):
    connection = Connection()
    dropoff = connection.query(models.DropoffTask).get(dropoff_id)

    if dropoff is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('supplier2_return.supplier2_returns'))

    if dropoff.supplier_id != current_user.id:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('supplier2_return.supplier2_returns'))

    if dropoff and dropoff.is_completed==False:
        dropoff.is_completed = True
        dropoff.status = "completed"
        dropoff.delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        dropoff.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        driver_history = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.dropoff_id==dropoff.id).first()

        driver_history.delivery_status = "completed"
        driver_history.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except:
            connection.rollback()
            connection.close()
        else:
            flash('Хүлээж авлаа', 'success')
            connection.close()
            return redirect(url_for('supplier2_return.supplier2_returns'))
            
    else:
        flash('Хүлээж авсан байна', 'info')
        connection.close()
        return redirect(url_for('supplier2_return.supplier2_returns'))

    return redirect(url_for('supplier2_return.supplier2_returns'))