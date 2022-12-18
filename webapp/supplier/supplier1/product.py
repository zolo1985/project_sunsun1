from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import ProductAddForm, ProductEditForm
from datetime import datetime
from webapp.utils import add_and_resize_image
import pytz

supplier1_product_blueprint = Blueprint('supplier1_product', __name__)


@supplier1_product_blueprint.route('/supplier1/products', methods=['GET', 'POST'])
@login_required
@has_role('supplier1')
def supplier1_products():
    products = current_user.products
    return render_template('/supplier/supplier1/products.html', products=products)


@supplier1_product_blueprint.route('/supplier1/products/add', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_product_add():
    connection = Connection()
    colors = connection.query(models.ProductColor).all()
    sizes = connection.query(models.ProductSize).all()
    
    form = ProductAddForm()
    form.color.choices = [(color.id, color.name) for color in colors]
    form.size.choices = [(size.id, size.name) for size in sizes]

    if form.validate_on_submit():
        try:
            line_names = request.form.getlist("name")
            line_colors = request.form.getlist("color")
            line_sizes = request.form.getlist("size")
            line_descriptions = request.form.getlist("description")
            line_prices = request.form.getlist("price")
            line_usage_guides = request.form.getlist("usage_guide")
            line_images = request.files.getlist("image")

            for i, name in enumerate(line_names):
                product = models.Product()
                product.name = name
                product.price = line_prices[i]
                product.description = line_descriptions[i]
                product.usage_guide = line_usage_guides[i]
                product.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                product.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                if not line_images[i].filename == '':
                    product.image = add_and_resize_image(line_images[i]),
                
                product.colors.append(connection.query(models.ProductColor).get(line_colors[i]))
                product.sizes.append(connection.query(models.ProductSize).get(line_sizes[i]))
                current_user.products.append(product)
                connection.flush()

                total_inventory = models.TotalInventory()
                total_inventory.quantity = 0
                total_inventory.product_id = product.id
                total_inventory.user_id = current_user.id
                total_inventory.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                total_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                connection.add(total_inventory)
                connection.commit()

        except Exception as ex:
            flash(f'%s'%(ex), 'danger')
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            connection.close()
            return redirect(request.url)
        else:
            flash('Шинэ бараа агуулахад амжилттай нэмэгдлээ.', 'success')
            return redirect(url_for('supplier1_product.supplier1_products'))
    return render_template('/supplier/supplier1/product_add.html', form=form)


@supplier1_product_blueprint.route('/supplier1/products/edit/<int:product_id>', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_product_edit(product_id):
    connection = Connection()
    product = connection.query(models.Product).get(product_id)

    if product is None:
        flash('Бараа олдсонгүй!', 'danger')
        connection.close()
        return redirect(url_for('supplier1_product.supplier1_products'))

    if product.supplier_id != current_user.id:
        abort(403)

    colors = connection.query(models.ProductColor).all()
    sizes = connection.query(models.ProductSize).all()

    form = ProductEditForm()
    form.color.choices = [(color.id, color.name) for color in colors]
    form.size.choices = [(size.id, size.name) for size in sizes]

    if form.validate_on_submit():
        update_product = connection.query(models.Product).filter(models.Product.id==product.id).first()
        update_product.name = form.name.data
        update_product.price = form.price.data
        update_product.description = form.description.data
        update_product.usage_guide = form.usage_guide.data
        update_product.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        update_product.colors.clear()
        update_product.sizes.clear()
        update_product.colors.append(connection.query(models.ProductColor).get(form.color.data))
        update_product.sizes.append(connection.query(models.ProductSize).get(form.size.data))
        image_file = request.files['image']
        if image_file:
            update_product.image = add_and_resize_image(form.image.data),

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(request.url)
        else:
            connection.close()
            flash('Бараа засагдлаа.', 'info')
            return redirect(url_for('supplier1_product.supplier1_products'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.description.data = product.description
        form.usage_guide.data = product.usage_guide
    connection.close()
    return render_template('/supplier/supplier1/product_edit.html', form=form)
