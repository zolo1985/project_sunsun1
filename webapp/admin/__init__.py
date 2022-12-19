def create_module(app, **kwargs):
    from .account import admin_account_blueprint
    from .user_profile import admin_profile_blueprint
    from .order import admin_order_blueprint
    from .stats import admin_stats_blueprint
    from .supplier_balance import admin_supplier_balance_blueprint
    from .search import admin_search_blueprint

    app.register_blueprint(admin_account_blueprint)
    app.register_blueprint(admin_profile_blueprint)
    app.register_blueprint(admin_order_blueprint)
    app.register_blueprint(admin_stats_blueprint)
    app.register_blueprint(admin_supplier_balance_blueprint)
    app.register_blueprint(admin_search_blueprint)
    