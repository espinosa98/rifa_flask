from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import random
import os
from dotenv import load_dotenv
from forms import RaffleForm

# Cargar variables de entorno desde el archivo .env
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

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


# Definir el modelo para los números de la rifa
class RaffleNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)


# Crear la base de datos
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = RaffleForm()
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

        if num_numbers > 100:
            # Maximo de 100 números únicos posibles en este caso
            flash('No se pueden generar más de 100 números únicos.', 'error')
            return redirect(url_for('index'))

        first_name = form.first_name.data
        last_name = form.last_name.data
        address = form.address.data
        reference_number = form.reference_number.data
        bank_account = form.bank_account.data

        # Obtener los números disponibles
        available_numbers = set(range(1, 101)) - {n.number for n in RaffleNumber.query.all()}
        print(available_numbers)
        print(num_numbers)
        if len(available_numbers) == num_numbers:
            flash('Se han agotado los números disponibles.', 'error')
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
                    new_number = RaffleNumber(number=number, person_id=person.id)
                    db.session.add(new_number)

                db.session.commit()

                msg = Message('Tus números de la rifa', recipients=[email])
                msg.body = (f'Tus números de la rifa son: {", ".join(map(str, numbers))}\n\n'
                            f'Información de la cuenta bancaria: {bank_account}\n'
                            f'Referencia de consignación: {reference_number}')

                mail.send(msg)

                flash('Tu solicitud ha sido enviada exitosamente. Tus números generados son: ' + ', '.join(map(str, numbers)), 'success')

        except Exception as e:
            print(f'Error: {e}')
            flash('Hubo un problema al procesar tu solicitud.', 'error')

        return redirect(url_for('index'))

    return render_template('index.html', form=form)


# Ruta para ver los números de la rifa con paginación
@app.route('/ver_numeros')
@app.route('/ver_numeros/<int:page>')
def ver_numeros(page=1):
    per_page = 10
    numeros_paginados = RaffleNumber.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('ver_numeros.html', numeros_paginados=numeros_paginados)


if __name__ == '__main__':
    app.run(debug=True)
