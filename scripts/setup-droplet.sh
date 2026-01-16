#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Game Review App - Droplet Setup ===${NC}\n"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}" 
   exit 1
fi

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install Docker
echo -e "${YELLOW}Installing Docker...${NC}"
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Install Git
echo -e "${YELLOW}Installing Git...${NC}"
apt-get install -y git

# Create app directory
echo -e "${YELLOW}Setting up application directory...${NC}"
mkdir -p /opt/game-review-app
cd /opt/game-review-app

# Create deploy user
echo -e "${YELLOW}Creating deploy user...${NC}"
useradd -m -s /bin/bash deploy || true
usermod -aG docker deploy

# Set up SSH for deploy user
mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chown -R deploy:deploy /home/deploy/.ssh

# Install fail2ban for security
echo -e "${YELLOW}Installing fail2ban...${NC}"
apt-get install -y fail2ban
systemctl start fail2ban
systemctl enable fail2ban

# Configure firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Create .env file template
echo -e "${YELLOW}Creating environment file template...${NC}"
cat > /opt/game-review-app/.env.template << 'EOF'
# GitHub Container Registry
GITHUB_REPOSITORY=your-username/GameReviewAppTest

# Domain
DOMAIN_NAME=yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

# Backend
SECRET_KEY=generate-a-secure-secret-key-here
CORS_ORIGINS=https://yourdomain.com

# External APIs
IGDB_CLIENT_ID=your-igdb-client-id
IGDB_CLIENT_SECRET=your-igdb-client-secret
RAWG_API_KEY=your-rawg-api-key
STEAM_API_KEY=your-steam-api-key
PSN_CLIENT_ID=your-psn-client-id
PSN_CLIENT_SECRET=your-psn-client-secret
XBOX_CLIENT_ID=your-xbox-client-id
XBOX_CLIENT_SECRET=your-xbox-client-secret
EOF

# Set permissions
chown -R deploy:deploy /opt/game-review-app

echo -e "${GREEN}\n=== Setup Complete! ===${NC}"
echo -e "\nNext steps:"
echo -e "1. Copy your .env.template to .env and fill in the values"
echo -e "2. Add your deploy SSH key to /home/deploy/.ssh/authorized_keys"
echo -e "3. Clone your repository to /opt/game-review-app"
echo -e "4. Set up GitHub Secrets for CI/CD:"
echo -e "   - DROPLET_IP: Your droplet's IP address"
echo -e "   - DROPLET_USER: deploy"
echo -e "   - SSH_PRIVATE_KEY: Your deployment SSH private key"
echo -e "   - DOMAIN_NAME: yourdomain.com"
echo -e "   - VITE_API_URL: https://yourdomain.com/api/v1"
echo -e "   - All environment variables from .env"
echo -e "\n5. Point your domain DNS A record to this droplet's IP"
echo -e "6. Push to main branch to trigger deployment"
