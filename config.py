import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = ''

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://{username}:{password}@{hostname}/{database}'.format(
            username=os.environ.get('DB_USERNAME', 'your-username'),
            password=os.environ.get('DB_PASSWORD', 'your-password'),
            hostname=os.environ.get('DB_HOSTNAME', 'your-hostname.mysql.pythonanywhere-services.com'),
            database=os.environ.get('DB_NAME', 'your-database-name')
        )

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'testing': DevelopmentConfig,
    'staging': ProductionConfig
}
