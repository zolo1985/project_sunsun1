def create_module(app, **kwargs):
    from .job import driver_job_blueprint
    from .user_profile import driver_profile_blueprint

    app.register_blueprint(driver_job_blueprint)
    app.register_blueprint(driver_profile_blueprint)