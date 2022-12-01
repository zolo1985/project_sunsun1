from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import Length, Email, EqualTo, ValidationError, DataRequired, Optional, NumberRange
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
    select_drivers = SelectField('Жолооч', choices=[], validators=[DataRequired()])
    submit = SubmitField('Сонгох')

class DriversHistoriesForm(FlaskForm):
    task_id = HiddenField()
    date = DateField('Он сараар', validators=[DataRequired()])
    select_drivers = SelectField('Жолооч', choices=[], validators=[DataRequired()])
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
    district_names = SelectField('Дүүрэгийн нэр', choices=[],validators=[DataRequired()])
    submit = SubmitField('Шүүж харах')


class FilterDateForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')

class MakeShowCommentForm(FlaskForm):
    order_id = HiddenField()
    submit = SubmitField('Бүх Коммент Нээх')

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
    firstname = StringField('Нэр', validators=[DataRequired()])
    lastname = StringField('Овог', validators=[DataRequired()])
    email = StringField('И-мэйл', validators=[DataRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар', validators=[DataRequired()])
    password = PasswordField('Нууц үг', validators=[DataRequired(), Length(min=3, max=50)])
    select_user_role = SelectField('Хэрэглэгчийн төрөл', choices=[], validators=[DataRequired()])
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
    email = StringField('И-мэйл', validators=[DataRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар', validators=[DataRequired()])
    fee = IntegerField('Хүргэлтийн төлбөр', validators=[DataRequired(), NumberRange(min=0)])
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
    select_option = SelectField('Хугацаа', choices=[],validators=[DataRequired()])
    date = DateField('Он сар', validators=[DataRequired()])
    submit = SubmitField('Сонгох')

class SelectDriverOption(FlaskForm):
    select_option = SelectField('Хугацаа', choices=[],validators=[DataRequired()])
    select_driver = SelectField('Жолооч', choices=[],validators=[DataRequired()])
    date = DateField('Он сар', validators=[DataRequired()])
    submit = SubmitField('Сонгох')

class SelectSupplierOption(FlaskForm):
    select_option = SelectField('Хугацаа', choices=[],validators=[DataRequired()])
    select_supplier = SelectField('Харилцагч', choices=[],validators=[DataRequired()])
    date = DateField('Он сар', validators=[DataRequired()])
    submit = SubmitField('Сонгох')


