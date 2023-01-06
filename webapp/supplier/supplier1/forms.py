from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, HiddenField, RadioField, PasswordField
from wtforms.validators import ValidationError, Optional, NumberRange, InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from webapp.database import Connection
import re


class FiltersForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')

    def validate_date(self, date):
        if date.data is None:
            raise ValidationError("Он сар өдөр сонгоно уу!")


class OrderAddForm(FlaskForm):
    order_type = RadioField('Хүргэлтийн чиглэл', choices=[(0,'Улаанбаатар'),(1,'Орон нутаг')], validators=[Optional()], default=0)
    phone = IntegerField('Утасны дугаар', validators=[InputRequired()])
    phone_more = IntegerField('Нэмэлт утасны дугаар', validators=[Optional()])
    district = SelectField('Дүүрэг', choices=[], validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[], validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[], validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[InputRequired()])
    total_amount = IntegerField('Нийт үнэ', validators=[InputRequired(), NumberRange(min=0)], default=0)
    submit = SubmitField('Үүсгэх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set((str(phone.data)))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

    # def validate_district(self, district):
    #     if district.data == "0" or district.data == "Дүүрэг сонгох":
    #         raise ValidationError('Дүүрэг сонгоно уу!')
    #     else:
    #         pass

    # def validate_khoroo(self, khoroo):
    #     if khoroo.data == "0" or khoroo.data == "Хороо сонгох":
    #         raise ValidationError('Хорооны дугаар сонгоно уу!')
    #     else:
    #         pass

    # def validate_aimag(self, aimag):
    #     if aimag.data == "0" or aimag.data == "Аймаг сонгох":
    #         raise ValidationError('Аймаг сонгоно уу!')
    #     else:
    #         pass


class OrderDetailFileAddForm(FlaskForm):
    excel_file = FileField('Excel файл оруулах', validators=[InputRequired(), FileAllowed(['xlsx', 'XLSX'], message='Зөвхөн Excel файл оруулна уу!')], id="inputGroupFile02")
    preview_orders = SubmitField('Захиалгууд харах')
    

class SubmitFileOrders(FlaskForm):
    submit = SubmitField('Захиалгууд нэмэх')


class ProductAddForm(FlaskForm):
    name = StringField('Нэр', validators=[InputRequired()])
    color = SelectField('Өнгө', choices=[],validators=[InputRequired()])
    size = SelectField('Хэмжээ', choices=[],validators=[InputRequired()])
    description = TextAreaField('Бусад', validators=[Optional()])
    image = FileField('Зураг', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], message='Зөвхөн jpg, jpeg, png өргөтгөлтэй зураг оруулна уу!')], id='image')
    price = IntegerField('Үнэ', validators=[InputRequired(), NumberRange(min=1)], id='price', default=0)
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
        product_database = connection.execute('select count(*) from sunsundatabase1.product as product join sunsundatabase1.product_colors as colors on product.id = colors.product_id join sunsundatabase1.product_color as color on colors.product_color_id = color.id join sunsundatabase1.product_sizes as sizes on product.id = sizes.product_id join sunsundatabase1.product_size as size on sizes.product_size_id = size.id where product.name = :product_name and color.id = :color_id and size.id = :size_id',{'product_name': name.data, 'color_id': self.color.data, 'size_id': self.size.data}).scalar()
        if product_database>0:
            raise ValidationError('Бараа бүртгэлтэй байна!')


class ProductEditForm(FlaskForm):
    name = StringField('Нэр', validators=[InputRequired()])
    description = TextAreaField('Бусад', validators=[Optional()])
    color = SelectField('Өнгө', choices=[],validators=[InputRequired()])
    size = SelectField('Хэмжээ', choices=[],validators=[InputRequired()])
    image = FileField('Зураг', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], message='Зөвхөн jpg, jpeg, png өргөтгөлтэй зураг оруулна уу!')], id='image')
    price = IntegerField('Үнэ', validators=[InputRequired(), NumberRange(min=1)], id='price', default=0)
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
        product_database = connection.execute('select count(*) from sunsundatabase1.product as product join sunsundatabase1.product_colors as colors on product.id = colors.product_id join sunsundatabase1.product_color as color on colors.product_color_id = color.id join sunsundatabase1.product_sizes as sizes on product.id = sizes.product_id join sunsundatabase1.product_size as size on sizes.product_size_id = size.id where product.name = :product_name and color.id = :color_id and size.id = :size_id',{'product_name': name.data, 'color_id': self.color.data, 'size_id': self.size.data}).scalar()
        if product_database>0:
            raise ValidationError('Бараа бүртгэлтэй байна!')


class InventoryAddForm(FlaskForm):
    quantity = IntegerField('Тоо ширхэг', validators=[InputRequired(), NumberRange(min=1)], id='quantity', default=0)
    product = SelectField('Бараа', choices=[],validators=[InputRequired()])
    choose_receiver = SelectField('Хүлээн авсан', choices=[],validators=[InputRequired()])
    submit = SubmitField('Хүлээлгэж өгөх')


class DriverPickupForm(FlaskForm):
    pickup_id = HiddenField()
    submit = SubmitField('Хүлээлгэж өгөх')


class InventoryPickupAddForm(FlaskForm):
    quantity = IntegerField('Тоо ширхэг', validators=[InputRequired(), NumberRange(min=1)], id='quantity', default=0)
    product = SelectField('Бараа', choices=[],validators=[InputRequired()])
    submit = SubmitField('Жолооч дуудах')


class ChooseType(FlaskForm):
    choose_type = SelectField('Төрөл сонгох', choices=[],validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class SelectOption(FlaskForm):
    select_option = DateField('Хугацаа сонгох', validators=[Optional()])
    submit = SubmitField('Сонгох')

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

        if password.data != password.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_password_again(self, confirm_password, password):
        if password.data != confirm_password.data:
            raise ValidationError('Нууц үгнүүд таарахгүй байна!')


class DateSelect(FlaskForm):
    select_date = DateField('Хугацаа сонгох', validators=[Optional()])
    submit = SubmitField('Сонгох')
