from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import Length, Email, EqualTo, ValidationError, InputRequired, Optional, NumberRange, InputRequired

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