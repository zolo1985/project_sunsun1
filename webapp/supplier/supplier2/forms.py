from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, HiddenField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Optional, NumberRange


class OrderDetailLocalAddForm(FlaskForm):
    phone = IntegerField('Утасны дугаар', validators=[DataRequired()])
    phone_more = IntegerField('Нэмэлт утасны дугаар', validators=[Optional()])
    district = SelectField('Дүүрэг', choices=[],validators=[DataRequired()])
    khoroo = SelectField('Хороо', choices=[],validators=[DataRequired()])
    address = TextAreaField('Хаяг', validators=[DataRequired()])
    total_amount = IntegerField('Үйлчлэгчээс авах дүн', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Хүргэлт нэмэх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

    def validate_district(self, district):
        if district.data == "0" or district.data == "Дүүрэг сонгох":
            raise ValidationError('Дүүрэг сонгоно уу!')
        else:
            pass

    def validate_khoroo(self, khoroo):
        if khoroo.data == "0" or khoroo.data == "Хороо сонгох":
            raise ValidationError('Хорооны дугаар сонгоно уу!')
        else:
            pass


class OrderDetailLongDistanceAddForm(FlaskForm):
    phone = IntegerField('Утасны дугаар', validators=[DataRequired()])
    phone_more = IntegerField('Нэмэлт утасны дугаар', validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[],validators=[DataRequired()])
    address = TextAreaField('Хаяг', validators=[DataRequired()])
    total_amount = IntegerField('Үйлчлэгчээс авах дүн', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Хүргэлт нэмэх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

    def validate_aimag(self, aimag):
        if aimag.data == "0" or aimag.data == "Аймаг сонгох":
            raise ValidationError('Аймаг сонгоно уу!')
        else:
            pass


class OrderEditForm(FlaskForm):
    phone = StringField('Утасны дугаар', validators=[DataRequired()])
    phone_more = StringField('Нэмэлт утасны дугаар', validators=[DataRequired()])
    district = SelectField('Дүүрэг', choices=[],validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[],validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[],validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[DataRequired()])
    total_amount = IntegerField('Үйлчлэгчээс авах дүн', validators=[InputRequired(), NumberRange(min=0)])
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