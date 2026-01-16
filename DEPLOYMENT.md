# Deployment Guide

Complete guide for deploying the Game Review App to Digital Ocean with CI/CD.

## Prerequisites

1. **Digital Ocean Account**
   - Create a Droplet (Ubuntu 22.04 LTS recommended)
   - Minimum: 2 GB RAM, 1 vCPU
   - Recommended: 4 GB RAM, 2 vCPUs

2. **Domain Name**
   - Point A record to your droplet's IP
   - Wait for DNS propagation (can take up to 24 hours)

3. **GitHub Repository**
   - Push your code to GitHub
   - Enable GitHub Packages (free for public repos)

4. **API Keys**
   - IGDB (Twitch Developer Console)
   - RAWG API Key
   - Steam API Key
   - PlayStation Developer Account (optional)
   - Xbox Developer Account (optional)

## Step 1: Initial Droplet Setup

### SSH into your droplet:
```bash
ssh root@your-droplet-ip
```

### Download and run setup script:
```bash
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/GameReviewAppTest/main/scripts/setup-droplet.sh
chmod +x setup-droplet.sh
./setup-droplet.sh
```

## Step 2: Configure Environment

### Create environment file:
```bash
cd /opt/game-review-app
cp .env.template .env
nano .env
```

Fill in all required values:
- Generate SECRET_KEY: `openssl rand -hex 32`
- Add your domain name
- Add all API keys

### Set proper permissions:
```bash
chmod 600 .env
chown deploy:deploy .env
```

## Step 3: Set Up Deploy SSH Key

### Generate deployment key (on your local machine):
```bash
ssh-keygen -t ed25519 -C "deploy@game-review-app" -f ~/.ssh/game-review-deploy
```

### Add public key to droplet:
```bash
# On your droplet as root
cat >> /home/deploy/.ssh/authorized_keys << EOF
[paste your public key here]
EOF

chmod 600 /home/deploy/.ssh/authorized_keys
chown deploy:deploy /home/deploy/.ssh/authorized_keys
```

## Step 4: Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add the following secrets:

### Required Secrets:
- `DROPLET_IP`: Your droplet's IP address
- `DROPLET_USER`: `deploy`
- `SSH_PRIVATE_KEY`: Contents of `~/.ssh/game-review-deploy` (private key)
- `DOMAIN_NAME`: `yourdomain.com`
- `VITE_API_URL`: `https://yourdomain.com/api/v1`

### Environment Variables (from .env):
- `SECRET_KEY`
- `CORS_ORIGINS`
- `IGDB_CLIENT_ID`
- `IGDB_CLIENT_SECRET`
- `RAWG_API_KEY`
- `STEAM_API_KEY`
- `PSN_CLIENT_ID` (optional)
- `PSN_CLIENT_SECRET` (optional)
- `XBOX_CLIENT_ID` (optional)
- `XBOX_CLIENT_SECRET` (optional)
- `ADMIN_EMAIL`

## Step 5: Clone Repository

### On your droplet:
```bash
su - deploy
cd /opt/game-review-app
git clone https://github.com/YOUR_USERNAME/GameReviewAppTest.git .
```

### Set up GitHub Container Registry authentication:
```bash
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

## Step 6: SSL Certificate Setup

### Run certbot to get SSL certificate:
```bash
docker compose -f docker-compose.prod.yml run --rm certbot
```

### Set up auto-renewal:
```bash
# Create renewal script
cat > /opt/game-review-app/renew-cert.sh << 'EOF'
#!/bin/bash
docker compose -f /opt/game-review-app/docker-compose.prod.yml run --rm certbot renew
docker compose -f /opt/game-review-app/docker-compose.prod.yml exec nginx nginx -s reload
EOF

chmod +x /opt/game-review-app/renew-cert.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 0 * * 0 /opt/game-review-app/renew-cert.sh") | crontab -
```

## Step 7: Deploy Application

### Manual first deployment:
```bash
cd /opt/game-review-app
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Check logs:
```bash
docker compose -f docker-compose.prod.yml logs -f
```

### Verify deployment:
```bash
curl https://yourdomain.com/api/v1/health
```

## Step 8: Automated Deployments

Once configured, deployments are automatic:

1. **Push to main branch:**
   ```bash
   git push origin main
   ```

2. **GitHub Actions will:**
   - Build Docker images
   - Push to GitHub Container Registry
   - SSH into droplet
   - Pull latest images
   - Restart containers
   - Run health checks

3. **Monitor deployment:**
   - Go to GitHub → Actions tab
   - Watch the deployment progress

## Maintenance Commands

### View logs:
```bash
docker compose -f docker-compose.prod.yml logs -f [service-name]
```

### Restart services:
```bash
docker compose -f docker-compose.prod.yml restart
```

### Update containers:
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Database backup:
```bash
docker compose -f docker-compose.prod.yml exec backend \
  cp /data/game_review.db /data/backup-$(date +%Y%m%d-%H%M%S).db
```

### View running containers:
```bash
docker ps
```

### Check resource usage:
```bash
docker stats
```

## Troubleshooting

### Container won't start:
```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
```

### SSL certificate issues:
```bash
# Check certificate
docker compose -f docker-compose.prod.yml run --rm certbot certificates

# Renew manually
docker compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
```

### Can't connect to database:
```bash
# Check if backend has write permissions
docker compose -f docker-compose.prod.yml exec backend ls -la /data
```

### High memory usage:
```bash
# Reduce backend workers in docker-compose.prod.yml
# Change --workers from 4 to 2
```

## Security Best Practices

1. **Keep system updated:**
   ```bash
   apt-get update && apt-get upgrade -y
   ```

2. **Monitor failed login attempts:**
   ```bash
   fail2ban-client status sshd
   ```

3. **Regular backups:**
   - Set up automated database backups
   - Store backups in Digital Ocean Spaces or S3

4. **Monitor logs:**
   ```bash
   tail -f /var/log/nginx/access.log
   tail -f /var/log/nginx/error.log
   ```

## Scaling

### Vertical Scaling (Resize Droplet):
1. Power off droplet
2. Resize in Digital Ocean dashboard
3. Power on and verify

### Horizontal Scaling (Multiple Droplets):
1. Set up Digital Ocean Load Balancer
2. Deploy to multiple droplets
3. Use managed database (PostgreSQL) instead of SQLite
4. Configure session storage (Redis)

## Cost Optimization

- **Basic**: $12/month (2GB RAM droplet)
- **Recommended**: $24/month (4GB RAM droplet)
- **Additional costs**: Domain ($12/year), Spaces backup ($5/month)

## Support

For issues:
1. Check GitHub Actions logs
2. Check droplet logs
3. Review nginx error logs
4. Verify environment variables
5. Check firewall rules
