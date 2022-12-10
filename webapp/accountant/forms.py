from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import Length, Email, EqualTo, ValidationError, DataRequired, Optional, NumberRange, InputRequired


class FiltersForm(FlaskForm):
    order_id = HiddenField()
    drivers = SelectField('Жолоочийн нэр', choices=[], validators=[DataRequired()])
    submit = SubmitField('Сонгох')

class ReceivePaymentForm(FlaskForm):
    order_id = HiddenField()
    net_amount = HiddenField()
    cash_amount = IntegerField('Бэлнээр', validators=[Optional(), NumberRange(min=0)], id='price')
    card_amount = IntegerField('Дансаар', validators=[Optional(), NumberRange(min=0)], id='price')
    remaining_amount = IntegerField('Үлдэгдэл', validators=[Optional(), NumberRange(min=0)], id='price')
    comment = TextAreaField('Тэмдэглэгээ', validators=[Optional()])
    submit = SubmitField('Тооцоо хийх')

class PaymentReceived(FlaskForm):
    submit = SubmitField('Тооцоогүй болгох')

class DateSelect(FlaskForm):
    select_date = DateField('Хугацаа сонгох', validators=[Optional()])
    submit = SubmitField('Сонгох')

class SearchForm(FlaskForm):
    search_text = StringField('Хайх', validators=[DataRequired(), Length(min=2, max=50, message='Нэр 2-50 урттай')])
    submit = SubmitField('Хайх')