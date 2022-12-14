from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField, TextAreaField, RadioField
from wtforms.validators import Length, Email, EqualTo, ValidationError, InputRequired, Optional, NumberRange, InputRequired
from webapp.database import Connection
from webapp import models
from datetime import datetime
import re
import pytz

class FiltersForm(FlaskForm):
    order_id = HiddenField()
    drivers = SelectField('Жолоочийн нэр', choices=[], validators=[Optional()])
    submit = SubmitField('Сонгох')

class DriverOrders(FlaskForm):
    submit = SubmitField('Бүх хүргэлтийг хүлээлгэж өгөх')

class ReceiveInventoryForm(FlaskForm):
    pickup_task_id = HiddenField()
    date = DateField('Он сар', validators=[Optional()])
    submit = SubmitField('Сонгох')

class FilterDateForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')


class SupplierChooseForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    select_supplier = SelectField('Харилцагч', choices=[], validators=[InputRequired()])
    submit = SubmitField('Шүүх')

class SuppliersOnlyForm(FlaskForm):
    select_supplier = SelectField('Харилцагч', choices=[], validators=[InputRequired()])
    submit = SubmitField('Агуулахаас Хасах')


class SearchForm(FlaskForm):
    search_text = StringField('Хайх', validators=[InputRequired(), Length(min=2, max=50, message='Нэр 2-50 урттай')])
    submit = SubmitField('Хайх')

class PasswordChangeForm(FlaskForm):
    user_id = HiddenField()
    current_password = StringField('Одоо хэрэглэж байгаа нууц үг', validators=[InputRequired()])
    password = StringField('Шинэ нууц үг', validators=[InputRequired()])
    confirm_password = StringField('Дахин нууц үг', validators=[InputRequired()])
    submit = SubmitField('Нууц үг өөрчлөх')

    def validate_password(self, password):
        flag = 0
        while True:  
            if (len(password.data)<8):
                flag = -1
                raise ValidationError('Нууц үг хамгийн багадаа 8 тэмдэгтэй!')
            elif not re.search("[a-z]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 жижиг үсэг оролцуулсан байх ёстой!')
            elif not re.search("[A-Z]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 том үсэг оролцуулсан байх ёстой!')
            elif not re.search("[0-9]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 тоо оролцуулсан байх ёстой!')
            elif not re.search("[_@$!]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа _, @, $, ! аль нэгийг тусгай тэмдэгтийг оролцуулсан байх ёстой!')
            elif re.search("\s", password.data):
                flag = -1
                raise ValidationError('Урд хойно хоосон зай ашигласан байна! Арилгана уу!')
            else:
                flag = 0
                break
        
        if flag ==-1:
            pass

        if password.data != password.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_password_again(self, confirm_password, password):
        if password.data != confirm_password.data:
            raise ValidationError('Нууц үгнүүд таарахгүй байна!')


class PasswordChangeForm(FlaskForm):
    user_id = HiddenField()
    current_password = PasswordField('Одоо хэрэглэж байгаа нууц үг', validators=[InputRequired(), Length(min=6, max=255, message='Хэт богино байна!')])
    password = PasswordField('Шинэ нууц үг', validators=[InputRequired(), Length(min=6, max=255, message='Хэт богино байна!')])
    confirm_password = PasswordField('Дахин шинэ нууц үг', validators=[InputRequired(), Length(min=6, max=255, message='Хэт богино байна!')])
    submit = SubmitField('Нууц үг өөрчлөх')

    def validate_password(self, password):
        flag = 0
        while True:  
            if (len(password.data)<8):
                flag = -1
                raise ValidationError('Нууц үг хамгийн багадаа 8 тэмдэгтэй!')
            elif not re.search("[a-z]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 жижиг үсэг оролцуулсан байх ёстой!')
            elif not re.search("[A-Z]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 том үсэг оролцуулсан байх ёстой!')
            elif not re.search("[0-9]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 тоо оролцуулсан байх ёстой!')
            elif not re.search("[_@$!]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа _, @, $, ! аль нэгийг тусгай тэмдэгтийг оролцуулсан байх ёстой!')
            elif re.search("\s", password.data):
                flag = -1
                raise ValidationError('Урд хойно хоосон зай ашигласан байна! Арилгана уу!')
            else:
                flag = 0
                break
        
        if flag ==-1:
            pass

        if password.data != password.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_password_again(self, confirm_password, password):
        if password.data != confirm_password.data:
            raise ValidationError('Нууц үгнүүд таарахгүй байна!')