def create_module(app, **kwargs):
    from .driver_salary import accountant_driver_salary_blueprint
    from .driver_payment import accountant_driver_payment_blueprint
    from .supplier_calculation import accountant_supplier_calculation_blueprint
    from .payment_history import accountant_payment_history_blueprint
    from .search import accountant_search_blueprint
    from .user_profile import accountant_profile_blueprint

    app.register_blueprint(accountant_profile_blueprint)
    app.register_blueprint(accountant_driver_salary_blueprint)
    app.register_blueprint(accountant_driver_payment_blueprint)
    app.register_blueprint(accountant_supplier_calculation_blueprint)
    app.register_blueprint(accountant_payment_history_blueprint)
    app.register_blueprint(accountant_search_blueprint)