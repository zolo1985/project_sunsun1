def create_module(app, **kwargs):
    from .order import supplier1_order_blueprint
    from .util import supplier1_util_blueprint
    from .product import supplier1_product_blueprint
    from .inventory import supplier1_inventory_blueprint
    from .expense import supplier1_expense_blueprint
    from .user_profile import supplier1_profile_blueprint
    from .stats import supplier1_stats_blueprint
    app.register_blueprint(supplier1_order_blueprint)
    app.register_blueprint(supplier1_util_blueprint)
    app.register_blueprint(supplier1_product_blueprint)
    app.register_blueprint(supplier1_inventory_blueprint)
    app.register_blueprint(supplier1_expense_blueprint)
    app.register_blueprint(supplier1_profile_blueprint)
    app.register_blueprint(supplier1_stats_blueprint)
