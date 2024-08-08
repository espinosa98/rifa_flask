import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    REGISTER_KEY = os.getenv('REGISTER_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///rifa.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    API_KEY = os.getenv('API_KEY')
    API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'
