# Flask
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required
import random
import requests
from werkzeug.utils import secure_filename
import os

# propios
from app import db
from app.models import Raffle, RaffleNumber, Person
from app.forms import RaffleForm, CreateRaffleForm, EditRaffleForm
from config import Config
from app.utils import allowed_file, MAX_CONTENT_LENGTH


raffle_bp = Blueprint('raffle', __name__)


@raffle_bp.route('/', methods=['GET', 'POST'])
def index():
    form = RaffleForm()
    # Obtener la rifa activa
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
            return redirect(url_for('raffle.index'))

        if num_numbers > raffle.max_number:
            flash(f'No puedes solicitar más de {raffle.max_number} números para este sorteo.', 'error')
            return redirect(url_for('raffle.index'))

        first_name = form.first_name.data
        last_name = form.last_name.data
        address = form.address.data
        reference_number = form.reference_number.data
        bank_account = form.bank_account.data

        # Obtener los números ya utilizados en la rifa activa
        used_numbers = [number.number for number in RaffleNumber.query.filter_by(raffle_id=raffle.id).all()]
        available_numbers = [str(num).zfill(len(str(raffle.max_number))) for num in range(1, raffle.max_number + 1) if
                             str(num).zfill(len(str(raffle.max_number))) not in used_numbers]

        if len(available_numbers) == 0:
            flash('No hay números disponibles en este momento.', 'error')
            return redirect(url_for('raffle.index'))
        elif len(available_numbers) < num_numbers:
            flash(f'Solo quedan {len(available_numbers)} números disponibles.', 'error')
            return redirect(url_for('raffle.index'))

        try:
            person = Person(first_name=first_name, last_name=last_name, address=address,
                            reference_number=reference_number, email=email)
            db.session.add(person)
            db.session.commit()

            # Generar los números de la rifa
            numbers = random.sample(available_numbers, num_numbers)

            for number in numbers:
                new_number = RaffleNumber(number=number, person_id=person.id, raffle_id=raffle.id)
                db.session.add(new_number)

            db.session.commit()

            mensaje = 'Tus números de la rifa han sido enviados a tu correo electrónico regitrado. ¡Buena suerte!', 'success'

        except Exception as e:
            db.session.rollback()
            mensaje = f'Hubo un problema al procesar tu solicitud. {e}', 'error'

        flash(mensaje[0], mensaje[1])
        return redirect(url_for('raffle.index'))

    return render_template('index.html', form=form, raffle=raffle, current_page='index')


@raffle_bp.route('/list_raffles', methods=['GET'])
@login_required
def list_raffles():
    raffles = Raffle.query.all()
    # ver numeros generados cantidad
    for raffle in raffles:
        raffle.numbers_count = len(raffle.raffle_numbers)
    return render_template('list_raffles.html', raffles=raffles, current_page='list_raffles')


@raffle_bp.route('/create_raffle', methods=['GET', 'POST'])
@login_required
def create_raffle():
    form = CreateRaffleForm()
    if form.validate_on_submit():
        if form.image.data:
            file = form.image.data

            # Validar el tamaño del archivo
            if len(file.read()) > MAX_CONTENT_LENGTH:
                flash('El tamaño de la imagen no puede exceder los 2 MB.', 'error')
                return redirect(url_for('raffle.create_raffle'))

            file.seek(0)

            # Validar la extensión del archivo
            if not allowed_file(file.filename):
                flash('Solo se permiten archivos de imagen (png, jpg, jpeg, gif).', 'error')
                return redirect(url_for('raffle.create_raffle'))

            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(file_path)

            try:
                new_raffle = Raffle(
                    name=form.name.data,
                    start_date=form.start_date.data,
                    max_number=form.max_number.data,
                    valor_numero=form.valor_numero.data,
                    image_filename=filename
                )
                raffle = Raffle.query.filter_by(active=True).first()
                if raffle:
                    mensaje = f'Ya hay un sorteo activo llamado {raffle.name}.', 'info'
                    raffle.active = False
                    db.session.add(raffle)
                else:
                    mensaje = 'Sorteo creado exitosamente.', 'success'
                db.session.add(new_raffle)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                mensaje = f'Hubo un problema al procesar tu solicitud. {e}', 'error'
            flash(mensaje[0], mensaje[1])
            return redirect(url_for('raffle.list_raffles'))

    return render_template('create_raffle.html', form=form, current_page='create_raffle')


@raffle_bp.route('/toggle_raffle/<int:raffle_id>', methods=['POST'])
@login_required
def toggle_raffle(raffle_id):
    # Obtener el sorteo especificado
    raffle = Raffle.query.get_or_404(raffle_id)
    raffle.active = not raffle.active
    db.session.add(raffle)
    db.session.commit()
    flash(f'El sorteo {raffle.name} ha sido {"activado" if raffle.active else "desactivado"} exitosamente.', 'success')
    return redirect(url_for('raffle.list_raffles'))


@raffle_bp.route('/edit_raffle/<int:raffle_id>', methods=['GET', 'POST'])
@login_required
def edit_raffle(raffle_id):
    raffle = Raffle.query.get_or_404(raffle_id)
    form = EditRaffleForm(obj=raffle)

    if form.validate_on_submit():
        raffle.name = form.name.data
        raffle.start_date = form.start_date.data
        raffle.max_number = form.max_number.data
        raffle.valor_numero = form.valor_numero.data
        db.session.commit()
        flash('Sorteo actualizado exitosamente.', 'success')
        return redirect(url_for('raffle.list_raffles'))

    return render_template('edit_raffle.html', form=form, raffle=raffle, current_page='edit_raffle')


@raffle_bp.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


@raffle_bp.route('/conversion_rate')
def conversion_rate():
    response = requests.get(Config.API_URL)
    data = response.json()
    rate = data['rates']['VES']
    return jsonify({'exchange_rate': rate})