def create_module(app, **kwargs):
    from .order import accountant_order_blueprint
    from .profile import accountant_profile_blueprint
    from .drivers import accountant_drivers_blueprint
    app.register_blueprint(accountant_order_blueprint)
    app.register_blueprint(accountant_profile_blueprint)
    app.register_blueprint(accountant_drivers_blueprint)