#!/usr/bin/env python3
"""
Simple Render Deployment Helper
"""

import os
import subprocess
import sys

def check_git_status():
    """Check if repository is ready for deployment"""
    print("🔍 Checking Git status...")
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Not in a Git repository")
            return False
        
        # Check if there are uncommitted changes
        if "nothing to commit" not in result.stdout:
            print("⚠️  You have uncommitted changes")
            print("   Consider committing before deploying")
        
        print("✅ Git repository ready")
        return True
        
    except FileNotFoundError:
        print("❌ Git not found. Please install Git")
        return False

def check_files():
    """Check if required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'app.py',
        'requirements_render.txt',
        'render.yaml',
        'render_config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def show_deployment_steps():
    """Show deployment steps"""
    print("\n🚀 RENDER DEPLOYMENT STEPS")
    print("=" * 50)
    
    print("\n1. 📁 Push to GitHub:")
    print("   git add .")
    print("   git commit -m 'Prepare for Render deployment'")
    print("   git push origin main")
    
    print("\n2. 🌐 Go to Render Dashboard:")
    print("   https://dashboard.render.com")
    print("   Click 'New +' → 'Web Service'")
    
    print("\n3. 🔗 Connect Repository:")
    print("   - Connect GitHub account")
    print("   - Select your repository")
    print("   - Choose 'main' branch")
    
    print("\n4. ⚙️ Configure Service:")
    print("   - Name: maritime-event-extractor")
    print("   - Environment: Python 3")
    print("   - Build Command: pip install -r requirements_render.txt && python -m spacy download en_core_web_sm")
    print("   - Start Command: gunicorn app:app --bind 0.0.0.0:$PORT")
    
    print("\n5. 🔑 Set Environment Variables:")
    print("   - PYTHON_VERSION: 3.11.0")
    print("   - FLASK_ENV: production")
    print("   - SECRET_KEY: [generate secure key]")
    print("   - PORT: 10000")
    
    print("\n6. 🚀 Deploy:")
    print("   - Click 'Create Web Service'")
    print("   - Wait for build to complete")
    print("   - Your app will be available at: https://your-service-name.onrender.com")

def main():
    """Main function"""
    print("🚀 Maritime Event Extractor - Render Deployment Helper")
    print("=" * 60)
    
    # Check prerequisites
    if not check_git_status():
        print("\n❌ Please fix Git issues before deploying")
        return
    
    if not check_files():
        print("\n❌ Please create missing files before deploying")
        return
    
    # Show deployment steps
    show_deployment_steps()
    
    print("\n📚 For detailed instructions, see: RENDER_DEPLOYMENT.md")
    print("🎉 Happy deploying!")

if __name__ == "__main__":
    main()
