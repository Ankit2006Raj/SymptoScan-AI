import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

import warnings

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # File Upload Limits (Max 5MB to prevent DoS)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    
    # Database
    # Use SQLite for local development by default
    default_db_path = '/tmp/app.db' if os.environ.get('VERCEL') == '1' else os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + default_db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
    def __init__(self):
        super().__init__()
        if not os.environ.get('SECRET_KEY'):
            warnings.warn("CRITICAL: SECRET_KEY is not set in production. Using insecure default.", RuntimeWarning)
        
        if not os.environ.get('DATABASE_URL') and os.environ.get('VERCEL') == '1':
            warnings.warn("CRITICAL: Using /tmp/app.db on Vercel. Data will be lost on every request! Set DATABASE_URL.", RuntimeWarning)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
