import os

class Config:
    # Utilisez la chaîne de connexion appropriée pour votre base de données
    SECRET_KEY = os.environ.get('SECRET_KEY', 'asmasara123')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://asmasara:asmasara123@localhost:3307/banking_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Pour le débogage

    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    