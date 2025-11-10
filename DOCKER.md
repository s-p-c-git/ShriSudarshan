# Docker Documentation for Project Shri Sudarshan

This guide provides comprehensive instructions for running Project Shri Sudarshan in Docker containers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Building the Image](#building-the-image)
- [Running the Container](#running-the-container)
- [Environment Configuration](#environment-configuration)
- [Data Persistence](#data-persistence)
- [Docker Compose Usage](#docker-compose-usage)
- [GPU Support](#gpu-support)
- [CLI Usage Examples](#cli-usage-examples)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher (optional, but recommended)
- **API Keys**: OpenAI or Anthropic API key
- **Hardware**: Minimum 4GB RAM, 2 CPU cores recommended
- **GPU** (optional): For FinBERT/FinGPT models with CUDA support

### Installing Docker

- **Linux**: Follow the [official Docker installation guide](https://docs.docker.com/engine/install/)
- **macOS**: Install [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

## Quick Start

### Option 1: Using Makefile (Recommended)

The easiest way to get started:

```bash
# 1. Clone and setup
git clone https://github.com/s-p-c-git/ShriSudarshan.git
cd ShriSudarshan
make setup

# 2. Edit .env and add your API keys
nano .env

# 3. Build and run
make build
make run SYMBOL=AAPL
```

See `make help` for all available commands.

### Option 2: Using Docker Compose

1. **Clone the repository**:
   ```bash
   git clone https://github.com/s-p-c-git/ShriSudarshan.git
   cd ShriSudarshan
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   nano .env
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker compose build
   docker compose run --rm shri-sudarshan --symbol AAPL
   ```

### Option 3: Using Docker directly

```bash
# Build the image
docker build -t shri-sudarshan:latest .

# Run analysis
docker run --rm --env-file .env -v $(pwd)/data:/app/data shri-sudarshan:latest --symbol AAPL
```

## Building the Image

### Basic Build

Build the Docker image using the provided Dockerfile:

```bash
docker build -t shri-sudarshan:latest .
```

### Build with Custom Tag

```bash
docker build -t shri-sudarshan:v0.1.0 .
```

### Build with Docker Compose

```bash
docker-compose build
```

### Verifying the Build

Check that the image was created successfully:

```bash
docker images | grep shri-sudarshan
```

## Running the Container

### Using Docker Run

**Basic usage**:
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:latest --symbol AAPL
```

**Interactive mode**:
```bash
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:latest --symbol TSLA --log-level DEBUG
```

**Background mode** (detached):
```bash
docker run -d \
  --name shri-analysis \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:latest --symbol AAPL
```

### Using Docker Compose

**Run analysis (one-time)**:
```bash
docker-compose run --rm shri-sudarshan --symbol AAPL
```

**Start services**:
```bash
docker-compose up -d
```

**View logs**:
```bash
docker-compose logs -f shri-sudarshan
```

**Stop services**:
```bash
docker-compose down
```

## Environment Configuration

### Using .env File

The easiest way to configure the application is using a `.env` file:

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your configuration:
   ```bash
   # Required: LLM Provider
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_actual_api_key_here
   
   # Optional: Data providers
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
   
   # Memory configuration
   CHROMA_PERSIST_DIRECTORY=./data/chroma_db
   DATABASE_URL=sqlite:///./data/episodic_memory.db
   ```

3. The `.env` file is automatically loaded by Docker Compose.

### Environment Variables

You can also pass environment variables directly:

```bash
docker run --rm \
  -e OPENAI_API_KEY=your_key \
  -e LLM_PROVIDER=openai \
  -e LOG_LEVEL=DEBUG \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:latest --symbol AAPL
```

### Required Environment Variables

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: Your LLM provider API key
- `LLM_PROVIDER`: Either "openai" or "anthropic"

### Optional Environment Variables

See `.env.example` for all available configuration options, including:
- Data provider API keys
- Memory configuration
- Risk management parameters
- Model selection
- Logging settings

## Data Persistence

### Volume Mounts

The application uses volumes to persist data between container runs:

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:latest --symbol AAPL
```

### Data Directory Structure

```
data/
├── chroma_db/              # ChromaDB vector database
├── episodic_memory.db      # SQLite database for trade history
└── logs/                   # Application logs
```

### Creating Data Directory

```bash
mkdir -p data/chroma_db data/logs
```

### Backing Up Data

```bash
# Backup all data
tar -czf shri-data-backup-$(date +%Y%m%d).tar.gz data/

# Backup only database
cp data/episodic_memory.db data/episodic_memory.db.backup
```

## Docker Compose Usage

### Basic Commands

**Start all services**:
```bash
docker-compose up
```

**Start in background**:
```bash
docker-compose up -d
```

**Run one-time analysis**:
```bash
docker-compose run --rm shri-sudarshan --symbol AAPL
```

**Stop all services**:
```bash
docker-compose down
```

**View logs**:
```bash
docker-compose logs -f
```

**Rebuild images**:
```bash
docker-compose build --no-cache
```

### Using Optional Services

The docker-compose.yml includes optional PostgreSQL and Redis services.

**Start with PostgreSQL** (for production episodic memory):
```bash
docker-compose --profile production up -d
```

**Start with all services** (PostgreSQL + Redis):
```bash
docker-compose --profile full up -d
```

**Configure PostgreSQL connection**:

Update your `.env` file:
```bash
DATABASE_URL=postgresql://shri_user:changeme@postgres:5432/shri_sudarshan
```

**Configure Redis connection**:

Update your `.env` file:
```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### Development Mode

For development with live code reloading, the source directory is mounted:

```bash
# docker-compose.yml already includes:
volumes:
  - ./src:/app/src
```

### Production Mode

For production, comment out the source mount in `docker-compose.yml`:

```yaml
volumes:
  # - ./src:/app/src  # Comment this out for production
  - ./data:/app/data
```

## GPU Support

To use GPU acceleration for FinBERT and FinGPT models:

### Prerequisites

1. Install [NVIDIA Docker runtime](https://github.com/NVIDIA/nvidia-docker)
2. Verify GPU access:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```

### GPU Dockerfile

Create a `Dockerfile.gpu`:

```dockerfile
# Use NVIDIA CUDA base image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Continue with standard Dockerfile instructions...
# (Copy the rest from the main Dockerfile)
```

### Build and Run with GPU

```bash
# Build GPU image
docker build -f Dockerfile.gpu -t shri-sudarshan:gpu .

# Run with GPU
docker run --gpus all --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:gpu --symbol AAPL
```

### Docker Compose with GPU

Add to `docker-compose.yml`:

```yaml
services:
  shri-sudarshan:
    # ... other config ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## CLI Usage Examples

All command-line arguments supported by `main.py` work with Docker.

### Basic Analysis

```bash
docker-compose run --rm shri-sudarshan --symbol AAPL
```

### Analysis with Date Range

```bash
docker-compose run --rm shri-sudarshan \
  --symbol AAPL \
  --start_date 2023-01-01 \
  --end_date 2023-12-31
```

### Paper Trading Mode (Default)

```bash
docker-compose run --rm shri-sudarshan \
  --symbol TSLA \
  --paper-trading
```

### Debug Mode

```bash
docker-compose run --rm shri-sudarshan \
  --symbol AAPL \
  --log-level DEBUG
```

### Live Trading Mode (Use with Caution!)

```bash
docker-compose run --rm shri-sudarshan \
  --symbol AAPL \
  --live-trading
```

### Get Help

```bash
docker-compose run --rm shri-sudarshan --help
```

### Override Entrypoint

For debugging or running other commands:

```bash
# Open shell in container
docker-compose run --rm --entrypoint /bin/bash shri-sudarshan

# Run tests
docker-compose run --rm --entrypoint pytest shri-sudarshan

# Run Python script
docker-compose run --rm --entrypoint python shri-sudarshan examples/simple_analysis.py
```

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error**: `OpenAI API key not configured`

**Solution**:
- Verify `.env` file exists and contains `OPENAI_API_KEY=your_actual_key`
- Ensure `.env` file is in the same directory as `docker-compose.yml`
- Check that the key is not wrapped in quotes

#### 2. Permission Denied on Data Directory

**Error**: `Permission denied: '/app/data'`

**Solution**:
```bash
# Fix permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

#### 3. Out of Memory

**Error**: Container crashes or system becomes unresponsive

**Solution**:
- Increase Docker memory limit in Docker Desktop settings
- Reduce resource limits in `docker-compose.yml`
- Use lighter models (gpt-4o-mini instead of gpt-4o)

#### 4. Port Already in Use

**Error**: `port is already allocated`

**Solution**:
- Change port mappings in `docker-compose.yml`
- Stop conflicting services
- Use different ports for PostgreSQL/Redis

#### 5. Image Build Fails

**Error**: `failed to solve with frontend dockerfile.v0`

**Solution**:
```bash
# Clear build cache
docker builder prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### 6. Module Not Found

**Error**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
- Verify all dependencies are in `requirements.txt`
- Rebuild the image: `docker-compose build --no-cache`
- Check that `PYTHONPATH` is set correctly in Dockerfile

#### 7. SSL Certificate Verification Failed During Build

**Error**: `[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain`

**Solution**:
This can occur in some CI/CD environments or corporate networks with SSL inspection. Try one of these approaches:

- **Option 1 - Use trusted certificates** (recommended for production):
  ```bash
  # Install certificates in the container
  RUN apt-get update && apt-get install -y ca-certificates
  RUN update-ca-certificates
  ```

- **Option 2 - Temporarily disable SSL verification** (development only):
  ```dockerfile
  # In Dockerfile, temporarily add:
  ENV PIP_TRUSTED_HOST=pypi.org pypi.python.org files.pythonhosted.org
  ```

- **Option 3 - Use a different network** or wait and retry if this is a transient issue

**Note**: The Dockerfile works correctly in normal environments. This is typically an environment-specific issue.

### Debugging Tips

**View container logs**:
```bash
docker-compose logs -f shri-sudarshan
```

**Inspect running container**:
```bash
docker exec -it shri-sudarshan-app /bin/bash
```

**Check environment variables**:
```bash
docker exec shri-sudarshan-app env | grep API_KEY
```

**Test API connectivity**:
```bash
docker exec shri-sudarshan-app python -c "from config import settings; print(settings.openai_api_key)"
```

**Run in interactive mode**:
```bash
docker run -it --rm --entrypoint /bin/bash \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:latest
```

## Production Deployment

### Best Practices

1. **Use specific image tags**:
   ```bash
   docker build -t shri-sudarshan:v0.1.0 .
   ```

2. **Remove development mounts**:
   Comment out source code volume in `docker-compose.yml`

3. **Use external databases**:
   Configure PostgreSQL instead of SQLite for episodic memory

4. **Set resource limits**:
   Adjust CPU and memory limits based on workload

5. **Enable restart policies**:
   ```yaml
   restart: unless-stopped
   ```

6. **Use secrets management**:
   Consider Docker secrets or external secret managers instead of `.env` files

7. **Monitor container health**:
   Set up monitoring and alerting for container metrics

### Security Considerations

1. **Protect API keys**:
   - Never commit `.env` files to version control
   - Use Docker secrets or environment variable injection
   - Rotate keys regularly

2. **Run as non-root user** (optional enhancement):
   ```dockerfile
   RUN useradd -m -u 1000 shri && \
       chown -R shri:shri /app
   USER shri
   ```

3. **Scan images for vulnerabilities**:
   ```bash
   docker scan shri-sudarshan:latest
   ```

4. **Use private registry**:
   Push images to a private container registry

5. **Network isolation**:
   Use Docker networks to isolate services

### Example Production docker-compose.yml

```yaml
version: '3.8'

services:
  shri-sudarshan:
    image: your-registry/shri-sudarshan:v0.1.0
    restart: always
    env_file: .env
    volumes:
      - /data/shri-sudarshan:/app/data
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
    networks:
      - shri-network
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: shri_sudarshan
      POSTGRES_USER: shri_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - shri-network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - shri-network

secrets:
  db_password:
    file: ./secrets/db_password.txt

volumes:
  postgres-data:
  redis-data:

networks:
  shri-network:
    driver: bridge
```

### Deployment Checklist

- [ ] Build and tag production image
- [ ] Test image locally with production configuration
- [ ] Push image to container registry
- [ ] Set up production server with Docker installed
- [ ] Transfer `.env` file securely (or use secrets management)
- [ ] Create data directories with correct permissions
- [ ] Deploy with `docker-compose up -d`
- [ ] Verify services are running: `docker-compose ps`
- [ ] Check logs: `docker-compose logs`
- [ ] Test application functionality
- [ ] Set up monitoring and alerting
- [ ] Configure backups for data volumes
- [ ] Document rollback procedure

### Scaling

For horizontal scaling with multiple containers:

```yaml
services:
  shri-sudarshan:
    # ... other config ...
    deploy:
      replicas: 3
```

Or use Docker Swarm / Kubernetes for more advanced orchestration.

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Project Shri Sudarshan README](README.md)
- [GitHub Repository](https://github.com/s-p-c-git/ShriSudarshan)

## Support

For issues and questions:
- Open an issue on [GitHub Issues](https://github.com/s-p-c-git/ShriSudarshan/issues)
- Check existing documentation in the `docs/` directory
- Review the main [README.md](README.md) file

---

**Note**: Always use paper trading mode when testing. Live trading involves real financial risk.
