from app import db, login_manager
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    reference_number = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    confirmed = db.Column(db.Boolean, default=False) # Confirmar si la persona ha pagado

    # Relación uno a muchos con RaffleNumber
    raffle_numbers = db.relationship('RaffleNumber', backref='person', lazy=True)


class RaffleNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    raffle_id = db.Column(db.Integer, db.ForeignKey('raffle.id'), nullable=False)

    # Relación con el modelo Raffle
    raffle = db.relationship('Raffle', backref='raffle_numbers', lazy=True)
    person = db.relationship('Person', backref='raffle_numbers', lazy=True)

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
    image_filename = db.Column(db.String(255))  # Campo para almacenar el nombre del archivo de la imagen

