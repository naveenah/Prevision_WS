# BrandForge AI - Deployment Guide

**Last Updated:** December 21, 2025  
**Version:** 1.0 (Phase 10 Complete)

---

## 📋 Overview

This guide covers all deployment options for BrandForge AI:
- **Local Development** - Running on your machine
- **Docker Deployment** - Containerized deployment
- **Streamlit Cloud** - Cloud hosting (free tier available)
- **Cloud Platforms** - AWS, GCP, Azure deployment

---

## 🔧 Prerequisites

### System Requirements
- **Python:** 3.9+ (3.11 recommended)
- **RAM:** Minimum 2GB, 4GB+ recommended
- **Storage:** 500MB for application + dependencies
- **Network:** Internet connection for API calls

### Required Accounts
- **Google AI Account:** For Gemini API key ([Get Key](https://makersuite.google.com/app/apikey))
- **GitHub Account:** For version control (optional but recommended)
- **Streamlit Cloud Account:** For cloud deployment (optional)

---

## 🚀 Deployment Options

## Option 1: Local Development

### Quick Start
```bash
# Clone repository
git clone <your-repo-url>
cd BrandForge-AI

# Run setup script
chmod +x setup.sh
./setup.sh

# Start application
source venv/bin/activate
streamlit run main.py
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your GOOGLE_API_KEY

# Run application
streamlit run main.py
```

### Accessing the Application
- Open browser to: `http://localhost:8501`
- The app runs on port 8501 by default
- Use Ctrl+C to stop the server

---

## Option 2: Docker Deployment

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Using Docker Compose (Recommended)

**1. Prepare environment:**
```bash
# Create .env file with your API key
cat > .env << EOF
GOOGLE_API_KEY=your_actual_api_key_here
EOF
```

**2. Build and run:**
```bash
# Build and start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

**3. Access application:**
- Open browser to: `http://localhost:8501`

### Using Docker Directly

**Build image:**
```bash
docker build -t brandforge-ai:latest .
```

**Run container:**
```bash
docker run -d \
  --name brandforge-ai \
  -p 8501:8501 \
  -e GOOGLE_API_KEY="your_api_key_here" \
  -v $(pwd)/exports:/app/exports \
  brandforge-ai:latest
```

**Manage container:**
```bash
# View logs
docker logs -f brandforge-ai

# Stop container
docker stop brandforge-ai

# Remove container
docker rm brandforge-ai
```

### Docker Commands Reference

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Enter container shell
docker exec -it brandforge-ai /bin/bash

# View resource usage
docker stats brandforge-ai

# Rebuild image
docker-compose build --no-cache
```

---

## Option 3: Streamlit Cloud Deployment

### Step-by-Step Guide

**1. Prepare Repository**

Ensure your repository has:
- `requirements.txt` (Python dependencies)
- `.python-version` (Python version specification)
- `main.py` (Application entry point)
- `.streamlit/config.toml` (Streamlit configuration)

**2. Push to GitHub**

```bash
# Initialize git (if not already)
git init

# Add files
git add .
git commit -m "Initial commit for deployment"

# Push to GitHub
git remote add origin <your-github-repo-url>
git push -u origin main
```

**3. Deploy on Streamlit Cloud**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `main.py`
6. Click "Advanced settings"
7. Add secrets:
   ```toml
   GOOGLE_API_KEY = "your_api_key_here"
   ```
8. Click "Deploy"

**4. Access Your App**

- Your app will be available at: `https://your-app-name.streamlit.app`
- Deployment takes 2-5 minutes
- App will auto-restart on code changes

### Streamlit Cloud Configuration

**secrets.toml:**
```toml
# In Streamlit Cloud dashboard -> Secrets
GOOGLE_API_KEY = "your_actual_api_key"
```

**config.toml:**
```toml
[server]
headless = true
port = $PORT

[browser]
gatherUsageStats = false
```

### Managing Your Deployment

- **View logs:** In Streamlit Cloud dashboard
- **Update code:** Push to GitHub, auto-deploys
- **Change settings:** Use dashboard settings
- **Delete app:** In app settings

---

## Option 4: Cloud Platform Deployment

### AWS Elastic Beanstalk

**1. Install EB CLI:**
```bash
pip install awsebcli
```

**2. Initialize EB:**
```bash
eb init -p python-3.11 brandforge-ai
```

**3. Create environment:**
```bash
eb create brandforge-env \
  --envvars GOOGLE_API_KEY=your_key_here \
  --instance-type t3.small
```

**4. Deploy updates:**
```bash
eb deploy
```

### Google Cloud Run

**1. Build container:**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/brandforge-ai
```

**2. Deploy:**
```bash
gcloud run deploy brandforge-ai \
  --image gcr.io/YOUR_PROJECT/brandforge-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key_here \
  --port 8501
```

### Azure Container Apps

**1. Create resource group:**
```bash
az group create --name brandforge-rg --location eastus
```

**2. Deploy container:**
```bash
az containerapp up \
  --name brandforge-ai \
  --resource-group brandforge-rg \
  --location eastus \
  --environment brandforge-env \
  --image YOUR_REGISTRY/brandforge-ai:latest \
  --target-port 8501 \
  --ingress external \
  --env-vars GOOGLE_API_KEY=your_key_here
```

---

## 🔐 Security Best Practices

### API Key Management

**Never commit .env files:**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

**Use environment variables:**
```python
import os
api_key = os.getenv('GOOGLE_API_KEY')
```

**Rotate keys regularly:**
- Generate new API keys every 90 days
- Revoke old keys immediately
- Use separate keys for dev/prod

### Docker Security

**Run as non-root user:**
```dockerfile
USER nobody
```

**Scan for vulnerabilities:**
```bash
docker scan brandforge-ai:latest
```

**Use specific base images:**
```dockerfile
FROM python:3.11-slim
```

### Network Security

**Enable HTTPS:**
- Use reverse proxy (nginx, Caddy)
- Configure SSL certificates
- Force HTTPS redirect

**Configure CORS:**
```toml
[server]
enableCORS = false
enableXsrfProtection = true
```

---

## 📊 Monitoring & Maintenance

### Health Checks

**Docker health check:**
```bash
docker inspect --format='{{.State.Health.Status}}' brandforge-ai
```

**Manual health check:**
```bash
curl http://localhost:8501/_stcore/health
```

### Logging

**Docker logs:**
```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f brandforge

# Last 100 lines
docker-compose logs --tail=100 brandforge
```

**Application logs:**
```bash
# Logs are in logs/ directory
tail -f logs/brandforge.log
```

### Performance Monitoring

**Resource usage:**
```bash
# Docker stats
docker stats brandforge-ai

# System resources
htop
```

**API usage:**
- Monitor Gemini API quota
- Track request counts
- Set up usage alerts

### Backup Strategy

**State files:**
```bash
# Backup autosave file
cp .brandforge_autosave.json backup/

# Backup exports
tar -czf exports_backup.tar.gz exports/
```

**Automated backups:**
```bash
# Add to crontab
0 2 * * * /path/to/backup_script.sh
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Port already in use:**
```bash
# Find process using port 8501
lsof -i :8501
# Kill the process
kill -9 <PID>
```

**2. API key not working:**
```bash
# Verify key format
echo $GOOGLE_API_KEY | grep "^AIza"

# Test API key
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=$GOOGLE_API_KEY"
```

**3. Docker build fails:**
```bash
# Clear cache and rebuild
docker-compose build --no-cache

# Check logs
docker-compose logs brandforge
```

**4. Out of memory:**
```bash
# Increase Docker memory limit
# In Docker Desktop: Settings -> Resources -> Memory

# For containers
docker run -m 2g brandforge-ai
```

### Debug Mode

**Enable debug logging:**
```bash
# Set environment variable
export STREAMLIT_LOGGER_LEVEL=debug

# Run with verbose output
streamlit run main.py --logger.level=debug
```

**Check configuration:**
```bash
streamlit config show
```

---

## 🚦 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (44/44)
- [ ] API key configured
- [ ] .env file created (not committed)
- [ ] Dependencies installed
- [ ] Application runs locally
- [ ] Documentation reviewed

### Docker Deployment
- [ ] Dockerfile tested
- [ ] docker-compose.yml configured
- [ ] .dockerignore updated
- [ ] Health checks working
- [ ] Volumes mounted correctly
- [ ] Environment variables set

### Cloud Deployment
- [ ] Repository pushed to GitHub
- [ ] Secrets configured
- [ ] Domain name set (optional)
- [ ] SSL certificate configured
- [ ] Monitoring enabled
- [ ] Backup strategy in place

### Post-Deployment
- [ ] Application accessible
- [ ] All features working
- [ ] API calls successful
- [ ] Exports generating
- [ ] No error logs
- [ ] Performance acceptable

---

## 📚 Additional Resources

### Documentation
- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [Docker Documentation](https://docs.docker.com/)
- [Google Gemini API Docs](https://ai.google.dev/docs)

### Support
- GitHub Issues: Report bugs and feature requests
- Streamlit Community: [discuss.streamlit.io](https://discuss.streamlit.io)
- Docker Community: [forums.docker.com](https://forums.docker.com)

### Related Files
- [README.md](../README.md) - General information
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Development setup
- [TEST_SUMMARY.md](TEST_SUMMARY.md) - Test coverage

---

## 🎯 Production Recommendations

### Recommended Configuration

**Small Team/MVP:**
- **Platform:** Streamlit Cloud (free tier)
- **Monitoring:** Built-in logs
- **Backup:** Manual exports

**Growing Business:**
- **Platform:** Docker on VPS/Cloud
- **Monitoring:** Application logs + health checks
- **Backup:** Automated daily backups

**Enterprise:**
- **Platform:** Kubernetes cluster
- **Monitoring:** Full observability stack
- **Backup:** Multi-region redundancy

### Performance Optimization

**Caching:**
```python
@st.cache_data
def expensive_function():
    # Your code here
```

**Connection pooling:**
```python
@st.cache_resource
def get_api_client():
    return GoogleGenAI()
```

**Lazy loading:**
- Load modules on demand
- Defer heavy computations
- Use pagination for large data

---

## ✅ Phase 10 Complete!

BrandForge AI is now production-ready with:
- ✅ Docker containerization
- ✅ Streamlit Cloud configuration
- ✅ Production setup scripts
- ✅ Comprehensive deployment guide
- ✅ Security best practices
- ✅ Monitoring & troubleshooting

**Ready to deploy to production!** 🚀

---

**Last Updated:** December 21, 2025  
**Deployment Version:** 1.0  
**Status:** Production Ready
