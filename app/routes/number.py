from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from flask_mail import Message
from app import mail
from app import db
from app.models import RaffleNumber
from app.models import Person

number_bp = Blueprint('number', __name__)


@number_bp.route('/list_numbers')
@login_required
def list_numbers():
    numeros = RaffleNumber.query.all()
    return render_template('list_numbers.html', numeros=numeros, current_page='list_numbers')


@number_bp.route('/delete_number/<int:raffle_number_id>', methods=['POST'])
@login_required
def delete_number(raffle_number_id):
    try:
        with db.session.begin():
            number = RaffleNumber.query.get_or_404(raffle_number_id)
            db.session.delete(number)
            db.session.commit()
            flash('Número eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hubo un problema al eliminar el número. {e}', 'error')
    return redirect(url_for('number.list_numbers'))


@number_bp.route('/list_person')
@login_required
def list_person():
    persons = Person.query.all()
    return render_template('list_person.html', persons=persons, current_page='list_person')


@number_bp.route('/delete_person/<int:person_id>', methods=['POST'])
@login_required
def delete_person(person_id):
    try:
        with db.session.begin():
            person = Person.query.get_or_404(person_id)
            db.session.delete(person)
            db.session.commit()
            flash('Persona eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hubo un problema al eliminar la persona. {e}', 'error')
    return redirect(url_for('number.list_person'))


@number_bp.route('/send_numbers/<int:person_id>', methods=['POST'])
@login_required
def send_numbers(person_id):
    try:
        with db.session.begin():
            person = Person.query.get_or_404(person_id)
            numbers = [number.number for number in person.raffle_numbers]
            msg = Message('Tus números de la rifa', recipients=[person.email])
            msg.html = (f'<html>'
                        f'<body style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f9;">'
                        f'<h2 style="color: #3498db;">¡Hola!</h2>'
                        f'<p><strong>Tus números de la rifa son:</strong></p>'
                        f'<p style="font-size: 16px;">{", ".join(map(str, numbers))}</p>'
                        f'<hr style="border: 1px solid #ddd;">'
                        f'<p>¡Gracias por participar!</p>'
                        f'<p>El equipo de Poison G</p>'
                        f'</body>'
                        f'</html>')

            mail.send(msg)
            person.confirmed = True
            db.session.add(person)
            db.session.commit()
            flash('Correo enviado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hubo un problema al enviar el correo. {e}', 'error')
    return redirect(url_for('number.list_person'))