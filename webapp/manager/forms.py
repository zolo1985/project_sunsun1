from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField, TextAreaField, RadioField
from wtforms.validators import Length, Email, EqualTo, ValidationError, InputRequired, Optional, NumberRange, InputRequired, Regexp
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
    phone = StringField('Утасны дугаар',validators=[ InputRequired(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    password = PasswordField('Нууц үг', validators=[InputRequired(), Length(min=3, max=50)])
    select_user_role = SelectField('Хэрэглэгчийн төрөл', choices=[], validators=[InputRequired()])
    submit = SubmitField('Хэрэглэгч нэмэх')

    def validate_company_name(self, company_name):
        connection = Connection()
        is_company_name = connection.query(models.User).filter_by(company_name=company_name.data.strip()).count()
        connection.close()
        if is_company_name>=1:
            raise ValidationError('Ийм нэртэй харилцагч бүртгэлтэй байна! Өөр нэр сонгоно уу!')

    def validate_firstname(self, firstname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ- "))
        validation = set((firstname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

    def validate_lastname(self, lastname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ- "))
        validation = set((lastname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

    def validate_email(self, email):
        connection = Connection()
        account = connection.query(models.User).filter_by(email=email.data.strip()).first()
        connection.close()
        if account:
            raise ValidationError('Энэ имэйл хаяг өөр данс нь дээр бүртгэлтэй байна! Өөр имэйл хаяг ашиглана уу!')

    def validate_phone(self, phone):
        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data.strip()).first()
        connection.close()
        if account:
            raise ValidationError('Энэ утас өөр данс нь дээр бүртгэлтэй байна! Өөр утас ашиглана уу!')


class EditAccountForm(FlaskForm):
    email = StringField('И-мэйл', validators=[InputRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар',validators=[InputRequired(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    fee = IntegerField('Хүргэлтийн төлбөр', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Өөрчлөх')

    def validate_firstname(self, firstname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((firstname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

    def validate_lastname(self, lastname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((lastname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

    def validate_email(self, email):
        connection = Connection()
        account = connection.query(models.User).filter_by(email=email.data.strip()).all()
        connection.close()
        if len(account)>1:
            raise ValidationError('Энэ имэйл хаяг өөр данс нь дээр бүртгэлтэй байна! Өөр имэйл хаяг ашиглана уу!')

    def validate_phone(self, phone):
        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data.strip()).all()
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
    phone = StringField('Утасны дугаар',validators=[ InputRequired(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    phone_more = StringField('Нэмэлт утасны дугаар*. (Заавал биш)',validators=[Optional(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    district = SelectField('Дүүрэг', choices=[], validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[], validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[], validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[InputRequired()])
    # comment = TextAreaField('Тэмдэглэгээ', validators=[Optional()])
    total_amount = IntegerField('Нийт үнэ', validators=[InputRequired(), NumberRange(min=0)], default=0)
    submit = SubmitField('Үүсгэх')

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


