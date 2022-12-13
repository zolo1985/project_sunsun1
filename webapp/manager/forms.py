from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField, TextAreaField, RadioField
from wtforms.validators import Length, Email, EqualTo, ValidationError, InputRequired, Optional, NumberRange, InputRequired
from webapp.database import Connection
from webapp import models
from datetime import datetime
import re
import pytz

class FiltersForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    regions = SelectField('Бүсийн нэр', choices=[], validators=[Optional()])
    status = SelectField('Төлөв', choices=[], validators=[Optional()])
    submit = SubmitField('Шүүх', id="submit1", name="submit1")

class DateFilterForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')


class SelectDriverForm(FlaskForm):
    selected_driver = SelectField('Жолооч', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')

class UnassignForm(FlaskForm):
    order_id = HiddenField()
    submit = SubmitField('Бүс, Жолоочгүй болгох')


class AssignRegionAndDriverForm(FlaskForm):
    order_id = HiddenField()
    select_regions = SelectField('Бүс', choices=[],validators=[Optional()])
    select_drivers = SelectField('Жолооч', choices=[], validators=[Optional()])
    submit = SubmitField('Хувиарлах')

class DriversSelect(FlaskForm):
    task_id = HiddenField()
    select_drivers = SelectField('Жолооч', choices=[], validators=[Optional()])
    submit = SubmitField('Сонгох')

class DriversDateSelect(FlaskForm):
    task_id = HiddenField()
    select_day = SelectField('Өдөр', choices=[], validators=[Optional()])
    select_drivers = SelectField('Жолооч', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')

class DriversHistoriesForm(FlaskForm):
    task_id = HiddenField()
    date = DateField('Он сараар', validators=[InputRequired()])
    select_drivers = SelectField('Жолооч', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class OrderEditForm(FlaskForm):
    select_regions = SelectField('Бүс өөрчлөх', choices=[],validators=[Optional()])
    select_drivers = SelectField('Жолооч өөрчлөх', choices=[], validators=[Optional()])
    date = DateField('Он сар өөрчлөх', validators=[Optional()])
    submit = SubmitField('Төлөв өөрчлөх')

    def validate_date(self, date):
        if date.data < datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date():
            raise ValidationError("Өнөөдрөөс өмнөх өдөр байх боломжгүй!")


class FilterOrderByDistrict(FlaskForm):
    khoroo_names = SelectField('Хорооны дугаар', choices=[],validators=[Optional()])
    district_names = SelectField('Дүүрэгийн нэр', choices=[],validators=[InputRequired()])
    submit = SubmitField('Шүүж харах')


class FilterDateForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')


class ShowCommentStatusForm(FlaskForm):
    order_id = HiddenField()
    submit = SubmitField('Бүх Төлөв, Коммент Нээх')


class EditCommentForm(FlaskForm):
    comment = TextAreaField('Коммент', validators=[Optional()])
    submit = SubmitField('Коммент Өөрчлөх')


class EditAddressForm(FlaskForm):
    address = TextAreaField('Хаяг', validators=[Optional()])
    submit = SubmitField('Хаяг Өөрчлөх')


class EditTotalAmountForm(FlaskForm):
    total_amount = TextAreaField('Дүн', validators=[Optional()])
    submit = SubmitField('Дүн Өөрчлөх')


class NewAccountForm(FlaskForm):
    company_name = StringField('Байгууллагын нэр', validators=[Optional(), Length(min=6, max=255, message='Хэт урт эсвэл богино байна!')])
    firstname = StringField('Нэр', validators=[InputRequired()])
    lastname = StringField('Овог', validators=[InputRequired()])
    email = StringField('И-мэйл', validators=[InputRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар', validators=[InputRequired()])
    password = PasswordField('Нууц үг', validators=[InputRequired(), Length(min=3, max=50)])
    select_user_role = SelectField('Хэрэглэгчийн төрөл', choices=[], validators=[InputRequired()])
    submit = SubmitField('Хэрэглэгч нэмэх')

    def validate_firstname(self, firstname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((firstname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг тоо ашиглана уу!')

        if firstname.data != firstname.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_lastname(self, lastname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((lastname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг тоо ашиглана уу!')

        if lastname.data != lastname.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email.data)):
            pass
        else:
            raise ValidationError('Имэйл хаяг биш байна!')

        if email.data != email.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

        connection = Connection()
        account = connection.query(models.User).filter_by(email=email.data).first()
        connection.close()
        if account:
            raise ValidationError('Энэ имэйл хаяг өөр данс нь дээр бүртгэлтэй байна! Өөр имэйл хаяг ашиглана уу!')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789+"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

        if phone.data != phone.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data).first()
        connection.close()
        if account:
            raise ValidationError('Энэ утас өөр данс нь дээр бүртгэлтэй байна! Өөр утас ашиглана уу!')


class EditAccountForm(FlaskForm):
    email = StringField('И-мэйл', validators=[InputRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар', validators=[InputRequired()])
    fee = IntegerField('Хүргэлтийн төлбөр', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Өөрчлөх')

    def validate_firstname(self, firstname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((firstname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

        if firstname.data != firstname.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_lastname(self, lastname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((lastname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

        if lastname.data != lastname.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email.data)):
            pass
        else:
            raise ValidationError('Имэйл хаяг биш байна!')

        if email.data != email.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

        connection = Connection()
        account = connection.query(models.User).filter_by(email=email.data).all()
        connection.close()
        if len(account)>1:
            raise ValidationError('Энэ имэйл хаяг өөр данс нь дээр бүртгэлтэй байна! Өөр имэйл хаяг ашиглана уу!')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789+"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

        if phone.data != phone.data.strip():
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data).all()
        connection.close()
        if len(account)>1:
            raise ValidationError('Энэ утас өөр данс нь дээр бүртгэлтэй байна! Өөр утас ашиглана уу!')


class SelectOption(FlaskForm):
    select_option = SelectField('Хугацаа', choices=[],validators=[InputRequired()])
    date = DateField('Он сар', validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class SelectDriverOption(FlaskForm):
    select_option = SelectField('Хугацаа', choices=[],validators=[InputRequired()])
    select_driver = SelectField('Жолооч', choices=[],validators=[InputRequired()])
    date = DateField('Он сар', validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class SelectSupplierOption(FlaskForm):
    select_option = SelectField('Хугацаа', choices=[],validators=[InputRequired()])
    select_supplier = SelectField('Харилцагч', choices=[],validators=[InputRequired()])
    date = DateField('Он сар', validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class SearchForm(FlaskForm):
    search_text = StringField('Хайх', validators=[InputRequired(), Length(min=2, max=50, message='Нэр 2-50 урттай')])
    submit = SubmitField('Хайх')


class SelectSupplierForm(FlaskForm):
    suppliers = SelectField('Харилцагч', choices=[], validators=[InputRequired()])


class OrderAddForm(FlaskForm):
    delivery_type = RadioField('Төрөл', choices=[(0,'Хүргэлт'),(1,'Агуулахаас')], validators=[Optional()], default=0)
    order_type = RadioField('Хүргэлтийн чиглэл', choices=[(0,'Улаанбаатар'),(1,'Орон нутаг')], validators=[Optional()], default=0)
    suppliers = SelectField('Харилцагч', choices=[], validators=[InputRequired()])
    phone = IntegerField('Утасны дугаар', validators=[InputRequired()])
    phone_more = IntegerField('Нэмэлт утасны дугаар', validators=[Optional()])
    district = SelectField('Дүүрэг', choices=[], validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[], validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[], validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[InputRequired()])
    # comment = TextAreaField('Тэмдэглэгээ', validators=[Optional()])
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


class OrderDetailEditForm(FlaskForm):
    submit = SubmitField('Өөрчлөх')

class AddColorForm(FlaskForm):
    color_name = StringField('Өнгө', validators=[InputRequired()])
    submit = SubmitField('Нэмэх')

    def validate_color_name(self, color_name):
        connection = Connection()
        color = connection.query(models.ProductColor).filter_by(name=color_name.data.strip()).all()
        connection.close()
        if len(color)>0:
            raise ValidationError('Энэ өнгө бүртгэлтэй байна! Өөр нэр ашиглана уу!')

class AddSizeForm(FlaskForm):
    size_name = StringField('Хэмжээ', validators=[InputRequired()])
    submit = SubmitField('Нэмэх')

    def validate_size_name(self, size_name):
        connection = Connection()
        size = connection.query(models.ProductSize).filter_by(name=size_name.data.strip()).all()
        connection.close()
        if len(size)>0:
            raise ValidationError('Энэ хэмжээ бүртгэлтэй байна! Өөр нэр ашиглана уу!')


