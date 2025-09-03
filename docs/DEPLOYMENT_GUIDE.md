# POTPLAG Deployment Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Development Setup](#development-setup)
3. [Production Deployment](#production-deployment)
4. [Database Configuration](#database-configuration)
5. [Environment Variables](#environment-variables)
6. [Web Server Configuration](#web-server-configuration)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 10GB minimum, 50GB recommended
- **Network**: Stable internet connection for academi.cx integration

### Software Dependencies

- Python 3.8+
- MySQL 8.0+ or PostgreSQL 13+ (optional, SQLite fallback available)
- Chrome/Chromium browser (for Selenium automation)
- Redis (optional, for future caching/task queue)
- Nginx (recommended for production)
- Gunicorn or uWSGI (for production WSGI)

## Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd potplag
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

### 5. Database Setup

```bash
# Initialize database (if using Flask-Migrate)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Or let the app create tables automatically
python wsgi.py
```

### 6. Run Development Server

```bash
# Using Flask development server
flask run

# Or using Python directly
python wsgi.py

# Or using Gunicorn for testing
gunicorn wsgi:app
```

The application will be available at `http://localhost:5000`.

## Production Deployment

### Option 1: Traditional Server Deployment

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install python3 python3-pip python3-venv nginx mysql-server -y

# Install Chrome for Selenium
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y
```

#### 2. Application Setup

```bash
# Create application directory
sudo mkdir /opt/potplag
cd /opt/potplag

# Clone application
sudo git clone <repository-url> .
sudo chown -R www-data:www-data /opt/potplag

# Switch to application user
sudo -u www-data bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Configuration

```bash
# Create production environment file
cat > .env << EOF
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=potplag
MYSQL_PASSWORD=secure_password
MYSQL_DATABASE=potplag

# Admin Account
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=secure_admin_password

# Academi.cx Integration
ACADEMI_EMAIL=your_email@example.com
ACADEMI_PASSWORD=your_password
EOF

# Set secure permissions
chmod 600 .env
```

#### 4. Database Setup

```bash
# Create MySQL database and user
sudo mysql -u root -p << EOF
CREATE DATABASE potplag CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'potplag'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON potplag.* TO 'potplag'@'localhost';
FLUSH PRIVILEGES;
EOF

# Initialize database
source venv/bin/activate
python wsgi.py  # This will create tables automatically
```

#### 5. Systemd Service

```bash
# Create systemd service file
sudo tee /etc/systemd/system/potplag.service << EOF
[Unit]
Description=POTPLAG Plagiarism Detection Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/potplag
Environment=PATH=/opt/potplag/venv/bin
ExecStart=/opt/potplag/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable potplag
sudo systemctl start potplag
sudo systemctl status potplag
```

### Option 2: Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create directories
RUN mkdir -p uploads downloads status

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "wsgi:app"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=mysql+pymysql://potplag:${MYSQL_PASSWORD}@db:3306/potplag
      - ADMIN_EMAIL=${ADMIN_EMAIL}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - ACADEMI_EMAIL=${ACADEMI_EMAIL}
      - ACADEMI_PASSWORD=${ACADEMI_PASSWORD}
    volumes:
      - uploads:/app/uploads
      - downloads:/app/downloads
      - status:/app/status
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=potplag
      - MYSQL_USER=potplag
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  mysql_data:
  uploads:
  downloads:
  status:
```

### Option 3: Cloud Deployment (AWS/GCP/Azure)

#### AWS Elastic Beanstalk

1. Create `requirements.txt` with all dependencies
2. Create `application.py` (symlink to `wsgi.py`)
3. Create `.ebextensions/01_packages.config`:

```yaml
packages:
  yum:
    git: []
    
commands:
  01_install_chrome:
    command: |
      curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
      echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
      apt-get -y update
      apt-get -y install google-chrome-stable
```

4. Deploy with EB CLI:

```bash
eb init potplag --region us-east-1
eb create production
eb deploy
```

## Database Configuration

### MySQL Configuration

```sql
-- Create database with proper charset
CREATE DATABASE potplag CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user with appropriate permissions
CREATE USER 'potplag'@'%' IDENTIFIED BY 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER ON potplag.* TO 'potplag'@'%';
FLUSH PRIVILEGES;

-- Optimize MySQL for application
SET GLOBAL innodb_buffer_pool_size = 1G;
SET GLOBAL max_connections = 200;
```

### PostgreSQL Configuration

```sql
-- Create database and user
CREATE DATABASE potplag;
CREATE USER potplag WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE potplag TO potplag;

-- Connect to database and grant schema permissions
\c potplag
GRANT ALL ON SCHEMA public TO potplag;
```

## Environment Variables

### Required Variables

```bash
# Core Flask Configuration
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key

# Database (choose one option)
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
# OR
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=potplag
MYSQL_PASSWORD=secure_password
MYSQL_DATABASE=potplag

# Admin Account
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=secure_admin_password

# Academi.cx Integration
ACADEMI_EMAIL=your_email@example.com
ACADEMI_PASSWORD=your_password
```

### Optional Variables

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Security Headers
TALISMAN_FORCE_HTTPS=true

# Performance Tuning
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_TIMEOUT=20
SQLALCHEMY_POOL_RECYCLE=3600
```

## Web Server Configuration

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/potplag
server {
    listen 80;
    server_name potplag.yourcompany.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name potplag.yourcompany.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/potplag.crt;
    ssl_certificate_key /etc/ssl/private/potplag.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # File Upload Configuration
    client_max_body_size 16M;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static Files (if served by nginx)
    location /static/ {
        alias /opt/potplag/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security - Hide server tokens
    server_tokens off;

    # Logging
    access_log /var/log/nginx/potplag_access.log;
    error_log /var/log/nginx/potplag_error.log;
}
```

### Apache Configuration

```apache
<VirtualHost *:80>
    ServerName potplag.yourcompany.com
    Redirect permanent / https://potplag.yourcompany.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName potplag.yourcompany.com
    
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/potplag.crt
    SSLCertificateKeyFile /etc/ssl/private/potplag.key
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    # File upload size
    LimitRequestBody 16777216
    
    # Security headers
    Header always set Strict-Transport-Security "max-age=63072000"
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
</VirtualHost>
```

## SSL/TLS Configuration

### Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d potplag.yourcompany.com

# Auto-renewal (already configured by default)
sudo systemctl status certbot.timer
```

### Manual SSL Certificate

```bash
# Generate private key
openssl genrsa -out potplag.key 2048

# Generate certificate signing request
openssl req -new -key potplag.key -out potplag.csr

# Install certificate files
sudo cp potplag.crt /etc/ssl/certs/
sudo cp potplag.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/potplag.key
```

## Monitoring and Maintenance

### System Monitoring

```bash
# Monitor application logs
sudo journalctl -u potplag -f

# Monitor nginx logs
sudo tail -f /var/log/nginx/potplag_error.log

# Monitor system resources
htop
df -h
free -m
```

### Application Health Checks

Create a health check endpoint:

```python
# Add to main routes
@bp.route('/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'timestamp': datetime.utcnow()}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

### Backup Strategy

```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump potplag > /backups/potplag_$DATE.sql
find /backups -name "potplag_*.sql" -mtime +7 -delete

# File backup
tar -czf /backups/potplag_files_$DATE.tar.gz /opt/potplag/uploads /opt/potplag/downloads
```

### Log Rotation

```bash
# Configure logrotate
sudo tee /etc/logrotate.d/potplag << EOF
/var/log/nginx/potplag_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    postrotate
        systemctl reload nginx
    endscript
}
EOF
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check MySQL service
sudo systemctl status mysql

# Test connection
mysql -u potplag -p -h localhost potplag

# Check configuration
cat .env | grep MYSQL
```

#### 2. Selenium/Chrome Issues

```bash
# Install Chrome dependencies
sudo apt install -y libnss3 libxss1 libasound2 libxrandr2 libatk1.0-0 libgtk-3-0 libdrm2

# Check Chrome installation
google-chrome --version

# Run in headless mode
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

#### 3. File Permission Issues

```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/potplag

# Fix permissions
sudo chmod -R 755 /opt/potplag
sudo chmod -R 777 /opt/potplag/uploads
sudo chmod -R 777 /opt/potplag/downloads
sudo chmod 600 /opt/potplag/.env
```

#### 4. Performance Issues

```bash
# Monitor system resources
top
iostat 1
netstat -tuln

# Check application metrics
sudo systemctl status potplag
sudo journalctl -u potplag --since "1 hour ago"
```

### Debugging

Enable debug logging in production:

```python
# In config.py
import logging

class ProductionConfig(Config):
    DEBUG = False
    LOGGING_LEVEL = logging.INFO
    
    @staticmethod
    def init_app(app):
        # Configure logging
        handler = logging.FileHandler('/var/log/potplag/app.log')
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
```

### Performance Tuning

```bash
# Gunicorn workers calculation
workers = (2 * CPU_cores) + 1

# Start with optimized Gunicorn
gunicorn --workers 4 --worker-class gevent --worker-connections 1000 --bind 0.0.0.0:8000 wsgi:app
```

## Security Checklist

- [ ] Environment variables properly configured
- [ ] Database credentials secured
- [ ] SSL/TLS enabled and configured
- [ ] Security headers configured
- [ ] File upload restrictions enforced
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Log monitoring configured
- [ ] Firewall properly configured
- [ ] Admin account secured with strong password

## Maintenance Schedule

### Daily
- Monitor application logs
- Check disk space
- Monitor performance metrics

### Weekly
- Review security logs
- Check backup integrity
- Update system packages

### Monthly
- Security patches review
- Performance optimization
- Backup retention cleanup
- SSL certificate expiry check
