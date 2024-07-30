from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import random
import os
from dotenv import load_dotenv
from forms import RaffleForm, CreateRaffleForm, RegisterForm, LoginForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

# Cargar variables de entorno desde el archivo .env
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
REGISTER_KEY = os.getenv('REGISTER_KEY')

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rifa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
mail = Mail(app)


# Configuración de Flask-Login
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'

# Modelo de usuario para Flask-Login
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


# Definir el modelo para las personas
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    reference_number = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    # Relación uno a muchos con RaffleNumber
    raffle_numbers = db.relationship('RaffleNumber', backref='person', lazy=True)


class RaffleNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    raffle_id = db.Column(db.Integer, db.ForeignKey('raffle.id'), nullable=False)

    #combinacion unica de sorteo y numero
    __table_args__ = (
        db.UniqueConstraint('number', 'raffle_id', name='uix_number_raffle_id'),
    )


class Raffle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True)
    max_number = db.Column(db.Integer, nullable=False)
    valor_numero = db.Column(db.Integer, nullable=False)


# Crear la base de datos
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def index():
    form = RaffleForm()
    # Obtener la rifa activa y actual
    raffle = Raffle.query.filter_by(active=True).first()
    if form.validate_on_submit():
        email = form.email.data
        num_numbers = form.num_numbers.data
        custom_number = form.custom_number.data

        if num_numbers == 'custom':
            if custom_number is not None:
                num_numbers = int(custom_number)
            else:
                num_numbers = 5  # Default to 5 if no custom number is provided
        else:
            num_numbers = int(num_numbers)

        if not raffle:
            flash('No hay sorteos activos en este momento.', 'error')
            return redirect(url_for('index'))

        if num_numbers > raffle.max_number:
            flash(f'No puedes solicitar más de {raffle.max_number} números para este sorteo.', 'error')
            return redirect(url_for('index'))

        first_name = form.first_name.data
        last_name = form.last_name.data
        address = form.address.data
        reference_number = form.reference_number.data
        bank_account = form.bank_account.data

        # Obtener los números ya utilizados en la rifa activa
        used_numbers = [number.number for number in RaffleNumber.query.filter_by(raffle_id=raffle.id).all()]

        # Calcular los números disponibles
        available_numbers = list(set(range(1, raffle.max_number + 1)) - set(used_numbers))

        if len(available_numbers) == 0:
            flash('No hay números disponibles en este momento.', 'error')
            return redirect(url_for('index'))
        elif len(available_numbers) < num_numbers:
            flash(f'Solo quedan {len(available_numbers)} números disponibles.', 'error')
            return redirect(url_for('index'))

        try:
            with db.session.no_autoflush:
                # Verificar si la persona ya existe en la base de datos sino crearla
                person = Person.query.filter_by(email=email).first()
                if person is None:
                    person = Person(first_name=first_name, last_name=last_name, address=address,
                                    reference_number=reference_number, email=email)
                    db.session.add(person)
                else:
                    person.first_name = first_name
                    person.last_name = last_name
                    person.address = address
                    person.reference_number = reference_number

                db.session.commit()

                # Generar los números de la rifa
                numbers = random.sample(available_numbers, num_numbers)

                for number in numbers:
                    new_number = RaffleNumber(number=number, person_id=person.id, raffle_id=raffle.id)
                    db.session.add(new_number)

                db.session.commit()

                msg = Message('Tus números de la rifa', recipients=[email])
                msg.body = (f'Tus números de la rifa son: {", ".join(map(str, numbers))}\n\n'
                            f'Información de la cuenta bancaria: {bank_account}\n'
                            f'Referencia de consignación: {reference_number}')

                mail.send(msg)

                mensaje = 'Tus números de la rifa han sido enviados a tu correo electrónico regitrado. ¡Buena suerte!', 'success'

        except Exception as e:
            mensaje = f'Hubo un problema al procesar tu solicitud. {e}', 'error'

        flash(mensaje[0], mensaje[1])
        return redirect(url_for('index'))

    return render_template('index.html', form=form, raffle=raffle)


# --------- Rutas para la administración de números ------------


@app.route('/list_numbers')
@login_required
def list_numbers():
    numeros = RaffleNumber.query.all()
    return render_template('list_numbers.html', numeros=numeros)


@app.route('/delete_number/<int:raffle_number_id>', methods=['POST'])
@login_required
def delete_number(raffle_number_id):
    number = RaffleNumber.query.get_or_404(raffle_number_id)
    db.session.delete(number)
    db.session.commit()
    flash('Número eliminado exitosamente.', 'success')
    return redirect(url_for('list_numbers'))


# --------- Rutas para la administración de sorteos ------------


@app.route('/create_raffle', methods=['GET', 'POST'])
@login_required
def create_raffle():
    form = CreateRaffleForm()
    if form.validate_on_submit():
        name = form.name.data
        start_date = form.start_date.data
        max_number = form.max_number.data

        new_raffle = Raffle(name=name, start_date=start_date, max_number=max_number, valor_numero=form.valor_numero.data)
        raffle = Raffle.query.filter_by(active=True).first()
        if raffle:
            mensaje = f'Ya hay un sorteo activo llamado {raffle.name}.', 'info'
            raffle.active = False
            db.session.add(raffle)
        else:
            mensaje = 'Sorteo creado exitosamente.', 'success'
        db.session.add(new_raffle)
        db.session.commit()


        flash(mensaje[0], mensaje[1])
        return redirect(url_for('list_raffles'))

    return render_template('create_raffle.html', form=form)


@app.route('/toggle_raffle/<int:raffle_id>', methods=['POST'])
@login_required
def toggle_raffle(raffle_id):
    # Obtener el sorteo especificado
    raffle = Raffle.query.get_or_404(raffle_id)
    if raffle.active:
        flash('El sorteo ya está activo.', 'info')
        return redirect(url_for('list_raffles'))

    # Desactivar todos los sorteos activos
    raffles_deactivate = Raffle.query.filter_by(active=True).all()
    for rafflee in raffles_deactivate:
        rafflee.active = False
        db.session.add(rafflee)

    # Activar el sorteo especificado
    raffle.active = True
    db.session.add(raffle)
    db.session.commit()

    mensaje = f'Sorteo {raffle.name} activado exitosamente.'
    if raffles_deactivate:
        mensaje += f' Los siguientes sorteos han sido desactivados: {", ".join([r.name for r in raffles_deactivate])}'
    flash(mensaje, 'success')
    return redirect(url_for('list_raffles'))



@app.route('/list_raffles', methods=['GET'])
@login_required
def list_raffles():
    raffles = Raffle.query.all()
    return render_template('list_raffles.html', raffles=raffles)


# --------- Rutas para la autenticación ------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        register_key = form.register_key.data
        if register_key != REGISTER_KEY:
            flash('Clave de registro incorrecta.', 'danger')
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Cuenta creada exitosamente!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('El correo electrónico o el nombre de usuario ya están registrados. Por favor, intenta con otros.',
                  'danger')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login exitoso!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Login fallido. Por favor verifica tu email y contraseña.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('index'))


# --------- Pagina de administración ------------


@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
