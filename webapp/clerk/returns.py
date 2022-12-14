from flask import (Blueprint, render_template, redirect, url_for, flash)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp.clerk.forms import FilterDateForm
from webapp import models
from datetime import datetime
from sqlalchemy import func
import pytz


clerk_returns_blueprint = Blueprint('clerk_returns', __name__)


@clerk_returns_blueprint.route('/clerk/returns', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_driver_returns():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    connection = Connection()
    returns = connection.query(models.DriverReturn).filter(func.date(models.DriverReturn.created_date) == cur_date).order_by(models.DriverReturn.created_date).all()
    substracted_products = connection.query(models.DriverProductReturn).filter(func.date(models.DriverProductReturn.created_date) == cur_date).all()

    form = FilterDateForm()
    if form.validate_on_submit():
        returns = connection.query(models.DriverReturn).filter(func.date(models.DriverReturn.created_date) == form.date.data).order_by(models.DriverReturn.created_date).all()
        substracted_products = connection.query(models.DriverProductReturn).filter(func.date(models.DriverProductReturn.created_date) == form.date.data).all()
        return render_template('/clerk/returns.html', returns=returns, form=form, substracted_products=substracted_products)

    return render_template('/clerk/returns.html', returns=returns, form=form, substracted_products=substracted_products)


@clerk_returns_blueprint.route('/clerk/returns/postphoned/<int:return_id>')
@login_required
@has_role('clerk')
def clerk_postphoned_order(return_id):
    connection = Connection()
    product_return = connection.query(models.DriverReturn).get(return_id)

    if product_return is None:
        flash('Буцаалт олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    if product_return.is_returned==True:
        flash('Захиалгыг буцааж авсан байна!', 'info')
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    if product_return.delivery_status!="postphoned":
        flash('Төлөв буруу байна', 'danger')
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    if product_return.delivery.order_type=="stored":
        try:
            for i, delivery_detail in enumerate(product_return.delivery.delivery_details):
                total_inventory = connection.query(models.TotalInventory).filter(models.TotalInventory.product_id==delivery_detail.product_id).first()
                total_inventory.postphoned_quantity = total_inventory.postphoned_quantity - delivery_detail.quantity
                total_inventory.quantity = total_inventory.quantity + delivery_detail.quantity

            product_return.delivery.is_returned = True

            product_return.is_returned = True
            product_return.returned_clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
            product_return.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('clerk_returns.clerk_driver_returns'))
        else:
            flash('Хүлээж авлаа', 'success')
            return redirect(url_for('clerk_returns.clerk_driver_returns'))

    elif product_return.delivery.order_type=="unstored":
        
        product_return.delivery.is_returned = True
        product_return.is_returned = True
        product_return.returned_clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
        product_return.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('clerk_returns.clerk_driver_returns'))
        else:
            flash('Хүлээж авлаа', 'success')
            return redirect(url_for('clerk_returns.clerk_driver_returns'))
    else:
        return redirect(url_for('clerk_returns.clerk_driver_returns'))


@clerk_returns_blueprint.route('/clerk/returns/cancelled/<int:return_id>')
@login_required
@has_role('clerk')
def clerk_cancelled_order(return_id):
    connection = Connection()
    product_return = connection.query(models.DriverReturn).get(return_id)

    if product_return is None:
        flash('Буцаалт олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    if product_return.is_returned==True:
        flash('Захиалгыг буцааж авсан байна!', 'info')
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    if product_return.delivery_status!="cancelled":
        flash('Төлөв буруу байна', 'danger')
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    if product_return.delivery.order_type=="stored":
        try:
            for i, delivery_detail in enumerate(product_return.delivery.delivery_details):
                total_inventory = connection.query(models.TotalInventory).filter(models.TotalInventory.product_id==delivery_detail.product_id).first()
                total_inventory.cancelled_quantity = total_inventory.cancelled_quantity - delivery_detail.quantity
                total_inventory.quantity = total_inventory.quantity + delivery_detail.quantity

            product_return.delivery.is_returned = True

            product_return.is_returned = True
            product_return.returned_clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
            product_return.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('clerk_returns.clerk_driver_returns'))
        else:
            flash('Хүлээж авлаа', 'success')
            return redirect(url_for('clerk_returns.clerk_driver_returns'))

    elif product_return.delivery.order_type=="unstored":
        
        product_return.delivery.is_returned = True

        product_return.is_returned = True
        product_return.returned_clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
        product_return.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        dropoff_task = connection.query(models.DropoffTask).filter(models.DropoffTask.is_completed==False, models.DropoffTask.supplier_id==product_return.delivery.user_id, models.DropoffTask.status=="waiting").first()

        if dropoff_task:
            new_dropoff_task_detail = models.DropoffTaskDetail()
            new_dropoff_task_detail.quantity = 1
            new_dropoff_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            new_dropoff_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            new_dropoff_task_detail.phone = product_return.delivery.delivery_details[0].phone
            new_dropoff_task_detail.delivery_id = product_return.delivery.id

            dropoff_task.dropoff_details.append(new_dropoff_task_detail)
            
        else:
            new_dropoff_task = models.DropoffTask()
            new_dropoff_task.is_ready = True
            new_dropoff_task.status = "waiting"
            new_dropoff_task.supplier_company = product_return.delivery.supplier_company_name
            new_dropoff_task.supplier_id = product_return.delivery.user_id
            new_dropoff_task.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            new_dropoff_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            new_dropoff_task_detail = models.DropoffTaskDetail()
            new_dropoff_task_detail.quantity = 1
            new_dropoff_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            new_dropoff_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            new_dropoff_task_detail.phone = product_return.delivery.delivery_details[0].phone
            new_dropoff_task_detail.delivery_id = product_return.delivery.id

            new_dropoff_task.dropoff_details.append(new_dropoff_task_detail)
            connection.add(new_dropoff_task)

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('clerk_returns.clerk_driver_returns'))
        else:
            flash('Хүлээж авлаа', 'success')
            return redirect(url_for('clerk_returns.clerk_driver_returns'))
    else:
        return redirect(url_for('clerk_returns.clerk_driver_returns'))



@clerk_returns_blueprint.route('/clerk/returns/substracted/<int:return_id>')
@login_required
@has_role('clerk')
def clerk_substracted_product(return_id):
    connection = Connection()
    product_to_substract = connection.query(models.DriverProductReturn).get(return_id)

    if product_to_substract is None:
        flash('Буцаалт олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    if product_to_substract.is_returned==True:
        flash('Захиалгыг буцааж авсан байна!', 'info')
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    try:
        total_inventory = connection.query(models.TotalInventory).filter(models.TotalInventory.product_id==product_to_substract.product_id).first()
        total_inventory.substracted_quantity = total_inventory.substracted_quantity - product_to_substract.product_quantity
        total_inventory.quantity = total_inventory.quantity + product_to_substract.product_quantity
        product_to_substract.is_returned = True
        product_to_substract.returned_clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
        product_to_substract.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        connection.commit()
    except Exception:
        flash('Алдаа гарлаа!', 'danger')
        connection.rollback()
        connection.close()
        return redirect(url_for('clerk_returns.clerk_driver_returns'))
    else:
        flash('Хүлээж авлаа', 'success')
        return redirect(url_for('clerk_returns.clerk_driver_returns'))

    