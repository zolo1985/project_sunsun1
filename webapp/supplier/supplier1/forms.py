from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Optional, NumberRange, InputRequired
from flask_wtf.file import FileField, FileAllowed
from webapp.database import Connection
from webapp import models


class FiltersForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')

    def validate_date(self, date):
        if date.data is None:
            raise ValidationError("Он сар өдөр сонгоно уу!")


class OrderDetailLocalAddForm(FlaskForm):
    phone = IntegerField('Утасны дугаар', validators=[DataRequired()])
    phone_more = IntegerField('Нэмэлт утасны дугаар', validators=[Optional()])
    district = SelectField('Дүүрэг', choices=[], validators=[DataRequired()])
    khoroo = SelectField('Хороо', choices=[], validators=[DataRequired()])
    aimag = SelectField('Аймаг', choices=[], validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[DataRequired()])
    products = SelectField('Бараа', choices=[], validators=[DataRequired()])
    quantity = IntegerField('Тоо ширхэг', validators=[DataRequired(), NumberRange(min=1)])
    total_amount = IntegerField('Нийт үнэ', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Хүргэлт нэмэх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((str(phone.data)))
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
    products = SelectField('Бараа', choices=[], validators=[DataRequired()])
    quantity = IntegerField('Тоо ширхэг', validators=[DataRequired(), NumberRange(min=1)], id='price')
    total_amount = IntegerField('Нийт үнэ', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Хүргэлт нэмэх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((str(phone.data)))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

    def validate_aimag(self, aimag):
        if aimag.data == "0" or aimag.data == "Аймаг сонгох":
            raise ValidationError('Аймаг сонгоно уу!')
        else:
            pass


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
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

        if name.data != name.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

        connection = Connection()
        product_database = connection.execute('select count(*) from sunsundatabase1.product as product join sunsundatabase1.product_colors as colors on product.id = colors.product_id join sunsundatabase1.product_color as color on colors.product_color_id = color.id join sunsundatabase1.product_sizes as sizes on product.id = sizes.product_id join sunsundatabase1.product_size as size on sizes.product_size_id = size.id where product.name = :product_name and color.id = :color_id and size.id = :size_id',{'product_name': name.data, 'color_id': self.color, 'size_id': self.size}).scalar()
        if product_database>0:
            raise ValidationError('Ийм нэртэй бараа байна!')


class ProductEditForm(FlaskForm):
    name = StringField('Нэр', validators=[DataRequired()])
    description = TextAreaField('Бусад', validators=[Optional()])
    image = FileField('Зураг', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], message='Зөвхөн jpg, jpeg, png өргөтгөлтэй зураг оруулна уу!')], id='image')
    price = IntegerField('Үнэ', validators=[DataRequired(), NumberRange(min=1)], id='price')
    usage_guide = TextAreaField('Хэрэглэх заавар', validators=[Optional()])
    submit = SubmitField('Өөрчлөх')

    def validate_name(self, name):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ0123456789 "))
        validation = set((name.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

        if name.data != name.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

        connection = Connection()
        products = connection.query(models.Product).filter_by(name=name.data).all()
        connection.close()
        if len(products)>1:
            raise ValidationError('Ийм нэртэй бараа байна!')


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
