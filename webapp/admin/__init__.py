from flask_admin import Admin, helpers as admin_helpers
from .admin_auth import MyAdminIndexView, CustomModelView, UserView, SignOutMenuLink, DeliveryView, PickupTaskView
from webapp.database import Connection
from webapp.models import Delivery, PickupTask, User, Product, ProductColor, ProductSize, Region, Address, Role


admin = Admin(static_url_path='/admin/static', index_view=MyAdminIndexView(url='/admin/admin'), base_template='adminlayout.html', template_mode='bootstrap4')

def create_module(app, **kwargs):
    admin.init_app(app)
    admin.add_view(UserView(User, Connection, category='Хэрэглэгч'))
    admin.add_view(DeliveryView(Delivery, Connection, category='Хүргэлт'))
    admin.add_view(PickupTaskView(PickupTask, Connection, category='Таталт'))
    admin.add_link(SignOutMenuLink(name='Гарах', category='', url="/admin/logout"))

    models = [Product, ProductColor, ProductSize]

    for model in models:
        admin.add_view(CustomModelView(model, Connection, category='Бараа'))

    models1 = [Region, Address, Role]

    for model in models1:
        admin.add_view(CustomModelView(model, Connection, category='Бусад'))
    