def create_module(app, **kwargs):
    from .account import admin_account_blueprint
    from .user_profile import admin_profile_blueprint

    app.register_blueprint(admin_account_blueprint)
    app.register_blueprint(admin_profile_blueprint)