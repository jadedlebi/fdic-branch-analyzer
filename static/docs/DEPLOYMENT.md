# FDIC Branch Analyzer - Deployment Guide

## Overview

This guide covers deploying the FDIC Branch Analyzer for production use, including both the web interface and API services.

## Prerequisites

- Python 3.8+
- Google Cloud Platform account with BigQuery access
- Claude API key
- Domain name (optional)
- SSL certificate (recommended)

## Deployment Options

### 1. GitHub Pages (Static Site)

For the web interface only:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push origin main
   ```

2. **Enable GitHub Pages**:
   - Go to repository Settings > Pages
   - Source: Deploy from a branch
   - Branch: main
   - Folder: /web
   - Save

3. **Custom Domain** (optional):
   - Add your domain in GitHub Pages settings
   - Update DNS records
   - Add CNAME file to /web directory

### 2. Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "run_web.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  fdic-analyzer:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - BQ_TYPE=${BQ_TYPE}
      - BQ_PROJECT_ID=${BQ_PROJECT_ID}
      - BQ_PRIVATE_KEY=${BQ_PRIVATE_KEY}
      - BQ_CLIENT_EMAIL=${BQ_CLIENT_EMAIL}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    volumes:
      - ./data:/app/data
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
      - fdic-analyzer
    restart: unless-stopped
```

### 3. Cloud Deployment

#### Google Cloud Run

1. **Build and Deploy**:
   ```bash
   # Build container
   gcloud builds submit --tag gcr.io/PROJECT_ID/fdic-analyzer

   # Deploy to Cloud Run
   gcloud run deploy fdic-analyzer \
     --image gcr.io/PROJECT_ID/fdic-analyzer \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars SECRET_KEY=your-secret-key
   ```

2. **Set Environment Variables**:
   ```bash
   gcloud run services update fdic-analyzer \
     --set-env-vars BQ_TYPE=service_account,BQ_PROJECT_ID=your-project-id
   ```

#### AWS Elastic Beanstalk

1. **Create Application**:
   ```bash
   eb init fdic-analyzer --platform python-3.9
   eb create fdic-analyzer-prod
   ```

2. **Configure Environment**:
   ```bash
   eb setenv SECRET_KEY=your-secret-key
   eb setenv BQ_TYPE=service_account
   eb setenv BQ_PROJECT_ID=your-project-id
   ```

3. **Deploy**:
   ```bash
   eb deploy
   ```

## Environment Configuration

### Required Environment Variables

```bash
# Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# BigQuery
BQ_TYPE=service_account
BQ_PROJECT_ID=your-project-id
BQ_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
BQ_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com

# AI Services
CLAUDE_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-api-key

# Database (if using external database)
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis (for caching)
REDIS_URL=redis://localhost:6379
```

### Security Best Practices

1. **Use Environment Variables**: Never hardcode secrets
2. **Rotate Keys Regularly**: Update API keys and service account credentials
3. **Limit Permissions**: Use least-privilege access for service accounts
4. **Enable Audit Logging**: Monitor access and usage
5. **Use HTTPS**: Always use SSL/TLS in production

## Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream fdic_analyzer {
        server fdic-analyzer:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
        limit_req zone=api burst=20 nodelay;

        location / {
            proxy_pass http://fdic_analyzer;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## Monitoring and Logging

### Application Monitoring

1. **Health Checks**:
   ```python
   @app.route('/health')
   def health():
       return jsonify({
           'status': 'healthy',
           'timestamp': datetime.now().isoformat(),
           'version': '1.0.0'
       })
   ```

2. **Logging Configuration**:
   ```python
   import logging
   from logging.handlers import RotatingFileHandler

   if not app.debug:
       file_handler = RotatingFileHandler('logs/fdic-analyzer.log', maxBytes=10240, backupCount=10)
       file_handler.setFormatter(logging.Formatter(
           '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
       ))
       file_handler.setLevel(logging.INFO)
       app.logger.addHandler(file_handler)
       app.logger.setLevel(logging.INFO)
       app.logger.info('FDIC Analyzer startup')
   ```

### Performance Monitoring

1. **Enable Metrics**:
   ```python
   from prometheus_client import Counter, Histogram, generate_latest

   request_count = Counter('http_requests_total', 'Total HTTP requests')
   request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

   @app.route('/metrics')
   def metrics():
       return generate_latest()
   ```

2. **Database Monitoring**:
   - Monitor BigQuery usage and costs
   - Set up alerts for quota limits
   - Track query performance

## Backup and Recovery

### Data Backup

1. **Configuration Backup**:
   ```bash
   # Backup environment variables
   env | grep -E "(BQ_|CLAUDE_|OPENAI_)" > backup.env
   ```

2. **Application Backup**:
   ```bash
   # Backup application code
   tar -czf fdic-analyzer-backup-$(date +%Y%m%d).tar.gz .
   ```

### Disaster Recovery

1. **Recovery Procedures**:
   - Document recovery steps
   - Test recovery procedures regularly
   - Maintain backup copies off-site

2. **Rollback Strategy**:
   - Use version tags for deployments
   - Maintain previous versions
   - Test rollback procedures

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use multiple instances behind a load balancer
2. **Session Management**: Use Redis for session storage
3. **Database Connection Pooling**: Optimize BigQuery connections

### Performance Optimization

1. **Caching**: Cache frequently accessed data
2. **CDN**: Use CDN for static assets
3. **Compression**: Enable gzip compression
4. **Database Optimization**: Optimize BigQuery queries

## Security Checklist

- [ ] Environment variables configured
- [ ] HTTPS enabled
- [ ] Security headers set
- [ ] Rate limiting configured
- [ ] Input validation implemented
- [ ] Error handling configured
- [ ] Logging enabled
- [ ] Monitoring set up
- [ ] Backup procedures documented
- [ ] Recovery procedures tested

## Troubleshooting

### Common Issues

1. **BigQuery Connection Errors**:
   - Check service account permissions
   - Verify project ID
   - Check network connectivity

2. **API Key Issues**:
   - Verify API keys are valid
   - Check rate limits
   - Monitor usage quotas

3. **Memory Issues**:
   - Monitor memory usage
   - Optimize data processing
   - Consider caching strategies

### Debug Mode

For debugging, enable debug mode temporarily:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

**Note**: Never use debug mode in production.

## Support

For deployment support:
- Email: deployment-support@ncrc.org
- Documentation: https://docs.fdic-analyzer.ncrc.org/deployment
- GitHub Issues: https://github.com/jadedlebi/fdic-branch-analyzer/issues 