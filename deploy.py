#!/usr/bin/env python3
"""
Maritime Event Extractor Deployment Script
Deploys the application to production environment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'spacy', 'PyPDF2', 'pandas', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_spacy_model():
    """Check if spaCy model is available"""
    print("\n🔍 Checking spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model 'en_core_web_sm' loaded successfully")
        return True
    except OSError:
        print("❌ spaCy model 'en_core_web_sm' not found")
        print("Installing...")
        try:
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            print("✅ spaCy model installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install spaCy model")
            return False

def run_tests():
    """Run comprehensive tests"""
    print("\n🧪 Running tests...")
    
    try:
        # Test the enhanced extractor
        from backend.enhanced_maritime_extractor import EnhancedMaritimeExtractor
        extractor = EnhancedMaritimeExtractor()
        
        # Test with sample text
        test_text = "Vessel MV OCEAN BEAUTY arrived at port at 06:45 on 15/03/2024. Pilot boarded at 07:00."
        events = extractor.extract_events(test_text)
        
        print(f"✅ Enhanced extractor working - Found {len(events)} events")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def create_production_config():
    """Create production configuration"""
    print("\n⚙️ Creating production configuration...")
    
    config = {
        "production": True,
        "debug": False,
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 4,
        "timeout": 120,
        "max_requests": 1000
    }
    
    with open("production_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Production configuration created")

def create_systemd_service():
    """Create systemd service file for production"""
    print("\n🔧 Creating systemd service...")
    
    service_content = """[Unit]
Description=Maritime Event Extractor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={}
ExecStart={}/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
""".format(os.getcwd(), os.getcwd())
    
    with open("maritime-extractor.service", "w") as f:
        f.write(service_content)
    
    print("✅ Systemd service file created")
    print("📝 To install: sudo cp maritime-extractor.service /etc/systemd/system/")
    print("📝 To enable: sudo systemctl enable maritime-extractor")
    print("📝 To start: sudo systemctl start maritime-extractor")

def create_nginx_config():
    """Create nginx configuration"""
    print("\n🌐 Creating nginx configuration...")
    
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/app/frontend;
        expires 30d;
    }
}
"""
    
    with open("nginx.conf", "w") as f:
        f.write(nginx_config)
    
    print("✅ Nginx configuration created")
    print("📝 Copy to /etc/nginx/sites-available/ and enable")

def create_docker_compose():
    """Create Docker Compose configuration"""
    print("\n🐳 Creating Docker Compose configuration...")
    
    docker_compose = """version: '3.8'

services:
  maritime-extractor:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./instance:/app/instance
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///instance/sof_extractor.db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - maritime-extractor
    restart: unless-stopped
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    print("✅ Docker Compose configuration created")

def main():
    """Main deployment function"""
    print("🚀 Maritime Event Extractor Deployment")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return
    
    # Check spaCy model
    if not check_spacy_model():
        print("\n❌ spaCy model check failed.")
        return
    
    # Run tests
    if not run_tests():
        print("\n❌ Tests failed. Please fix issues before deployment.")
        return
    
    # Create production configurations
    create_production_config()
    create_systemd_service()
    create_nginx_config()
    create_docker_compose()
    
    print("\n🎉 Deployment preparation completed!")
    print("\n📋 Next steps:")
    print("1. Test the application: python app.py")
    print("2. For production with Gunicorn: gunicorn -c gunicorn_config.py app:app")
    print("3. For Docker: docker-compose up -d")
    print("4. For systemd: Follow the service installation instructions above")

if __name__ == "__main__":
    main()
