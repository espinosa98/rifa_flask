from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, IntegerField, SubmitField, DateField,  PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, Optional, Length, EqualTo
import re


class RaffleForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    address = StringField('Dirección', validators=[DataRequired()])
    reference_number = StringField('Referencia de Consignación', validators=[DataRequired()])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    num_numbers = SelectField('Cantidad de Números', choices=[('', ''), ('5', '5'), ('10', '10'), ('20', '20'), ('custom', 'Otro')], validators=[DataRequired()])
    custom_number = IntegerField('Número Personalizado', validators=[Optional()])  # Hacer el campo opcional
    bank_account = SelectField('Cuenta Bancaria', choices=[('1234567890', 'Banco A - 1234567890'), ('0987654321', 'Banco B - 0987654321'), ('1122334455', 'Banco C - 1122334455')], validators=[DataRequired()])


class CreateRaffleForm(FlaskForm):
    name = StringField('Nombre del Sorteo', validators=[DataRequired()])
    start_date = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    max_number = IntegerField('Máximo Número a Generar', validators=[DataRequired()])
    valor_numero = IntegerField('Valor por Número', validators=[DataRequired()])
    submit = SubmitField('Crear Sorteo')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    register_key = PasswordField('Clave de Registro', validators=[DataRequired()])
    submit = SubmitField('Registrar')

    def validate_password(form, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not re.search("[a-z]", password):
            raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
        if not re.search("[A-Z]", password):
            raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not re.search("[0-9]", password):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not re.search("[!@#$%^&*()_+]", password):
            raise ValidationError('La contraseña debe contener al menos un carácter especial (!@#$%^&*()_+).')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')
