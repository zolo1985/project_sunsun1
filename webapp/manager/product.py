from flask import (Blueprint, render_template, flash)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import AddColorForm, AddSizeForm

manager_product_blueprint = Blueprint('manager_product', __name__)

@manager_product_blueprint.route('/manager/product/add-color', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_product_add_color():
    connection = Connection()
    form = AddColorForm()
    colors = connection.query(models.ProductColor).all()

    if form.validate_on_submit():
        is_color = connection.query(models.ProductColor).filter(models.ProductColor.name==form.color_name.data.strip()).first()

        if is_color:
            flash('Өнгө бүртгэлтэй байна.', 'info')
            connection.close()
            return render_template('/manager/add_color.html', colors=colors, form=form)
        else:
            color = models.ProductColor(name=form.color_name.data.strip())
            
            try:
                connection.add(color)
                connection.commit()
            except Exception as e:
                flash('Алдаа гарлаа!', 'danger')
                connection.rollback()
            else:
                flash('Өнгө нэмэгдлээ.', 'success')
                return render_template('/manager/add_color.html', colors=colors, form=form)

    return render_template('/manager/add_color.html', colors=colors, form=form)



@manager_product_blueprint.route('/manager/product/add-size', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_product_add_size():
    connection = Connection()
    form = AddSizeForm()
    sizes = connection.query(models.ProductSize).all()

    if form.validate_on_submit():
        is_size = connection.query(models.ProductSize).filter(models.ProductSize.name==form.size_name.data.strip()).first()

        if is_size:
            flash('Хэмжээ бүртгэлтэй байна.', 'info')
            connection.close()
            return render_template('/manager/add_size.html', sizes=sizes, form=form)
        else:
            size = models.ProductSize(name=form.size_name.data.strip())
            
            try:
                connection.add(size)
                connection.commit()
            except Exception as e:
                flash('Алдаа гарлаа!', 'danger')
                connection.rollback()
            else:
                flash('Хэмжээ нэмэгдлээ.', 'success')
                return render_template('/manager/add_size.html', sizes=sizes, form=form)

    return render_template('/manager/add_size.html', sizes=sizes, form=form)