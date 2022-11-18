from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, HiddenField
from wtforms.validators import ValidationError, DataRequired, StopValidation, Optional, NumberRange
from werkzeug.datastructures import FileStorage
from flask_wtf.file import FileField, FileAllowed
from collections.abc import Iterable


class OrderDetailLocalAddForm(FlaskForm):
    phone = StringField('Утасны дугаар', validators=[DataRequired()])
    phone_more = StringField('Нэмэлт утасны дугаар', validators=[Optional()])
    district = SelectField('Дүүрэг', choices=[],validators=[DataRequired()])
    khoroo = SelectField('Хороо', choices=[],validators=[DataRequired()])
    address = TextAreaField('Хаяг', validators=[DataRequired()])
    total_amount = IntegerField('Үйлчлэгчээс авах дүн', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Хүргэлт нэмэх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')


class OrderDetailLongDistanceAddForm(FlaskForm):
    phone = StringField('Утасны дугаар', validators=[DataRequired()])
    phone_more = StringField('Нэмэлт утасны дугаар', validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[],validators=[DataRequired()])
    address = TextAreaField('Хаяг', validators=[DataRequired()])
    total_amount = IntegerField('Үйлчлэгчээс авах дүн', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Хүргэлт нэмэх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')


class OrderEditForm(FlaskForm):
    phone = StringField('Утасны дугаар', validators=[DataRequired()])
    phone_more = StringField('Нэмэлт утасны дугаар', validators=[DataRequired()])
    district = SelectField('Дүүрэг', choices=[],validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[],validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[],validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[DataRequired()])
    total_amount = IntegerField('Нийт дүн', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Өөрчлөх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

class TransferForm(FlaskForm):
    order_id = HiddenField()
    inventory_id = HiddenField()
    submit = SubmitField('Хүлээлгэж өгөх')

class DateSelectForm(FlaskForm):
    select_date = DateField('Он Сар', validators=[Optional()])
    submit = SubmitField('Сонгох')