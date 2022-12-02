from flask import (Blueprint, render_template, request)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from sqlalchemy import func, and_, or_
from .forms import SupplierChooseForm
from webapp import models
from datetime import datetime
import calendar
import pytz
from dateutil.rrule import DAILY,rrule

clerk_inventory_blueprint = Blueprint('clerk_inventory', __name__)

@clerk_inventory_blueprint.route('/clerk/supplier1/inventories', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_inventories():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    connection = Connection()
    suppliers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier1")).filter(models.User.is_authorized==True).all()

    inventories = []
    final_inventories = []
    days_data = []

    form = SupplierChooseForm()
    form.select_supplier.choices = [(supplier.id, f'%s'%(supplier.company_name)) for supplier in suppliers]
    form.select_supplier.choices.insert(0,(0,'Харилцагч сонгох'))

    if form.date.data is None and form.select_supplier.data != 0 and form.validate_on_submit():
        supplier = connection.query(models.User).filter(models.User.id==form.select_supplier.data).first()
        inventories = supplier.total_inventories

        if current_date.day < 15:
            for inventory in inventories:
                data_format = [f"%s"%(inventory.total_inventory_product.name.capitalize()), inventory.quantity]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 15))):
                    day_added = connection.execute('SELECT sum(inventory.quantity) as total_amount FROM sunsundatabase1.inventory as inventory where inventory.product_id=:product_id and date(inventory.received_date)=:day group by inventory.product_id;', {"day": i.date(), "product_id": inventory.product_id }).scalar()
                    day_expense = connection.execute('SELECT sum(delivery_detail.quantity) as total_amount, delivery_detail.product_id as product_id FROM sunsundatabase1.delivery as delivery join sunsundatabase1.delivery_detail as delivery_detail on delivery.id=delivery_detail.delivery_id where delivery.is_delivered=true and delivery_detail.product_id=:product_id and date(delivery.delivered_date)=:day group by delivery_detail.product_id;', {"day": i.date(), "product_id": inventory.product_id }).scalar()
                    
                    day_format = (i.day, 0 if day_added is None else int(day_added), 0 if day_expense is None else int(day_expense))
                    days_list.append(day_format)
                    days_data.append(i.day)

                day_total = connection.execute('SELECT total_inventory.quantity as available_quantity, total_inventory.postphoned_quantity as postphoned_quantity, total_inventory.cancelled_quantity as cancelled_quantity, total_inventory.substracted_quantity as substracted_quantity FROM sunsundatabase1.total_inventory as total_inventory where total_inventory.product_id=:product_id;', {"product_id": inventory.product_id }).first()
                data_format.insert(2, (days_list))
                data_format.insert(3, (day_total))
                data_format.insert(4, (inventory.quantity, inventory.postphoned_quantity, inventory.cancelled_quantity, inventory.substracted_quantity))
                final_inventories.append(data_format)
        else:
            for inventory in inventories:
                data_format = [f"%s"%(inventory.total_inventory_product.name.capitalize()), inventory.quantity]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]))):
                    day_added = connection.execute('SELECT sum(inventory.quantity) as total_amount FROM sunsundatabase1.inventory as inventory where inventory.product_id=:product_id and date(inventory.received_date)=:day group by inventory.product_id;', {"day": i.date(), "product_id": inventory.product_id}).scalar()
                    day_expense = connection.execute('SELECT sum(delivery_detail.quantity) as total_amount, delivery_detail.product_id as product_id FROM sunsundatabase1.delivery as delivery join sunsundatabase1.delivery_detail as delivery_detail on delivery.id=delivery_detail.delivery_id where delivery.is_delivered=true and delivery_detail.product_id=:product_id and date(delivery.delivered_date)=:day group by delivery_detail.product_id;', {"day": i.date(), "product_id": inventory.product_id}).scalar()
                    
                    day_format = (i.day, 0 if day_added is None else int(day_added), 0 if day_expense is None else int(day_expense))
                    days_list.append(day_format)
                    days_data.append(i.day)

                day_total = connection.execute('SELECT total_inventory.quantity as available_quantity, total_inventory.postphoned_quantity as postphoned_quantity, total_inventory.cancelled_quantity as cancelled_quantity, total_inventory.substracted_quantity as substracted_quantity FROM sunsundatabase1.total_inventory as total_inventory where total_inventory.product_id=:product_id;', {"product_id": inventory.product_id }).first()
                data_format.insert(2, (days_list))
                data_format.insert(3, (day_total))
                data_format.insert(4, (inventory.quantity, inventory.postphoned_quantity, inventory.cancelled_quantity, inventory.substracted_quantity))
                final_inventories.append(data_format)

        return render_template('/clerk/inventories.html', supplier=supplier, form=form, inventories=inventories, current_date=current_date, day_list=days_data, final_inventories=final_inventories)
    
    if form.date.data is not None and form.select_supplier.data != 0 and form.validate_on_submit():
        supplier = connection.query(models.User).filter(models.User.id==form.select_supplier.data).first()
        inventories = supplier.total_inventories

        if (form.date.data.day) <= 15:
            for inventory in inventories:
                data_format = [f"%s"%(inventory.total_inventory_product.name.capitalize()), inventory.quantity]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.date.data.year, form.date.data.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.date.data.year, form.date.data.month, 15))):
                    day_added = connection.execute('SELECT sum(inventory.quantity) as total_amount FROM sunsundatabase1.inventory as inventory where inventory.product_id=:product_id and date(inventory.received_date)=:day group by inventory.product_id;', {"day": i.date(), "product_id": inventory.product_id }).scalar()
                    day_expense = connection.execute('SELECT sum(delivery_detail.quantity) as total_amount, delivery_detail.product_id as product_id FROM sunsundatabase1.delivery as delivery join sunsundatabase1.delivery_detail as delivery_detail on delivery.id=delivery_detail.delivery_id where delivery.is_delivered=true and delivery_detail.product_id=:product_id and date(delivery.delivered_date)=:day group by delivery_detail.product_id;', {"day": i.date(), "product_id": inventory.product_id }).scalar()
                    
                    day_format = (i.day, 0 if day_added is None else int(day_added), 0 if day_expense is None else int(day_expense))
                    days_list.append(day_format)
                    days_data.append(i.day)

                day_total = connection.execute('SELECT total_inventory.quantity as available_quantity, total_inventory.postphoned_quantity as postphoned_quantity, total_inventory.cancelled_quantity as cancelled_quantity, total_inventory.substracted_quantity as substracted_quantity FROM sunsundatabase1.total_inventory as total_inventory where total_inventory.product_id=:product_id;', {"product_id": inventory.product_id }).first()    
                data_format.insert(2, (days_list))
                data_format.insert(3, (day_total))
                data_format.insert(4, (inventory.quantity, inventory.postphoned_quantity, inventory.cancelled_quantity, inventory.substracted_quantity))
                final_inventories.append(data_format)
        else:
            for inventory in inventories:
                data_format = [f"%s"%(inventory.total_inventory_product.name.capitalize()), inventory.quantity]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.date.data.year, form.date.data.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.date.data.year, form.date.data.month, calendar.monthrange(form.date.data.year, form.date.data.month)[1]))):
                    day_added = connection.execute('SELECT sum(inventory.quantity) as total_amount FROM sunsundatabase1.inventory as inventory where inventory.product_id=:product_id and date(inventory.received_date)=:day group by inventory.product_id;', {"day": i.date(), "product_id": inventory.product_id}).scalar()
                    day_expense = connection.execute('SELECT sum(delivery_detail.quantity) as total_amount, delivery_detail.product_id as product_id FROM sunsundatabase1.delivery as delivery join sunsundatabase1.delivery_detail as delivery_detail on delivery.id=delivery_detail.delivery_id where delivery.is_delivered=true and delivery_detail.product_id=:product_id and date(delivery.delivered_date)=:day group by delivery_detail.product_id;', {"day": i.date(), "product_id": inventory.product_id}).scalar()
                    
                    day_format = (i.day, 0 if day_added is None else int(day_added), 0 if day_expense is None else int(day_expense))
                    days_list.append(day_format)
                    days_data.append(i.day)

                day_total = connection.execute('SELECT total_inventory.quantity as available_quantity, total_inventory.postphoned_quantity as postphoned_quantity, total_inventory.cancelled_quantity as cancelled_quantity, total_inventory.substracted_quantity as substracted_quantity FROM sunsundatabase1.total_inventory as total_inventory where total_inventory.product_id=:product_id;', {"product_id": inventory.product_id }).first()

                data_format.insert(2, (days_list))
                data_format.insert(3, (day_total))
                data_format.insert(4, (inventory.quantity, inventory.postphoned_quantity, inventory.cancelled_quantity, inventory.substracted_quantity))
                final_inventories.append(data_format)
        
        return render_template('/clerk/inventories.html', supplier=supplier, form=form, inventories=inventories, current_date=form.date.data, day_list=days_data, final_inventories=final_inventories)
        
    return render_template('/clerk/inventories.html', form=form, inventories=inventories, current_date=current_date, day_list=days_data, final_inventories=final_inventories)



@clerk_inventory_blueprint.route('/clerk/supplier2/inventories')
@login_required
@has_role('clerk')
def clerk_inventories_supplier2():
    connection = Connection()
    cancelled_orders = connection.query(models.DriverReturn).filter(or_(models.DriverReturn.delivery_status=="cancelled", models.DriverReturn.delivery_status=="postphoned"), models.DriverReturn.is_returned==True, models.DriverReturn.delivery.has(models.Delivery.order_type=="unstored"), models.DriverReturn.delivery.has(models.Delivery.is_returned==True)).all()
    # postphoned_orders = connection.query(models.DriverReturn).filter(models.DriverReturn.delivery_status=="postphoned", models.DriverReturn.is_returned==True, models.DriverReturn.delivery.has(models.Delivery.order_type=="unstored"), models.DriverReturn.delivery.has(models.Delivery.is_returned==True)).all()
    return render_template('/clerk/supplier2_returned_inventories.html', returned_orders=cancelled_orders)