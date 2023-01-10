from flask import (Blueprint, render_template, flash, redirect, url_for, abort, request)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from .forms import NewAccountForm, EditAccountForm
from webapp import bcrypt
import pytz

manager_account_blueprint = Blueprint('manager_account', __name__)

@manager_account_blueprint.route('/manager/accounts', methods=['GET'])
@login_required
@has_role('manager')
def manager_accounts():
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
    clerks = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="clerk")).all()
    accountants = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="accountant")).all()
    supplier1s = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier1")).all()
    supplier2s = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier2")).all()
    return render_template('/manager/accounts.html', drivers=drivers, clerks=clerks, accountants=accountants, supplier1s=supplier1s, supplier2s=supplier2s)



@manager_account_blueprint.route('/manager/accounts/edit/<int:account_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_account(account_id):

    connection = Connection()
    account = connection.query(models.User).get(account_id)

    if account is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        
    form = EditAccountForm()

    if form.validate_on_submit():
        account_to_update = connection.query(models.User).get(account_id)
        account_to_update.email = form.email.data
        account_to_update.phone = form.phone.data
        account_to_update.fee = form.fee.data

        try:
            connection.commit()
        except:
            connection.rollback()
            connection.close()
            flash('Алдаа гарлаа', 'danger')
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Мэдээлэл өөрчлөгдлөө', 'success')
            return redirect(url_for('manager_account.manager_accounts'))

    elif request.method == 'GET':
        form.email.data = account.email
        form.phone.data = account.phone
        form.fee.data = account.fee
        return render_template('/manager/account.html', form=form, account=account)
    return render_template('/manager/account.html', form=form, account=account)



@manager_account_blueprint.route('/manager/drivers/authorize/<int:driver_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_driver_authorize(driver_id):
    connection = Connection()
    user = connection.query(models.User).get(driver_id)

    if user.has_role('driver'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        connection.close()
        abort(403)


@manager_account_blueprint.route('/manager/supplier1/authorize/<int:supplier1_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_supplier1_authorize(supplier1_id):
    connection = Connection()
    user = connection.query(models.User).get(supplier1_id)

    if user.has_role('supplier1'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        connection.close()
        abort(403)



@manager_account_blueprint.route('/manager/supplier2/authorize/<int:supplier2_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_supplier2_authorize(supplier2_id):
    connection = Connection()
    user = connection.query(models.User).get(supplier2_id)

    if user.has_role('supplier2'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        connection.close()
        abort(403)


@manager_account_blueprint.route('/manager/account/password-reset/<int:user_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_account_password_reset(user_id):
    connection = Connection()
    user = connection.query(models.User).get(user_id)

    if user:
        try:
            hashed_password = bcrypt.generate_password_hash("password")
            user.password = hashed_password
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Нууц үг password болж өөрчлөгдлөө.', 'success')
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        connection.close()
        abort(403)


def switch_role(role):
    if role == "Харилцагч(агуулахтай)":
        return "supplier1"
    elif role == "Харилцагч(агуулахгүй)":
        return "supplier2"
    elif role == "Жолооч":
        return "driver"


@manager_account_blueprint.route('/manager/accounts/add-account', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_add_account():
    form = NewAccountForm()
    connection = Connection()
    roles_selection = ['Харилцагч(агуулахтай)', 'Харилцагч(агуулахгүй)', 'Жолооч']
    form.select_user_role.choices = [(role) for role in roles_selection]
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            user = models.User()
            user.company_name = form.company_name.data.lower()
            user.firstname = form.firstname.data.lower()
            user.lastname = form.lastname.data.lower()
            user.password = hashed_password
            user.status = "verified"
            user.email = form.email.data
            user.phone = form.phone.data
            user_role = connection.query(models.Role).filter_by(name=switch_role(form.select_user_role.data)).first()
            user.roles.append(user_role)
            user.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            user.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            user.is_authorized = True
            connection.add(user)
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_account.manager_add_account'))
        else:
            flash('Шинэ данс үүслээ баталгаажуулах и-мэйл илгээлээ.', 'success')
            connection.close()
            return redirect(url_for('manager_account.manager_add_account'))

    return render_template('/manager/new_account.html', form=form)


@manager_account_blueprint.route('/manager/account/is-invoiced/<int:user_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_account_is_invoiced(user_id):
    connection = Connection()
    user = connection.query(models.User).get(user_id)

    if user:
        try:
            if user.is_invoiced:
                user.is_invoiced = False
            else:
                user.is_invoiced = True

            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            if user.is_invoiced:
                flash(f'%s нэхэмжилдэггүй боллоо.'%(user.company_name), 'success')
            else:
                flash(f'%s нэхэмжилдэг боллоо.'%(user.company_name), 'success')
            connection.close()
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        connection.close()
        flash('Хэрэглэгч олдсонгүй!', 'danger')
        return redirect(url_for('manager_account.manager_accounts'))


