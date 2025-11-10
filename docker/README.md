# Docker Setup for Project Shri Sudarshan

This directory contains all Docker-related files for containerized deployment of Project Shri Sudarshan.

## Quick Start

### 1. Prerequisites
- Docker 20.10+ and Docker Compose 2.0+
- 8GB RAM minimum, 16GB recommended
- OpenAI or Anthropic API key

### 2. Configuration
```bash
# From project root
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Build and Run
```bash
cd docker
docker compose build
docker compose run --rm shri-sudarshan --symbol AAPL
```

Or use the Makefile from project root:
```bash
make setup    # First time only
make build
make run SYMBOL=AAPL
```

## Files in This Directory

- **Dockerfile** - Multi-stage build for optimized image (CPU)
- **docker-compose.yml** - Complete service configuration with PostgreSQL and Redis
- **.dockerignore** - Files to exclude from Docker context
- **DOCKER.md** - Comprehensive documentation (start here!)
- **DOCKER_EXAMPLES.md** - Quick reference examples
- **test_docker_setup.sh** - Validation script

## Documentation

For detailed instructions, see:
- [DOCKER.md](DOCKER.md) - Complete Docker guide
- [DOCKER_EXAMPLES.md](DOCKER_EXAMPLES.md) - Quick examples

## GPU Support

GPU support (for FinBERT/FinGPT) uses a separate Dockerfile:
```bash
# From project root
docker build -f Dockerfile.gpu -t shri-sudarshan:gpu .
docker run --gpus all --rm --env-file .env \
  -v $(pwd)/data:/app/data \
  shri-sudarshan:gpu --symbol AAPL
```

## Production Deployment

For production use with PostgreSQL and Redis:
```bash
cd docker
docker compose --profile production up -d
```

See [DOCKER.md](DOCKER.md) for complete production deployment guide.

## Support

- [Main README](../README.md)
- [Project Documentation](../docs/)
- [GitHub Issues](https://github.com/s-p-c-git/ShriSudarshan/issues)
