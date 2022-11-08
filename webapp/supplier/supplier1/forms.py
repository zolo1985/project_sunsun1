from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed


class FiltersForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')

    def validate_date(self, date):
        if date.data is None:
            raise ValidationError("Он сар өдөр сонгоно уу!")


class OrderDetailLocalAddForm(FlaskForm):
    phone = StringField('Утасны дугаар', validators=[DataRequired()])
    phone_more = StringField('Нэмэлт утасны дугаар', validators=[Optional()])
    district = SelectField('Дүүрэг', choices=[],validators=[DataRequired()])
    khoroo = SelectField('Хороо', choices=[],validators=[DataRequired()])
    aimag = SelectField('Аймаг', choices=[],validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[DataRequired()])
    products = SelectField('Бараа', choices=[], validators=[DataRequired()])
    quantity = IntegerField('Тоо ширхэг', validators=[DataRequired(), NumberRange(min=1)], id='price')
    payment_type = SelectField('Төлбөр', choices=[],validators=[DataRequired()])
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
    products = SelectField('Бараа', choices=[], validators=[DataRequired()])
    quantity = IntegerField('Тоо ширхэг', validators=[DataRequired(), NumberRange(min=1)], id='price')
    payment_type = SelectField('Төлбөр', choices=[],validators=[DataRequired()])
    submit = SubmitField('Хүргэлт нэмэх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')


class OrderDetailFileAddForm(FlaskForm):
    excel_file = FileField('Excel файл оруулах', validators=[DataRequired(), FileAllowed(['xlsx', 'XLSX'], message='Зөвхөн Excel файл оруулна уу!')], id="inputGroupFile02")
    preview_orders = SubmitField('Захиалгууд харах')
    

class SubmitFileOrders(FlaskForm):
    submit = SubmitField('Захиалгууд нэмэх')


class ProductAddForm(FlaskForm):
    name = StringField('Нэр', validators=[DataRequired()])
    color = SelectField('Өнгө', choices=[],validators=[DataRequired()])
    size = SelectField('Хэмжээ', choices=[],validators=[DataRequired()])
    description = TextAreaField('Бусад', validators=[Optional()])
    image = FileField('Зураг', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], message='Зөвхөн jpg, jpeg, png өргөтгөлтэй зураг оруулна уу!')], id='image')
    price = IntegerField('Үнэ', validators=[DataRequired(), NumberRange(min=1)], id='price')
    usage_guide = TextAreaField('Хэрэглэх заавар', validators=[Optional()])
    submit = SubmitField('Бараа бүртгэлд нэмэх')

    def validate_name(self, name):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ0123456789 "))
        validation = set((name.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг, тоо ашиглана уу!')


class ProductEditForm(FlaskForm):
    name = StringField('Нэр', validators=[DataRequired()])
    description = TextAreaField('Бусад', validators=[Optional()])
    image = FileField('Зураг', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], message='Зөвхөн jpg, jpeg, png өргөтгөлтэй зураг оруулна уу!')], id='image')
    price = IntegerField('Үнэ', validators=[DataRequired(), NumberRange(min=1)], id='price')
    usage_guide = TextAreaField('Хэрэглэх заавар', validators=[Optional()])
    submit = SubmitField('Өөрчлөх')

    def validate_name(self, name):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ0123456789"))
        validation = set((name.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг, тоо ашиглана уу!')


class InventoryAddForm(FlaskForm):
    quantity = IntegerField('Тоо ширхэг', validators=[DataRequired(), NumberRange(min=1)], id='quantity')
    product = SelectField('Бараа', choices=[],validators=[DataRequired()])
    choose_receiver = SelectField('Хүлээн авсан', choices=[],validators=[DataRequired()])
    submit = SubmitField('Хүлээлгэж өгөх')

class DriverPickupForm(FlaskForm):
    pickup_id = HiddenField()
    submit = SubmitField('Хүлээлгэж өгөх')


class InventoryPickupAddForm(FlaskForm):
    quantity = IntegerField('Тоо ширхэг', validators=[DataRequired(), NumberRange(min=1)], id='quantity')
    product = SelectField('Бараа', choices=[],validators=[DataRequired()])
    submit = SubmitField('Жолооч дуудах')

class ChooseType(FlaskForm):
    choose_type = SelectField('Төрөл сонгох', choices=[],validators=[DataRequired()])
    submit = SubmitField('Сонгох')

class SelectOption(FlaskForm):
    select_option = SelectField('Хугацаа сонгох', choices=[],validators=[DataRequired()])
    submit = SubmitField('Сонгох')
