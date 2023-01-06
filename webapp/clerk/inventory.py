from flask import (Blueprint, render_template, request, jsonify, flash, url_for, redirect)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from sqlalchemy import func, or_
from .forms import SupplierChooseForm, SuppliersOnlyForm
from webapp import models
from datetime import datetime
from flask_login import current_user
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

        if current_date.day <= 15:
            for inventory in inventories:
                data_format = [f"%s (%s, %s)"%(inventory.total_inventory_product.name.capitalize(), inventory.total_inventory_product.colors[0], inventory.total_inventory_product.sizes[0]), inventory.quantity]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 15))):
                    day_added = connection.execute('SELECT sum(inventory.quantity) as total_amount FROM sunsundatabase1.inventory as inventory where inventory.product_id=:product_id and date(inventory.received_date)=:day and inventory.status=true group by inventory.product_id;', {"day": i.date(), "product_id": inventory.product_id }).scalar()
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
                data_format = [f"%s (%s, %s)"%(inventory.total_inventory_product.name.capitalize(), inventory.total_inventory_product.colors[0], inventory.total_inventory_product.sizes[0]), inventory.quantity]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]))):
                    day_added = connection.execute('SELECT sum(inventory.quantity) as total_amount FROM sunsundatabase1.inventory as inventory where inventory.product_id=:product_id and date(inventory.received_date)=:day and inventory.status=true group by inventory.product_id;', {"day": i.date(), "product_id": inventory.product_id}).scalar()
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
                data_format = [f"%s (%s, %s)"%(inventory.total_inventory_product.name.capitalize(), inventory.total_inventory_product.colors[0], inventory.total_inventory_product.sizes[0]), inventory.quantity]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.date.data.year, form.date.data.month, "01")), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.date.data.year, form.date.data.month, 15))):
                    day_added = connection.execute('SELECT sum(inventory.quantity) as total_amount FROM sunsundatabase1.inventory as inventory where inventory.product_id=:product_id and date(inventory.received_date)=:day and inventory.status=true group by inventory.product_id;', {"day": i.date(), "product_id": inventory.product_id }).scalar()
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
                data_format = [f"%s (%s, %s)"%(inventory.total_inventory_product.name.capitalize(), inventory.total_inventory_product.colors[0], inventory.total_inventory_product.sizes[0]), inventory.quantity]
                days_list = []
                days_data = []
                for i in rrule(DAILY , dtstart=datetime.fromisoformat(f'%s-%02d-%s'%(form.date.data.year, form.date.data.month, 16)), until=datetime.fromisoformat(f'%s-%02d-%s'%(form.date.data.year, form.date.data.month, calendar.monthrange(form.date.data.year, form.date.data.month)[1]))):
                    day_added = connection.execute('SELECT sum(inventory.quantity) as total_amount FROM sunsundatabase1.inventory as inventory where inventory.product_id=:product_id and date(inventory.received_date)=:day and inventory.status=true group by inventory.product_id;', {"day": i.date(), "product_id": inventory.product_id}).scalar()
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



# @clerk_inventory_blueprint.route('/clerk/supplier1/inventories/return', methods=['GET', 'POST'])
# @login_required
# @has_role('clerk')
# def clerk_inventories_return():
#     current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
#     connection = Connection()
#     suppliers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier1")).filter(models.User.is_authorized==True).all()

#     form = SuppliersOnlyForm()
#     form.select_supplier.choices = [(supplier.id, f'%s'%(supplier.company_name)) for supplier in suppliers]
#     form.select_supplier.choices.insert(0,(0,'Харилцагч сонгох'))
#     inventories=[]

#     if form.validate_on_submit():
#         line_suppliers = request.form.getlist("supplier")
#         line_products = request.form.getlist("product")
#         line_quantities = request.form.getlist("quantity")

#         for i, supplier_id in enumerate(line_suppliers):

#             for i, supplier_id in enumerate(line_suppliers):
#                 supplier = connection.query(models.User).filter(models.User.id==supplier_id).first()
#                 is_supplier_product = connection.query(models.Product).filter(models.Product.supplier_id==supplier.id, models.Product.id==int(line_products[i])).first()

#                 warehouse_quantity = connection.execute('SELECT SUM(quantity) as quantity FROM sunsundatabase1.total_inventory inventory join sunsundatabase1.product product on product.id=inventory.product_id where product.supplier_id=:current_user and product.id=:product_id group by product_id;', {'current_user': supplier_id, 'product_id': int(line_products[i])}).scalar()
                    
#                 if int(warehouse_quantity) < int(line_quantities[i]):
#                     flash(f'Агуулахад байгаа барааны тоо хүрэхгүй байна', 'danger')
#                     return redirect(url_for('clerk_inventory.clerk_inventories_return'))

#                 if is_supplier_product:
#                     total_product_inventory = connection.query(models.TotalInventory).filter_by(product_id=line_products[i]).first()
#                     inventory = models.Inventory()
#                     inventory.quantity = -abs(int(line_quantities[i]))
#                     inventory.inventory_type = "stored"
#                     inventory.status = True
#                     inventory.product_id = line_products[i]
#                     inventory.is_returned_to_supplier = True
#                     inventory.clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
#                     inventory.clerk_id = current_user.id
#                     inventory.supplier_id = int(supplier_id)
#                     inventory.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#                     inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

#                     total_product_inventory.quantity = total_product_inventory.quantity-int(line_quantities[i])
#                     total_product_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#                     total_product_inventory.total_inventories.append(inventory)

#                 else:
#                     flash('Зарим барааг буруу оруулсан байна!', 'danger')
#                     continue

#             try:
#                 connection.commit()
#             except:
#                 flash('Алдаа гарлаа!', 'danger')
#                 connection.rollback()
#                 return redirect(url_for('clerk_inventory.clerk_inventories_return'))
#             else:
#                 flash('Бараанууд агуулахаас хасагдлаа.', 'success')
#                 return redirect(url_for('clerk_inventory.clerk_inventories_return'))

#         return render_template('/clerk/supplier1_clerk_returned_inventories.html', form=form, inventories=inventories, current_date = current_date)

#     return render_template('/clerk/supplier1_clerk_returned_inventories.html', form=form, inventories=inventories, current_date = current_date)



@clerk_inventory_blueprint.route("/clerk/supplier1/search/products/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_search_products(supplier_id):

    query = request.form.get("term")
    connection = Connection()
    search = "%{}%".format(query)
    products = connection.query(models.Product).filter(models.Product.supplier_id==supplier_id,models.Product.name.like(search)).all()
    results = []

    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'supplier': product.supplier.company_name,
            'color': str(product.colors[0]),
            'size': str(product.sizes[0]),
            'quantity': int(connection.query(models.TotalInventory.quantity).filter(models.TotalInventory.product_id==product.id).scalar()),
            'price': int(product.price),
        })
    return jsonify(results)



@clerk_inventory_blueprint.route('/clerk/supplier2/inventories', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_inventories_supplier2():

    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    connection = Connection()
    suppliers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier2")).filter(models.User.is_authorized==True).all()
    form = SupplierChooseForm()
    form.select_supplier.choices = [(supplier.id, f'%s'%(supplier.company_name)) for supplier in suppliers]
    form.select_supplier.choices.insert(0,(0,'Харилцагч сонгох'))
    orders=[]

    if form.validate_on_submit():
        if form.date.data is None:
            orders = connection.query(models.DriverReturn).filter(or_(models.DriverReturn.delivery_status=="cancelled", models.DriverReturn.delivery_status=="postphoned"), models.DriverReturn.is_returned==True, func.date(models.DriverReturn.returned_date) == current_date, models.DriverReturn.delivery.has(models.Delivery.order_type=="unstored"), models.DriverReturn.delivery.has(models.Delivery.is_returned==True), models.DriverReturn.delivery.has(models.Delivery.user_id==form.select_supplier.data)).all()
            return render_template('/clerk/supplier2_driver_returned_inventories.html', orders=orders, form=form, current_date = current_date)
        if form.date.data is not None:
            orders = connection.query(models.DriverReturn).filter(or_(models.DriverReturn.delivery_status=="cancelled", models.DriverReturn.delivery_status=="postphoned"), models.DriverReturn.is_returned==True, func.date(models.DriverReturn.returned_date) == form.date.data, models.DriverReturn.delivery.has(models.Delivery.order_type=="unstored"), models.DriverReturn.delivery.has(models.Delivery.is_returned==True), models.DriverReturn.delivery.has(models.Delivery.user_id==form.select_supplier.data)).all()
            return render_template('/clerk/supplier2_driver_returned_inventories.html', orders=orders, form=form, current_date = current_date)

    return render_template('/clerk/supplier2_driver_returned_inventories.html', orders=orders, form=form, current_date = current_date)