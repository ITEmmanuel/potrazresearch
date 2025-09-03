# POTRAZ Research - Ubuntu Server Deployment Guide

## Server Information
- **IP Address**: 185.181.8.83
- **Hostname**: 185-181-8-83.cloud-xip.com
- **OS**: Ubuntu Server
- **Application**: Flask-based Plagiarism Detection System

## Prerequisites

### 1. SSH Access to Server
```bash
ssh root@185.181.8.83
# or if you have a specific user
ssh username@185.181.8.83
```

### 2. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

## Step 1: Install Required Software

### Install Python and Dependencies
```bash
# Install Python 3.9+ and pip
sudo apt install python3 python3-pip python3-venv python3-dev -y

# Install Git
sudo apt install git -y

# Install MySQL Server
sudo apt install mysql-server mysql-client -y

# Install Nginx (Web Server)
sudo apt install nginx -y

# Install system dependencies for Python packages
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
sudo apt install pkg-config default-libmysqlclient-dev -y
```

## Step 2: Secure MySQL Installation

```bash
# Run MySQL secure installation
sudo mysql_secure_installation

# Follow the prompts:
# - Set root password (choose a strong password)
# - Remove anonymous users: Y
# - Disallow root login remotely: Y
# - Remove test database: Y
# - Reload privilege tables: Y
```

### Configure MySQL
```bash
# Login to MySQL as root
sudo mysql -u root -p

# Create database and user (in MySQL prompt)
CREATE DATABASE potplag CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'potplag'@'localhost' IDENTIFIED BY 'potplag_secure_password_123';
GRANT ALL PRIVILEGES ON potplag.* TO 'potplag'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Step 3: Clone and Setup Application

### Create Application Directory
```bash
# Create application user
sudo adduser --system --group potraz

# Create application directory
sudo mkdir -p /var/www/potrazresearch
sudo chown potraz:potraz /var/www/potrazresearch

# Switch to application directory
cd /var/www/potrazresearch
```

### Clone Repository
```bash
# Clone the repository
sudo -u potraz git clone https://github.com/ITEmmanuel/potrazresearch.git .

# Set proper permissions
sudo chown -R potraz:potraz /var/www/potrazresearch
```

### Setup Python Virtual Environment
```bash
# Create virtual environment
sudo -u potraz python3 -m venv venv

# Activate virtual environment
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install --upgrade pip

# Install Python dependencies
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install Flask
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install Flask-SQLAlchemy
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install Flask-Login
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install Flask-Migrate
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install Flask-WTF
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install WTForms
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install Werkzeug
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install python-dotenv
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install cryptography
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install PyMySQL
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install gunicorn
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install requests
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install selenium
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install pandas
sudo -u potraz /var/www/potrazresearch/venv/bin/pip install numpy
```

## Step 4: Configure Environment Variables

### Create Production Environment File
```bash
# Create .env file for production
sudo -u potraz tee /var/www/potrazresearch/.env << 'EOF'
# Flask Configuration
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=your-super-secure-production-secret-key-change-this

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=potplag
MYSQL_PASSWORD=potplag_secure_password_123
MYSQL_DATABASE=potplag

# Admin Account Configuration
ADMIN_EMAIL=admin@potplag.com
ADMIN_PASSWORD=secure_admin_password_change_this

# Production Settings
TALISMAN_FORCE_HTTPS=false
EOF
```

### Create WSGI Entry Point
```bash
# Create wsgi.py file
sudo -u potraz tee /var/www/potrazresearch/wsgi.py << 'EOF'
#!/usr/bin/env python3
from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
EOF
```

## Step 5: Initialize Database

### Run Database Setup
```bash
# Switch to application directory
cd /var/www/potrazresearch

# Run the database setup script
sudo -u potraz /var/www/potrazresearch/venv/bin/python setup_database_complete.py
```

## Step 6: Configure Gunicorn (WSGI Server)

### Create Gunicorn Configuration
```bash
# Create gunicorn configuration file
sudo tee /var/www/potrazresearch/gunicorn_config.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
user = "potraz"
group = "potraz"
chdir = "/var/www/potrazresearch"
pythonpath = "/var/www/potrazresearch"
raw_env = [
    'FLASK_ENV=production',
]
EOF
```

### Create Systemd Service for Gunicorn
```bash
# Create systemd service file
sudo tee /etc/systemd/system/potrazresearch.service << 'EOF'
[Unit]
Description=Gunicorn instance to serve POTRAZ Research
After=network.target

[Service]
User=potraz
Group=potraz
WorkingDirectory=/var/www/potrazresearch
Environment="PATH=/var/www/potrazresearch/venv/bin"
ExecStart=/var/www/potrazresearch/venv/bin/gunicorn --config gunicorn_config.py wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### Enable and Start the Service
```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable potrazresearch

# Start the service
sudo systemctl start potrazresearch

# Check service status
sudo systemctl status potrazresearch
```

## Step 7: Configure Nginx (Reverse Proxy)

### Create Nginx Configuration
```bash
# Remove default nginx site
sudo rm /etc/nginx/sites-enabled/default

# Create new site configuration
sudo tee /etc/nginx/sites-available/potrazresearch << 'EOF'
server {
    listen 80;
    server_name 185.181.8.83 185-181-8-83.cloud-xip.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Serve static files directly
    location /static {
        alias /var/www/potrazresearch/app/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Handle file uploads (larger files)
    client_max_body_size 20M;

    # Main application
    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        proxy_pass http://127.0.0.1:5000;
    }

    # Logging
    access_log /var/log/nginx/potrazresearch_access.log;
    error_log /var/log/nginx/potrazresearch_error.log;
}
EOF
```

### Enable Site and Restart Nginx
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/potrazresearch /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Enable nginx to start on boot
sudo systemctl enable nginx
```

## Step 8: Configure Firewall

```bash
# Install UFW if not already installed
sudo apt install ufw -y

# Allow SSH (important - don't lock yourself out!)
sudo ufw allow ssh

# Allow HTTP traffic
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw --force enable

# Check firewall status
sudo ufw status
```

## Step 9: Create Required Directories

```bash
# Create upload and download directories
sudo -u potraz mkdir -p /var/www/potrazresearch/uploads
sudo -u potraz mkdir -p /var/www/potrazresearch/downloads
sudo -u potraz mkdir -p /var/www/potrazresearch/logs

# Set proper permissions
sudo chmod 755 /var/www/potrazresearch/uploads
sudo chmod 755 /var/www/potrazresearch/downloads
sudo chmod 755 /var/www/potrazresearch/logs
```

## Step 10: Final Verification

### Check All Services
```bash
# Check if services are running
sudo systemctl status potrazresearch
sudo systemctl status nginx
sudo systemctl status mysql

# Check if application is accessible
curl -I http://185.181.8.83
curl -I http://185-181-8-83.cloud-xip.com
```

### View Logs
```bash
# Application logs
sudo journalctl -u potrazresearch -f

# Nginx logs
sudo tail -f /var/log/nginx/potrazresearch_access.log
sudo tail -f /var/log/nginx/potrazresearch_error.log
```

## Access Your Application

Your POTRAZ Research application should now be accessible at:
- **HTTP**: http://185.181.8.83
- **HTTP**: http://185-181-8-83.cloud-xip.com

### Login Credentials

**Admin Account:**
- Email: admin@potplag.com
- Password: secure_admin_password_change_this

**Test Accounts:**
- Username format: [username]@test.com (e.g., john.researcher@test.com)
- Password: test123 (for all test accounts)

## Maintenance Commands

### Restart Application
```bash
sudo systemctl restart potrazresearch
sudo systemctl restart nginx
```

### Update Application
```bash
cd /var/www/potrazresearch
sudo -u potraz git pull origin master
sudo systemctl restart potrazresearch
```

### View Logs
```bash
# Real-time application logs
sudo journalctl -u potrazresearch -f

# Real-time nginx logs
sudo tail -f /var/log/nginx/potrazresearch_access.log
```

### Backup Database
```bash
mysqldump -u potplag -p potplag > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Security Notes

1. **Change Default Passwords**: Update all default passwords in production
2. **SSL Certificate**: Consider adding SSL certificate for HTTPS
3. **Regular Updates**: Keep system and packages updated
4. **Backup Strategy**: Implement regular database and file backups
5. **Monitor Logs**: Regularly check application and system logs

## Troubleshooting

If the application isn't working:

1. Check service status: `sudo systemctl status potrazresearch`
2. Check logs: `sudo journalctl -u potrazresearch -n 50`
3. Check nginx: `sudo nginx -t && sudo systemctl status nginx`
4. Check database connection: `mysql -u potplag -p potplag -e "SHOW TABLES;"`
5. Check file permissions: `ls -la /var/www/potrazresearch/`

---

**Deployment completed!** Your POTRAZ Research application should now be live and accessible from the internet.
