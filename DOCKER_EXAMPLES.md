# Docker Quick Start Examples

This file contains practical examples for using Docker with Project Shri Sudarshan.

## Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   # Edit .env and add your actual API keys
   ```

2. **Create data directory:**
   ```bash
   mkdir -p data/chroma_db data/logs
   ```

## Basic Usage

### Build the Image
```bash
docker build -t shri-sudarshan:latest .
```

### Run Simple Analysis
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:latest --symbol AAPL
```

### Run with Docker Compose
```bash
# One-time analysis
docker compose run --rm shri-sudarshan --symbol AAPL

# With custom parameters
docker compose run --rm shri-sudarshan \
  --symbol TSLA \
  --start_date 2023-01-01 \
  --end_date 2023-12-31 \
  --log-level DEBUG
```

## Docker Compose Examples

### Start All Services (Background)
```bash
docker compose up -d
```

### Run with PostgreSQL and Redis
```bash
# Update .env to use PostgreSQL:
# DATABASE_URL=postgresql://shri_user:changeme@postgres:5432/shri_sudarshan

docker compose --profile full up -d
docker compose run --rm shri-sudarshan --symbol AAPL
```

### View Logs
```bash
docker compose logs -f shri-sudarshan
```

### Stop All Services
```bash
docker compose down
```

## Development Mode

### Run with Source Code Mounted
```bash
docker compose up -d  # Source is already mounted in docker-compose.yml
```

### Run Tests in Container
```bash
docker compose run --rm --entrypoint pytest shri-sudarshan
```

### Open Interactive Shell
```bash
docker compose run --rm --entrypoint /bin/bash shri-sudarshan
```

## GPU Support

### Build GPU Image
```bash
docker build -f Dockerfile.gpu -t shri-sudarshan:gpu .
```

### Run with GPU
```bash
docker run --gpus all --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:gpu --symbol AAPL
```

## Production Deployment

### Build Production Image
```bash
docker build -t shri-sudarshan:v0.1.0 .
docker tag shri-sudarshan:v0.1.0 your-registry/shri-sudarshan:v0.1.0
docker push your-registry/shri-sudarshan:v0.1.0
```

### Run in Production
```bash
# Edit docker-compose.yml to remove source mount
# Set DATABASE_URL to PostgreSQL
# Enable restart policies

docker compose --profile production up -d
```

## Troubleshooting

### Check Container Health
```bash
docker ps
docker logs shri-sudarshan-app
```

### Verify Environment Variables
```bash
docker exec shri-sudarshan-app env | grep API_KEY
```

### Clean Up
```bash
# Remove all containers and volumes
docker compose down -v

# Remove images
docker rmi shri-sudarshan:latest

# Clean up build cache
docker builder prune -a
```

## Complete Workflow Example

```bash
# 1. Setup
git clone https://github.com/s-p-c-git/ShriSudarshan.git
cd ShriSudarshan
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Build
docker build -t shri-sudarshan:latest .

# 3. Run analysis
docker compose run --rm shri-sudarshan --symbol AAPL

# 4. Check results in data directory
ls -la data/

# 5. Run with different parameters
docker compose run --rm shri-sudarshan \
  --symbol TSLA \
  --start_date 2024-01-01 \
  --end_date 2024-01-31 \
  --log-level INFO
```

## Notes

- Always use paper trading mode (default) when testing
- Ensure your .env file has valid API keys
- Data persists in the ./data directory
- For GPU support, use Dockerfile.gpu and --gpus flag
- See DOCKER.md for comprehensive documentation
