# 🚀 Deploying Maritime Event Extractor to Render

## 📋 **Prerequisites**

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Python 3.11+** - For local testing

## 🔧 **Step 1: Prepare Your Repository**

Make sure your repository has these files:
- `app.py` - Main Flask application
- `requirements_render.txt` - Dependencies for Render
- `render.yaml` - Render configuration
- `render_config.py` - Render-specific settings

## 🚀 **Step 2: Deploy to Render**

### **Option A: Using Render Dashboard (Recommended)**

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"

2. **Connect GitHub Repository**
   - Connect your GitHub account
   - Select your repository
   - Choose the branch (usually `main` or `master`)

3. **Configure Service**
   - **Name:** `maritime-event-extractor`
   - **Environment:** `Python 3`
   - **Build Command:** 
     ```bash
     pip install -r requirements_render.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command:** 
     ```bash
     gunicorn app:app --bind 0.0.0.0:$PORT
     ```

4. **Environment Variables**
   - `PYTHON_VERSION`: `3.11.0`
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate a secure key
   - `PORT`: `10000`

5. **Click "Create Web Service"**

### **Option B: Using render.yaml (Blue-Green Deployment)**

1. **Push your code to GitHub**
2. **In Render Dashboard:**
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically use `render.yaml`

## ⚙️ **Step 3: Configure Environment Variables**

In your Render service dashboard, add these environment variables:

```bash
# Required
PYTHON_VERSION=3.11.0
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key-here
PORT=10000

# Optional
LOG_LEVEL=INFO
OPENAI_API_KEY=your-openai-key-if-using-ai
```

## 🔍 **Step 4: Monitor Deployment**

1. **Build Process**
   - Render will install dependencies
   - Download spaCy model
   - Build your application

2. **Health Checks**
   - Service will be available at: `https://your-service-name.onrender.com`
   - Health check endpoint: `/`

## 📊 **Step 5: Test Your Deployment**

### **Test Endpoints**
```bash
# Health check
curl https://your-service-name.onrender.com/

# API test
curl https://your-service-name.onrender.com/api/documents

# Upload test (if you have a test PDF)
curl -X POST -F "file=@test.pdf" https://your-service-name.onrender.com/api/upload
```

### **Test Event Extraction**
```bash
# Test with sample text
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Vessel arrived at port at 06:45"}' \
  https://your-service-name.onrender.com/api/chat
```

## 🚨 **Common Issues & Solutions**

### **Issue 1: Build Fails**
**Solution:** Check requirements.txt and ensure all dependencies are compatible

### **Issue 2: spaCy Model Download Fails**
**Solution:** The build command includes spaCy download, but if it fails:
```bash
# Add to build command
pip install -r requirements_render.txt && python -m spacy download en_core_web_sm --user
```

### **Issue 3: Port Binding Error**
**Solution:** Ensure your app uses `$PORT` environment variable:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### **Issue 4: Database Issues**
**Solution:** SQLite files are ephemeral on Render. For production, consider:
- PostgreSQL database service
- External storage for uploads

## 🔄 **Step 6: Continuous Deployment**

1. **Auto-deploy is enabled by default**
2. **Every push to main branch triggers deployment**
3. **Monitor deployments in Render dashboard**

## 📈 **Step 7: Scale & Monitor**

### **Scaling Options**
- **Starter Plan:** 1 instance, 512MB RAM
- **Standard Plan:** Multiple instances, 1GB RAM
- **Pro Plan:** Custom resources

### **Monitoring**
- **Logs:** Available in Render dashboard
- **Metrics:** Response times, error rates
- **Health Checks:** Automatic monitoring

## 🎯 **Production Considerations**

### **Database**
- **Development:** SQLite (included)
- **Production:** PostgreSQL service on Render

### **File Storage**
- **Development:** Local uploads folder
- **Production:** External storage (AWS S3, Google Cloud)

### **Security**
- **HTTPS:** Automatically provided by Render
- **Environment Variables:** Secure storage
- **CORS:** Configured for production domains

## 📞 **Support**

- **Render Documentation:** [docs.render.com](https://docs.render.com)
- **Community:** [Render Community](https://community.render.com)
- **Status:** [status.render.com](https://status.render.com)

---

## 🎉 **Deployment Complete!**

Your Maritime Event Extractor is now running on Render with:
- ✅ Automatic HTTPS
- ✅ Auto-scaling capabilities
- ✅ Continuous deployment
- ✅ Professional monitoring
- ✅ Global CDN

**Access your app at:** `https://your-service-name.onrender.com`
