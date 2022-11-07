from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from webapp.auth.forms import SignInForm
from webapp.database import Connection
from webapp import models
from webapp.utils import generate_confirmation_token


auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/signin', methods=['GET','POST'])
def signin():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = SignInForm()

    if form.validate_on_submit():
        connection = Connection()
        user = connection.query(models.User).filter_by(email=form.email.data).first()
        if user:
            if user.status == "unverified" and user.check_password(form.password.data):
                token = generate_confirmation_token(user.email)
                # send_confirmation_email.delay(user.email, token)
                flash('Та имэйлээр ирсэн линкээр хаягаа баталгаажуулна уу!', 'info')
                connection.close()
            elif user.is_authorized == False and user.check_password(form.password.data):
                flash('Таны данс хаагдсан байна. Менежертэй холбогдоно уу!', 'info')
                connection.close()
            else:
                if user.check_password(form.password.data):
                    login_user(user)
                    connection.close()
                    flash(f"Сайна байна уу %s!"%(user.firstname), category="success")
                    return redirect(url_for('main.home'))
                else:
                    flash('Хэрэглэгч олдсонгүй!', 'danger')
                    connection.close()
            connection.close()
        else:
            flash('Хэрэглэгч олдсонгүй!', 'danger')
            connection.close()

    return render_template('/auth/signin.html', form=form, title='Нэвтрэх')


@auth_blueprint.route('/signout', methods=['GET','POST'])   
@login_required
def signout():
    logout_user()
    return redirect(url_for('main.home'))