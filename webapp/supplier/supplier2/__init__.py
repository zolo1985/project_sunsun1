def create_module(app, **kwargs):
    from .order import supplier2_order_blueprint
    from .profile import supplier2_profile_blueprint
    from .stats import supplier2_stats_blueprint
    app.register_blueprint(supplier2_order_blueprint)
    app.register_blueprint(supplier2_profile_blueprint)
    app.register_blueprint(supplier2_stats_blueprint)