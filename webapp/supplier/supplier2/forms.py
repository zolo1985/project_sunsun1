from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, HiddenField, RadioField, PasswordField
from wtforms.validators import ValidationError, Optional, NumberRange, InputRequired, Length
from webapp.database import Connection
import re

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


class OrderEditForm(FlaskForm):
    phone = IntegerField('Утасны дугаар', validators=[InputRequired()])
    phone_more = IntegerField('Нэмэлт утасны дугаар', validators=[InputRequired()])
    district = SelectField('Дүүрэг', choices=[],validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[],validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[],validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[InputRequired()])
    total_amount = IntegerField('Үйлчлэгчээс авах дүн', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Өөрчлөх')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789"))
        validation = set(str(phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

class TransferForm(FlaskForm):
    order_id = HiddenField()
    inventory_id = HiddenField()
    submit = SubmitField('Хүлээлгэж өгөх')

class DateSelectForm(FlaskForm):
    date = DateField('Он Сар', validators=[Optional()])
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