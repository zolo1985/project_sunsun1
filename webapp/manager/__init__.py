def create_module(app, **kwargs):
    from .profile import manager_profile_blueprint
    from .order import manager_order_blueprint
    from .account import manager_account_blueprint
    from .pickup import manager_pickup_blueprint
    from .driver_stats import manager_driver_stats_blueprint
    from .analytics import manager_analytics_blueprint

    app.register_blueprint(manager_profile_blueprint)
    app.register_blueprint(manager_order_blueprint)
    app.register_blueprint(manager_account_blueprint)
    app.register_blueprint(manager_pickup_blueprint)
    app.register_blueprint(manager_driver_stats_blueprint)
    app.register_blueprint(manager_analytics_blueprint)