def create_module(app, **kwargs):
    from .user_profile import manager_profile_blueprint
    from .order import manager_order_blueprint
    from .account import manager_account_blueprint
    from .pickup import manager_pickup_blueprint
    from .dropoff import manager_dropoff_blueprint
    from .analytics import manager_analytics_blueprint
    from .search import manager_search_blueprint
    from .product import manager_product_blueprint

    app.register_blueprint(manager_profile_blueprint)
    app.register_blueprint(manager_order_blueprint)
    app.register_blueprint(manager_account_blueprint)
    app.register_blueprint(manager_pickup_blueprint)
    app.register_blueprint(manager_dropoff_blueprint)
    app.register_blueprint(manager_analytics_blueprint)
    app.register_blueprint(manager_search_blueprint)
    app.register_blueprint(manager_product_blueprint)