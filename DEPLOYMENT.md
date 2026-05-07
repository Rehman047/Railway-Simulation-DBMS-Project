# Deployment Guide

## Production Deployment

### Prerequisites

- Server with Ubuntu 20.04+
- Python 3.8+
- PostgreSQL 12+
- Nginx or Apache
- SSL certificate (Let's Encrypt)

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# Create application user
sudo useradd -m -s /bin/bash railway
sudo usermod -aG sudo railway
```

### Step 2: Clone and Setup Application

```bash
# Switch to railway user
sudo su - railway

# Clone repository
git clone https://github.com/yourrepo/railway-simulation-dbms.git
cd Railway-Simulation-DBMS-Project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Step 3: Configure Environment

```bash
# Create .env file with production settings
cat > .env << EOF
FLASK_ENV=production
DB_HOST=localhost
DB_NAME=railway_db
DB_USER=railway_user
DB_PASSWORD=strong_password_here
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FIREBASE_CREDENTIALS_PATH=/home/railway/firebase-credentials.json
EOF

chmod 600 .env
```

### Step 4: Setup PostgreSQL

```bash
# Connect as postgres
sudo -i -u postgres

# Create database and user
psql << EOF
CREATE DATABASE railway_db;
CREATE USER railway_user WITH PASSWORD 'strong_password_here';
ALTER ROLE railway_user SET client_encoding TO 'utf8';
ALTER ROLE railway_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE railway_user SET default_transaction_deferrable TO on;
ALTER ROLE railway_user SET default_transaction_read_uncommitted TO off;
GRANT ALL PRIVILEGES ON DATABASE railway_db TO railway_user;
EOF

# Exit postgres user
exit

# Initialize database schema
cd /home/railway/Railway-Simulation-DBMS-Project
psql -U railway_user -d railway_db -f database/schema.sql
psql -U railway_user -d railway_db -f database/seed.sql
psql -U railway_user -d railway_db -f database/indexes.sql
psql -U railway_user -d railway_db -f database/views_procedures.sql
```

### Step 5: Setup Gunicorn

```bash
# Create systemd service file
sudo tee /etc/systemd/system/railway-dbms.service > /dev/null << EOF
[Unit]
Description=Railway DBMS Flask Application
After=network.target

[Service]
User=railway
Group=www-data
WorkingDirectory=/home/railway/Railway-Simulation-DBMS-Project
Environment="PATH=/home/railway/Railway-Simulation-DBMS-Project/venv/bin"
ExecStart=/home/railway/Railway-Simulation-DBMS-Project/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    run:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable railway-dbms
sudo systemctl start railway-dbms
sudo systemctl status railway-dbms
```

### Step 6: Setup Nginx

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/railway-dbms > /dev/null << 'EOF'
upstream railway_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy settings
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://railway_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files caching
    location /static/ {
        alias /home/railway/Railway-Simulation-DBMS-Project/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # File uploads
    location /uploads/ {
        alias /home/railway/Railway-Simulation-DBMS-Project/uploads/;
        expires 7d;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/railway-dbms /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx
sudo nginx -t

# Start Nginx
sudo systemctl restart nginx
```

### Step 7: Setup SSL Certificate

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Step 8: Setup Backups

```bash
# Create backup script
sudo tee /home/railway/backup-railway.sh > /dev/null << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/railway-dbms"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="railway_db"
DB_USER="railway_user"

mkdir -p $BACKUP_DIR

# Database backup
PGPASSWORD="strong_password_here" pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Application backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/railway/Railway-Simulation-DBMS-Project

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

# Make executable
chmod +x /home/railway/backup-railway.sh

# Schedule daily backup at 2 AM
sudo bash -c 'echo "0 2 * * * /home/railway/backup-railway.sh" | crontab -'
```

### Step 9: Monitor Application

```bash
# View application logs
sudo journalctl -u railway-dbms -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Database connection check
psql -U railway_user -d railway_db -c "SELECT version();"
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  database:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: railway_db
      POSTGRES_USER: railway_user
      POSTGRES_PASSWORD: strong_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database:/docker-entrypoint-initdb.d

  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      DB_HOST: database
      DB_NAME: railway_db
      DB_USER: railway_user
      DB_PASSWORD: strong_password
    depends_on:
      - database
    volumes:
      - ./uploads:/app/uploads

volumes:
  postgres_data:
```

### Deployment Commands

```bash
# Build image
docker build -t railway-dbms:latest .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f app

# Stop application
docker-compose down
```

## Health Checks

```bash
# Application health
curl http://localhost:5000/api/analytics/dashboard

# Database connection
psql -U railway_user -d railway_db -c "SELECT COUNT(*) FROM passengers;"

# Nginx status
sudo systemctl status nginx

# Service status
sudo systemctl status railway-dbms
```

## Monitoring & Maintenance

### Log Rotation

```bash
sudo tee /etc/logrotate.d/railway-dbms > /dev/null << EOF
/var/log/railway-dbms/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 railway www-data
    sharedscripts
}
EOF
```

### Performance Tuning

**PostgreSQL (`/etc/postgresql/14/main/postgresql.conf`)**:
```
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
```

**Nginx Connection Limits**:
```
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
```

## Troubleshooting

### Application Won't Start
```bash
# Check systemd logs
sudo journalctl -u railway-dbms -n 50

# Test gunicorn manually
cd /home/railway/Railway-Simulation-DBMS-Project
source venv/bin/activate
gunicorn run:app
```

### Database Connection Issues
```bash
# Test connection
psql -U railway_user -h localhost -d railway_db -c "SELECT 1"

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql.log
```

### High Memory Usage
```bash
# Check gunicorn processes
ps aux | grep gunicorn

# Restart application
sudo systemctl restart railway-dbms

# Monitor memory
watch -n 1 'free -h'
```

## Rollback Procedure

```bash
# Stop application
sudo systemctl stop railway-dbms

# Restore previous version
cd /home/railway
tar -xzf backups/app_previous_date.tar.gz

# Restart
sudo systemctl start railway-dbms
```

## Success Checklist

- [ ] Server configured
- [ ] PostgreSQL running
- [ ] Application deployed
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] Backups scheduled
- [ ] Monitoring enabled
- [ ] Health checks passing
- [ ] Performance acceptable
- [ ] Documentation updated
