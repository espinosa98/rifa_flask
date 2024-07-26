from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
import random
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email', '')
        num_numbers = request.form.get('num_numbers', '5')  # Valor predeterminado si no está presente
        custom_number = request.form.get('custom_number', '')

        # Manejar la opción personalizada
        if num_numbers == 'custom':
            if custom_number:
                num_numbers = int(custom_number)
            else:
                # Manejar el caso en el que el campo personalizado está vacío
                num_numbers = 5  # O puedes enviar un mensaje de error o manejarlo de otra manera
        else:
            num_numbers = int(num_numbers)

        bank_account = request.form.get('bank_account', '')
        reference = request.form.get('reference', '')

        # Generar números de la rifa
        numbers = [random.randint(1, 100) for _ in range(num_numbers)]

        # Crear el mensaje
        msg = Message('Tus números de la rifa', recipients=[email])
        msg.body = (f'Tus números de la rifa son: {", ".join(map(str, numbers))}\n\n'
                    f'Información de la cuenta bancaria: {bank_account}\n'
                    f'Referencia de consignación: {reference}')

        try:
            mail.send(msg)
            print('Correo enviado con éxito')
        except Exception as e:
            print(f'Error al enviar correo: {e}')

        return redirect(url_for('index'))

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

