from flask_admin import expose, AdminIndexView
from flask_login import login_required, current_user, logout_user, login_user
from flask import redirect, url_for, flash
from webapp.models import User
from webapp.database import Connection
from .forms import SignInForm
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import current_user
from flask import flash
from .forms import CKTextAreaField

from webapp import has_role

class MyAdminIndexView(AdminIndexView):

    @expose('/')
    @login_required
    @has_role('admin')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.signin_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/signin/', methods=('GET', 'POST'))
    def signin_view(self):
        form = SignInForm()
        if form.validate_on_submit():
            connection = Connection()
            account = connection.query(User).filter_by(email=form.email.data).first()
            if account.has_role('admin'):
                if account.status == "unverified" and account.check_password(form.password.data):
                    flash('Та имэйлээр ирсэн линкээр хаягаа баталгаажуулна уу!', 'info')
                    connection.close()
                else:
                    if account.check_password(form.password.data):
                        login_user(account)
                        connection.close()
                        flash("Сайна байна уу!", category="success")
                        return super(MyAdminIndexView, self).index()
                    else:
                        flash('Хэрэглэгч олдсонгүй!', 'danger')
                        connection.close()
                        return self.render('admin/signin.html', form=form)
            else:
                flash('Хэрэглэгч олдсонгүй!', 'danger')
                connection.close()
                return self.render('admin/signin.html', form=form)
        return self.render('admin/signin.html', form=form)

    @expose('/logout/')
    @login_required
    def logout_view(self):
        logout_user()
        return redirect(url_for('admin.signin_view'))

class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

class CustomModelView2(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

class UserView(CustomModelView):
    column_searchable_list = ['email', 'phone']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

class DeliveryView(CustomModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

class PickupTaskView(CustomModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

class SignOutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')