def create_module(app, **kwargs):
    from .order import supplier2_order_blueprint
    from .user_profile import supplier2_profile_blueprint
    from .stats import supplier2_stats_blueprint
    from .returns import supplier2_return_blueprint
    app.register_blueprint(supplier2_order_blueprint)
    app.register_blueprint(supplier2_profile_blueprint)
    app.register_blueprint(supplier2_stats_blueprint)
    app.register_blueprint(supplier2_return_blueprint)