from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from dotenv import load_dotenv
import os
from config import config

db = SQLAlchemy()
cache = Cache()

import logging

def run_startup_checks(app):
    with app.app_context():
        logger = app.logger
        logger.info("Running startup health checks...")
        

        # 2. Dependencies
        try:
            import faiss
            logger.info("FAISS dependency loaded successfully.")
        except ImportError:
            logger.error("CRITICAL: faiss module not found! RAG pipeline will crash. Run: pip install faiss-cpu")
            
        # 3. Model Files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
        required_files = ['faiss.index', 'medical_knowledge.json', 'metadata.pkl']
        for f in required_files:
            if not os.path.exists(os.path.join(data_dir, f)):
                logger.warning(f"CRITICAL: Missing model file: {f}. RAG pipeline may fail.")
        
        # 4. Database Connection
        try:
            db.create_all()
            db.engine.connect()
            logger.info("Database connection and table creation successful.")
        except Exception as e:
            logger.error(f"CRITICAL: Database connection failed: {str(e)}")

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Load environment variables
    load_dotenv()
    
    # Database Configuration
    if os.getenv('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_123')
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})
    
    # Register blueprints
    from .routes.views import views_bp
    from .routes.api import api_bp
    
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Run startup checks
    run_startup_checks(app)
    
    return app
