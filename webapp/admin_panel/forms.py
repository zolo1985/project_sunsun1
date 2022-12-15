# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField, BooleanField
# from wtforms.validators import Length, Email, ValidationError, DataRequired
# import re
# from wtforms import (
#     widgets,
#     TextAreaField
# )

# class CKTextAreaWidget(widgets.TextArea):
#     def __call__(self, field, **kwargs):
#         kwargs.setdefault('class_', 'ckeditor')
#         return super(CKTextAreaWidget, self).__call__(field, **kwargs)


# class CKTextAreaField(TextAreaField):
#     widget = CKTextAreaWidget()
    

# class SignInForm(FlaskForm):
#     email = StringField('Имэйл', validators=[DataRequired(), Email("Имэйл хаяг оруулна уу!"), Length(min=6, max=255, message='Хэт урт эсвэл богино байна!')], render_kw={"placeholder": "Имэйл"})
#     password = PasswordField('Нууц үг', validators=[DataRequired(), Length(min=6, max=255, message='Хэт богино байна!')])
#     remember = BooleanField("Remember Me")
#     submit = SubmitField('Нэвтрэх')

#     def validate_email(self, email):
#         if email.data is None:
#             raise ValidationError('Имэйл хаяг оруулна уу!!!')

#         if email.data != email.data.strip():
#             raise ValidationError("Урд хойно хоосон зай ашигласан байна!")

#         regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#         if(re.fullmatch(regex, email.data)):
#             pass
#         else:
#             raise ValidationError('Имэйл хаяг алдаатай байна!')