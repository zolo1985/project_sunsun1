from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Optional

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
    select_supplier = SelectField('Харилцагч', choices=[], validators=[DataRequired()])
    submit = SubmitField('Шүүх')