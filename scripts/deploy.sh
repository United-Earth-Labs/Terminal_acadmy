#!/bin/bash
# Terminal Academy - Deployment Script

set -e

echo "🚀 Terminal Academy Deployment Script"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required files
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: .env.production not found${NC}"
    echo "Copy .env.production.example to .env.production and configure it"
    exit 1
fi

# Check for SSL certificates
if [ ! -f "nginx/certs/fullchain.pem" ] || [ ! -f "nginx/certs/privkey.pem" ]; then
    echo -e "${YELLOW}Warning: SSL certificates not found in nginx/certs/${NC}"
    echo "You can generate self-signed certs with:"
    echo "  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\"
    echo "    -keyout nginx/certs/privkey.pem -out nginx/certs/fullchain.pem"
    echo ""
fi

# Build and start containers
echo -e "${GREEN}Building Docker images...${NC}"
docker-compose build

echo -e "${GREEN}Starting containers...${NC}"
docker-compose up -d

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database...${NC}"
sleep 10

# Run migrations
echo -e "${GREEN}Running database migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput

# Create superuser prompt
echo ""
echo -e "${YELLOW}Would you like to create a superuser? (y/n)${NC}"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    docker-compose exec web python manage.py createsuperuser
fi

# Show status
echo ""
echo -e "${GREEN}======================================"
echo "Deployment complete!"
echo "======================================"
echo ""
docker-compose ps
echo ""
echo "Access the application at: https://localhost"
echo "Admin panel: https://localhost/admin/"
