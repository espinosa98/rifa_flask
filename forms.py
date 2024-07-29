from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, IntegerField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Optional

class RaffleForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    address = StringField('Dirección', validators=[DataRequired()])
    reference_number = StringField('Número de Referencia', validators=[DataRequired()])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    num_numbers = SelectField('Cantidad de Números', choices=[('5', '5'), ('10', '10'), ('20', '20'), ('custom', 'Otro')], validators=[DataRequired()])
    custom_number = IntegerField('Número Personalizado', validators=[Optional()])  # Hacer el campo opcional
    bank_account = SelectField('Cuenta Bancaria', choices=[('1234567890', 'Banco A - 1234567890'), ('0987654321', 'Banco B - 0987654321'), ('1122334455', 'Banco C - 1122334455')], validators=[DataRequired()])
    reference = StringField('Referencia de Consignación', validators=[DataRequired()])

class CreateRaffleForm(FlaskForm):
    name = StringField('Nombre del Sorteo', validators=[DataRequired()])
    start_date = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    max_number = IntegerField('Máximo Número a Generar', validators=[DataRequired()])
    submit = SubmitField('Crear Sorteo')
