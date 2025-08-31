"""
Render-specific configuration for Maritime Event Extractor
"""

import os

class RenderConfig:
    """Configuration for Render deployment"""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'render-secret-key-change-in-production')
    
    # Database - Use SQLite for simplicity on Render
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/sof_extractor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    # AI service settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # CORS settings for Render
    CORS_ORIGINS = [
        'https://maritime-event-extractor.onrender.com',
        'https://*.onrender.com',
        'http://localhost:3000',
        'http://127.0.0.1:5500'
    ]
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'app.log'
    
    # Render-specific settings
    RENDER = True
    DEBUG = False
