def create_module(app, **kwargs):
    from .inventory import clerk_inventory_blueprint
    from .receive import clerk_receive_blueprint
    from .expense import clerk_expense_blueprint
    from .returns import clerk_returns_blueprint
    from .profile import clerk_profile_blueprint
    app.register_blueprint(clerk_inventory_blueprint)
    app.register_blueprint(clerk_receive_blueprint)
    app.register_blueprint(clerk_expense_blueprint)
    app.register_blueprint(clerk_returns_blueprint)
    app.register_blueprint(clerk_profile_blueprint)