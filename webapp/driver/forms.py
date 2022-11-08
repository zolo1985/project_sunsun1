from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Optional

class DeliveryStatusForm(FlaskForm):
    current_status = SelectField('Төлөв өөрчлөх', choices=[], validators=[Optional()])
    submit = SubmitField('Төлөв өөрчлөх')

class DeliveryPostphonedForm(FlaskForm):
    driver_comment = TextAreaField('Шалтгаан', validators=[Optional()])
    postphoned_date = DateField('Хойшлуулсан өдөр', validators=[DataRequired()])
    submit = SubmitField('Захиалга хойшлуулах')

class DeliveryCancelledForm(FlaskForm):
    driver_comment = TextAreaField('Шалтгаан', validators=[Optional()])
    submit = SubmitField('Захиалга цуцлах')