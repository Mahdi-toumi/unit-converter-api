# 🐳 Docker Guide - Unit Converter API

This document explains how to build, run, and deploy the Unit Converter API using Docker.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Building the Image](#building-the-image)
- [Running the Container](#running-the-container)
- [Using Docker Compose](#using-docker-compose)
- [Docker Hub](#docker-hub)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- Docker Hub account (for pushing images)

### Check versions
```bash
docker --version
docker-compose --version
```

---

## 🏗️ Building the Image

### Local build
```bash
# Build the image
docker build -t unit-converter-api:latest .

# Check the image
docker images unit-converter-api
```

### Build with specific tag
```bash
docker build -t unit-converter-api:1.0.0 .
```

### Build arguments (optional)
```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t unit-converter-api:latest .
```

---

## 🚀 Running the Container

### Basic run
```bash
docker run -d \
  --name unit-converter \
  -p 8000:8000 \
  unit-converter-api:latest
```

### Run with environment variables
```bash
docker run -d \
  --name unit-converter \
  -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  -e API_TITLE="My Converter API" \
  unit-converter-api:latest
```

### Run from Docker Hub
```bash
docker run -d \
  --name unit-converter \
  -p 8000:8000 \
  votre-username/unit-converter-api:latest
```

### Check logs
```bash
# View logs
docker logs unit-converter

# Follow logs
docker logs -f unit-converter

# Last 100 lines
docker logs --tail 100 unit-converter
```

### Stop and remove
```bash
# Stop
docker stop unit-converter

# Remove
docker rm unit-converter

# Stop and remove in one command
docker rm -f unit-converter
```

---

## 🎼 Using Docker Compose

### Start all services
```bash
# Build and start
docker-compose up --build -d

# Start without building
docker-compose up -d
```

### View services
```bash
# List containers
docker-compose ps

# View logs
docker-compose logs

# Follow logs
docker-compose logs -f api
```

### Stop services
```bash
# Stop
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers and volumes
docker-compose down -v
```

### Scale services (if needed)
```bash
# Run 3 instances of API
docker-compose up -d --scale api=3
```

---

## 🌐 Docker Hub

### Login
```bash
docker login
```

### Tag for Docker Hub
```bash
# Tag with username
docker tag unit-converter-api:latest votre-username/unit-converter-api:latest
docker tag unit-converter-api:latest votre-username/unit-converter-api:1.0.0
```

### Push to Docker Hub
```bash
# Push latest
docker push votre-username/unit-converter-api:latest

# Push specific version
docker push votre-username/unit-converter-api:1.0.0
```

### Pull from Docker Hub
```bash
docker pull votre-username/unit-converter-api:latest
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_TITLE` | Unit Converter API | API title in documentation |
| `API_VERSION` | 1.0.0 | API version |
| `API_DESCRIPTION` | REST API for unit conversions | API description |
| `HOST` | 0.0.0.0 | Bind address |
| `PORT` | 8000 | Server port |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CURRENCY_API_URL` | https://api.exchangerate-api.com/v4/latest | Currency API endpoint |
| `CURRENCY_API_TIMEOUT` | 5 | Currency API timeout in seconds |

### Example with custom config
```bash
docker run -d \
  -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  -e CURRENCY_API_TIMEOUT=10 \
  votre-username/unit-converter-api:latest
```

### Using .env file

Create `.env`:
```env
LOG_LEVEL=DEBUG
API_TITLE=Custom API
```

Run with:
```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  votre-username/unit-converter-api:latest
```

---

## 🔍 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs unit-converter

# Inspect container
docker inspect unit-converter

# Check exit code
docker ps -a
```

### Port already in use
```bash
# Find process using port 8000
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000

# Use different port
docker run -d -p 8001:8000 unit-converter-api:latest
```

### Health check failing
```bash
# Check health status
docker inspect unit-converter --format='{{.State.Health.Status}}'

# View health check logs
docker inspect unit-converter --format='{{json .State.Health}}' | python -m json.tool

# Manual health check
curl http://localhost:8000/health
```

### Image too large
```bash
# Check image size
docker images unit-converter-api

# Analyze layers
docker history unit-converter-api:latest

# Use dive for detailed analysis
dive unit-converter-api:latest
```

### Permission denied errors

The container runs as non-root user (UID 1000). If you encounter permission issues:
```bash
# Run as root (not recommended for production)
docker run -d --user root -p 8000:8000 unit-converter-api:latest
```

### Can't connect to Docker daemon
```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or start Docker service
sudo systemctl start docker
```

---

## 🧪 Testing the Container

### Quick test
```bash
# Health check
curl http://localhost:8000/health

# API root
curl http://localhost:8000/

# Test conversion
curl -X POST http://localhost:8000/convert/length \
  -H "Content-Type: application/json" \
  -d '{"value": 100, "from_unit": "meter", "to_unit": "foot"}'

# Check metrics
curl http://localhost:8000/metrics

# View documentation
open http://localhost:8000/docs
```

### Performance test
```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health
```

---

## 📊 Monitoring with Prometheus

When using docker-compose, Prometheus is available at http://localhost:9090

### Useful queries
```promql
# Request rate
rate(api_requests_total[1m])

# 95th percentile latency
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Error rate
sum(rate(api_requests_total{status="error"}[1m])) / sum(rate(api_requests_total[1m]))
```

---

## 🔒 Security Best Practices

✅ **Implemented in this image:**
- Non-root user (UID 1000)
- Minimal base image (python:slim)
- No unnecessary packages
- Multi-stage build (no build tools in final image)
- Health checks
- Read-only filesystem where possible

⚠️ **Additional recommendations for production:**
- Use specific version tags (not `latest`)
- Scan images for vulnerabilities: `docker scan unit-converter-api:latest`
- Use secrets management for sensitive data
- Implement network policies
- Use resource limits

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
- [Prometheus Docker Guide](https://prometheus.io/docs/prometheus/latest/installation/)

---

## 🆘 Support

For issues or questions:
- GitHub Issues: https://github.com/Mahdi-toumi/unit-converter-api/issues
- Documentation: See README.md