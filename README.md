# Video Processing and Analysis Backend

A scalable backend system for video processing and frame analysis using FastAPI, OpenCV, and Streamlit.

## Features

- Video upload and YouTube video download capabilities
- Frame extraction every 1 - 20 seconds using OpenCV
- Clean architecture with Controller-Service-Model pattern
- FastAPI-based RESTful API
- Streamlit dashboard for user interaction
- Docker support for easy deployment

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── controllers/
│   │   ├── dependencies/
│   │   └── routes/
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── domain/
│   │   └── schemas/
│   ├── services/
│   │   ├── video/
│   │   └── frame/
│   └── utils/
├── frontend/
│   └── streamlit_app.py
├── tests/
├── storage/
│   ├── videos/
│   └── frames/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your environment variables
5. Run the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Run the Streamlit frontend (in a new terminal):
   ```bash
   # Make sure you're in the project root and your virtual environment is activated
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```
   The Streamlit dashboard will be available at: `http://localhost:8501`

Note: Make sure both the FastAPI backend (port 8000) and Streamlit frontend (port 8501) are running simultaneously for the application to work properly.

## Docker Deployment

Build and run using Docker Compose:
```bash
docker-compose up --build
```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests using pytest:
```bash
pytest
```

## AWS Deployment Guide

### Prerequisites
1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Docker installed locally
4. ECR (Elastic Container Registry) repository created

### Step 1: Create ECR Repositories
```bash
# Create repositories for both services
aws ecr create-repository --repository-name chicken-behavior-api
aws ecr create-repository --repository-name chicken-behavior-frontend
```

### Step 2: Push Docker Images to ECR
```bash
# Login to ECR
aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com

# Build and tag images
docker build -t chicken-behavior-api -f Dockerfile --target api .
docker build -t chicken-behavior-frontend -f Dockerfile --target frontend .

# Tag images for ECR
docker tag chicken-behavior-api:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/chicken-behavior-api:latest
docker tag chicken-behavior-frontend:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/chicken-behavior-frontend:latest

# Push images
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/chicken-behavior-api:latest
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/chicken-behavior-frontend:latest
```

### Step 3: Set Up ECS (Elastic Container Service)

1. Create an ECS cluster
2. Create Task Definitions for both services
3. Configure services with Application Load Balancer

#### Storage Configuration
- Create an EFS (Elastic File System) for persistent storage
- Mount the EFS volume in both task definitions to `/app/storage`

### Step 4: Environment Variables
Set up the following in ECS Task Definitions:
- `OPENAI_API_KEY`
- `API_URL` (for frontend service)
- Other environment variables from `.env`

### Step 5: Security Groups
Configure security groups to allow:
- Frontend service (8501)
- API service (8000)
- EFS mount points
- Load balancer rules

### Step 6: Load Balancer Setup
1. Create Application Load Balancer
2. Configure listeners:
   - Port 8000 -> API service
   - Port 8501 -> Frontend service
3. Set up health checks:
   - API: `/health`
   - Frontend: `/`

### Step 7: DNS and HTTPS (Optional)
1. Create Route53 records
2. Set up ACM certificate
3. Configure HTTPS listeners

### Infrastructure as Code (Optional)
Consider using:
- AWS CDK
- Terraform
- AWS CloudFormation

Example Terraform configuration available in `deployment/terraform/`

## Monitoring and Logging

### CloudWatch Setup
1. Configure CloudWatch agent in ECS tasks
2. Set up log groups for both services
3. Create dashboards for monitoring:
   - CPU/Memory usage
   - Request counts
   - Error rates
   - Processing times

### Alerts
Set up CloudWatch Alarms for:
- High CPU/Memory usage
- Error rate spikes
- Service health check failures

## Scaling Configuration

### Auto Scaling
Configure ECS Service Auto Scaling based on:
- CPU utilization
- Memory utilization
- Request count

### Cost Optimization
- Use Spot Instances for processing tasks
- Configure scaling policies
- Set up AWS Cost Explorer alerts

## Maintenance

### Backup Strategy
1. EFS backups
2. Database backups (if added later)
3. Configuration backups

### Updates
1. CI/CD pipeline setup
2. Blue-green deployment strategy
3. Rollback procedures

## EC2 Deployment Guide

### Prerequisites
1. AWS Account with EC2 access
2. SSH key pair for EC2 instance
3. Git installed locally
4. Basic knowledge of Linux commands

### Step 1: Launch EC2 Instance
1. Launch an EC2 instance with the following specifications:
   - Amazon Linux 2023 or Ubuntu Server 22.04
   - t2.large or better (for video processing)
   - At least 30GB storage
   - Security group with ports:
     - 22 (SSH)
     - 8000 (API)
     - 8501 (Streamlit)

### Step 2: Install Dependencies
```bash
# Connect to your EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Update system packages
sudo yum update -y  # For Amazon Linux
# OR
sudo apt update && sudo apt upgrade -y  # For Ubuntu

# Install Docker
sudo yum install docker -y  # For Amazon Linux
# OR
sudo apt install docker.io -y  # For Ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and log back in for changes to take effect
```

### Step 3: Clone and Configure Project
```bash
# Clone repository
git clone https://github.com/yourusername/chicken-behavior.git
cd chicken-behavior

# Create and configure .env file
cp .env.example .env
nano .env  # Add your environment variables
```

### Step 4: Start Application
```bash
# Build and start containers
docker-compose up --build -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Setup Automatic Updates (Optional)
Create a deployment script `deploy.sh`:
```bash
#!/bin/bash
cd /path/to/chicken-behavior
git pull
docker-compose down
docker-compose up --build -d
```

Make it executable:
```bash
chmod +x deploy.sh
```

### Step 6: Setup SSL with Nginx (Recommended)
```bash
# Install Nginx
sudo yum install nginx -y  # For Amazon Linux
# OR
sudo apt install nginx -y  # For Ubuntu

# Create Nginx configuration
sudo nano /etc/nginx/conf.d/chicken-behavior.conf
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Maintenance

#### Updating the Application
```bash
# Pull latest changes
git pull

# Rebuild and restart containers
docker-compose down
docker-compose up --build -d
```

#### Backup Data
```bash
# Backup storage directory
sudo tar -czf backup-$(date +%Y%m%d).tar.gz storage/

# Copy backup to secure location
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

#### Monitoring
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Monitor system resources
htop  # Install with: sudo yum install htop
```

#### Troubleshooting
1. If containers fail to start:
   ```bash
   # Check logs
   docker-compose logs
   
   # Verify disk space
   df -h
   
   # Check Docker status
   sudo systemctl status docker
   ```

2. If application is slow:
   ```bash
   # Monitor resource usage
   docker stats
   
   # Check system load
   uptime
   ```

## License

MIT License 