# ✅ FINAL DEPLOYMENT CHECKLIST

Complete checklist before deploying to production.

---

## 🔐 SECURITY (CRITICAL)

### Environment Variables
- [ ] **SECRET_KEY** - Generated with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] **EXTENSION_API_KEY** - Strong random API key (32+ characters)
- [ ] **DATABASE_URL** - Production database connection string
- [ ] **REDIS_PASSWORD** - Strong password for Redis
- [ ] **JWT_SECRET** - Separate from SECRET_KEY
- [ ] All passwords changed from defaults
- [ ] No `.env` files committed to Git

### Authentication & Authorization
- [ ] JWT tokens properly configured
- [ ] Token expiration times set appropriately
- [ ] Refresh token mechanism tested
- [ ] Rate limiting enabled and configured
- [ ] API key rotation schedule defined
- [ ] Admin accounts secured

### CORS & Security Headers
- [ ] CORS origins properly configured (no `*` in production)
- [ ] Security headers enabled
- [ ] HTTPS enforced
- [ ] SSL certificates installed and valid

---

## 💾 DATABASE

### Configuration
- [ ] Production database created (PostgreSQL recommended)
- [ ] Database user with appropriate permissions
- [ ] Connection pooling configured
- [ ] Database indexes applied
  ```bash
  python -m backend.db.migrations.add_performance_indexes
  ```
- [ ] Backup strategy configured
- [ ] Retention policy defined

### Performance
- [ ] Slow query logging enabled
- [ ] Query performance monitored
- [ ] Index usage verified

---

## 🚀 BACKEND API

### Configuration
- [ ] `.env` file properly configured
- [ ] `DEBUG=False` in production
- [ ] `LOG_LEVEL=INFO` or `WARNING`
- [ ] Model preloading enabled (`MODEL_PRELOAD=True`)
- [ ] Redis enabled (`REDIS_ENABLED=True`)
- [ ] Prometheus enabled (`PROMETHEUS_ENABLED=True`)

### Deployment
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Gunicorn configured with appropriate workers
- [ ] Worker count = (2 × CPU cores) + 1
- [ ] Health check endpoint tested (`/health`)
- [ ] API documentation accessible (`/docs`)
- [ ] Metrics endpoint accessible (`/metrics`)

### Testing
- [ ] All tests passing (`make test`)
- [ ] Integration tests run against staging
- [ ] Load testing completed
- [ ] Error handling verified

---

## 🖥️ WEB DASHBOARD

### Configuration
- [ ] `.env` file configured in `webdashboard/`
- [ ] `APP_ENV=production`
- [ ] `APP_DEBUG=false`
- [ ] `APP_KEY` generated (`php artisan key:generate`)
- [ ] Database connection configured
- [ ] API_BASE_URL points to backend
- [ ] API_KEY matches backend

### Deployment
- [ ] Composer dependencies installed (`composer install --no-dev`)
- [ ] NPM dependencies installed (`npm install`)
- [ ] Assets built (`npm run build`)
- [ ] Migrations run (`php artisan migrate`)
- [ ] Cache cleared (`php artisan cache:clear`)
- [ ] Config cached (`php artisan config:cache`)
- [ ] Routes cached (`php artisan route:cache`)
- [ ] Views cached (`php artisan view:cache`)

### Web Server
- [ ] Nginx/Apache configured
- [ ] Document root points to `webdashboard/public/`
- [ ] PHP-FPM configured
- [ ] File permissions set correctly
- [ ] Storage directory writable
- [ ] Log directory writable

---

## 🔌 BROWSER EXTENSION

### Configuration
- [ ] API endpoint updated to production URL
- [ ] Version number incremented in `manifest.json`
- [ ] Extension packaged (`./scripts/package-extension.sh`)
- [ ] Icons and assets included
- [ ] Permissions justified

### Testing
- [ ] Extension loaded in browser
- [ ] API connection verified
- [ ] Comment detection tested on:
  - [ ] Facebook
  - [ ] YouTube
  - [ ] Twitter
- [ ] Error handling tested
- [ ] Offline mode tested
- [ ] Retry logic verified

### Publishing
- [ ] Chrome Web Store listing prepared
- [ ] Screenshots captured (1280×800 or 640×400)
- [ ] Description written
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Support email configured
- [ ] Extension submitted for review

---

## 🗄️ REDIS

### Configuration
- [ ] Redis server installed and running
- [ ] Password configured
- [ ] Port configured (default: 6379)
- [ ] Max memory policy set (`maxmemory-policy allkeys-lru`)
- [ ] Persistence configured (RDB or AOF)
- [ ] Backup strategy defined

### Testing
- [ ] Connection test: `redis-cli ping`
- [ ] Password test: `redis-cli -a <password> ping`
- [ ] Cache operations verified
- [ ] Rate limiting tested

---

## 📊 MONITORING

### Prometheus
- [ ] Prometheus enabled in backend
- [ ] Metrics endpoint accessible (`/metrics`)
- [ ] Prometheus server configured (optional)
- [ ] Scrape interval configured
- [ ] Alert rules defined (optional)

### Grafana (Optional)
- [ ] Grafana installed and configured
- [ ] Data source added (Prometheus)
- [ ] Dashboards imported
- [ ] Alerts configured
- [ ] Notification channels set up

### Logging
- [ ] Log rotation configured
- [ ] Log aggregation set up (optional)
- [ ] Error tracking enabled
- [ ] Log retention policy defined

### Health Checks
- [ ] Backend health check: `curl http://localhost:7860/health`
- [ ] Dashboard health check: `curl http://localhost:8080`
- [ ] Redis health check: `redis-cli ping`
- [ ] Database health check: connection test

---

## 🐳 DOCKER (if using)

### Configuration
- [ ] `docker-compose.yml` configured
- [ ] Environment variables set
- [ ] Volumes configured for persistence
- [ ] Ports properly mapped
- [ ] Networks configured

### Deployment
- [ ] Images built: `docker-compose build`
- [ ] Containers started: `docker-compose up -d`
- [ ] Health checks passing
- [ ] Logs reviewed: `docker-compose logs`
- [ ] Resource limits set

### Registry (if applicable)
- [ ] Images tagged properly
- [ ] Images pushed to registry
- [ ] Registry authentication configured

---

## 🔄 CI/CD

### GitHub Actions
- [ ] Workflows configured in `.github/workflows/`
- [ ] Secrets set in GitHub repository:
  - [ ] `SECRET_KEY`
  - [ ] `EXTENSION_API_KEY`
  - [ ] `DOCKERHUB_USERNAME`
  - [ ] `DOCKERHUB_TOKEN`
  - [ ] `DEPLOY_KEY` (if auto-deploying)
- [ ] Test workflow running
- [ ] Lint workflow running
- [ ] Docker workflow running
- [ ] Deploy workflow running (on tags)

### Testing
- [ ] Tests run automatically on push
- [ ] Tests pass before merge
- [ ] Coverage reporting enabled

---

## 📈 PERFORMANCE

### Backend
- [ ] Model preloading enabled
- [ ] Redis caching enabled
- [ ] Connection pooling configured
- [ ] Worker count optimized
- [ ] Response time < 200ms (cached)
- [ ] Response time < 1s (uncached)

### Database
- [ ] Indexes applied
- [ ] Query performance verified
- [ ] Connection pooling enabled
- [ ] Slow query log reviewed

### Extension
- [ ] Batch processing enabled
- [ ] Caching implemented
- [ ] Retry logic tested
- [ ] Error handling robust

---

## 🔒 BACKUP & RECOVERY

### Database Backup
- [ ] Automated backups configured
- [ ] Backup schedule defined (daily recommended)
- [ ] Backup retention policy set
- [ ] Backup restoration tested
- [ ] Off-site backup configured

### Redis Backup
- [ ] Persistence enabled (RDB or AOF)
- [ ] Backup schedule defined
- [ ] Restoration tested

### Application Backup
- [ ] Configuration files backed up
- [ ] Environment variables documented
- [ ] Deployment scripts backed up

### Disaster Recovery Plan
- [ ] Recovery procedures documented
- [ ] RTO (Recovery Time Objective) defined
- [ ] RPO (Recovery Point Objective) defined
- [ ] Recovery test scheduled

---

## 📝 DOCUMENTATION

### Code Documentation
- [ ] API documentation up to date
- [ ] Code comments adequate
- [ ] Docstrings complete
- [ ] README.md updated

### Operational Documentation
- [ ] Deployment guide complete
- [ ] Troubleshooting guide available
- [ ] Monitoring guide available
- [ ] Backup/restore procedures documented

### User Documentation
- [ ] Extension user guide
- [ ] Dashboard user guide
- [ ] FAQ prepared
- [ ] Support contact info provided

---

## 🧪 TESTING

### Unit Tests
- [ ] All unit tests passing
- [ ] Coverage > 80%
- [ ] New features tested

### Integration Tests
- [ ] API endpoint tests passing
- [ ] Database integration tested
- [ ] Redis integration tested
- [ ] Extension integration tested

### Performance Tests
- [ ] Load testing completed
- [ ] Stress testing completed
- [ ] Concurrency testing completed
- [ ] Results documented

### Security Tests
- [ ] Authentication tested
- [ ] Authorization tested
- [ ] Input validation tested
- [ ] SQL injection prevention tested
- [ ] XSS prevention tested

---

## 📊 POST-DEPLOYMENT

### Monitoring (First 24 Hours)
- [ ] Error rates monitored
- [ ] Response times monitored
- [ ] CPU/Memory usage monitored
- [ ] Database performance monitored
- [ ] Redis performance monitored
- [ ] User activity monitored

### Verification
- [ ] All services running
- [ ] Health checks passing
- [ ] Logs reviewed
- [ ] Metrics collected
- [ ] Users can access system
- [ ] Extension working

### Communication
- [ ] Team notified of deployment
- [ ] Users notified (if applicable)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

---

## 🚨 ROLLBACK PLAN

### Preparation
- [ ] Previous version tagged in Git
- [ ] Database backup before migration
- [ ] Rollback procedure documented
- [ ] Rollback tested in staging

### If Rollback Needed
```bash
# 1. Stop services
docker-compose down
# or
make stop

# 2. Restore database
psql -U user -d toxic_detector < backup.sql

# 3. Checkout previous version
git checkout v0.9.0

# 4. Restart services
docker-compose up -d
# or
make start

# 5. Verify rollback
curl http://localhost:7860/health
```

---

## ✅ FINAL SIGN-OFF

### Pre-Production
- [ ] All critical items checked
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Team review completed
- [ ] Stakeholder approval obtained

### Production Deployment
- [ ] Deployment window scheduled
- [ ] Team notified
- [ ] Monitoring team on standby
- [ ] Support team briefed

### Post-Deployment
- [ ] Deployment successful
- [ ] Health checks passing
- [ ] Users notified
- [ ] Monitoring confirmed
- [ ] Documentation updated
- [ ] Post-mortem scheduled (if needed)

---

## 📞 CONTACTS

### Technical Contacts
- **DevOps Lead**: [email]
- **Backend Lead**: [email]
- **Frontend Lead**: [email]
- **On-Call**: [phone]

### Business Contacts
- **Product Manager**: [email]
- **Stakeholder**: [email]

### External Services
- **Hosting Provider**: [contact]
- **DNS Provider**: [contact]
- **SSL Certificate Provider**: [contact]

---

## 📋 CHECKLIST SUMMARY

**Total Items**: ~150  
**Critical Items**: ~50  
**Recommended Items**: ~100  

### Status
- [ ] All critical items complete
- [ ] All recommended items reviewed
- [ ] Ready for production deployment

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Approved By**: _______________  
**Version**: 1.0.0

---

*Checklist Version: 1.0.0*  
*Last Updated: 2025-10-19*

