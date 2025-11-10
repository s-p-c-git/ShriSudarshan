# Makefile for Project Shri Sudarshan Docker operations
.PHONY: help build build-gpu run run-gpu up down logs clean test shell

# Default target
help:
	@echo "Project Shri Sudarshan - Docker Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Initial setup (copy .env.example, create directories)"
	@echo ""
	@echo "Build:"
	@echo "  make build          - Build Docker image (CPU)"
	@echo "  make build-gpu      - Build Docker image with GPU support"
	@echo ""
	@echo "Run:"
	@echo "  make run SYMBOL=AAPL - Run analysis for a symbol"
	@echo "  make run-gpu SYMBOL=AAPL - Run analysis with GPU"
	@echo ""
	@echo "Docker Compose:"
	@echo "  make up             - Start all services in background"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View logs"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Development:"
	@echo "  make shell          - Open interactive shell in container"
	@echo "  make test           - Run tests in container"
	@echo "  make validate       - Validate Docker configuration"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make clean-all      - Remove containers, volumes, and images"

# Setup
setup:
	@echo "Setting up Project Shri Sudarshan..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file from .env.example"; \
		echo "⚠ Please edit .env and add your API keys"; \
	else \
		echo "✓ .env file already exists"; \
	fi
	@mkdir -p data/chroma_db data/logs
	@echo "✓ Created data directories"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env and add your API keys"
	@echo "  2. Run 'make build' to build the Docker image"
	@echo "  3. Run 'make run SYMBOL=AAPL' to analyze a stock"

# Build targets
build:
	@echo "Building Docker image (CPU)..."
	cd docker && docker build -t shri-sudarshan:latest -f Dockerfile ..
	@echo "✓ Build complete"

build-gpu:
	@echo "Building Docker image with GPU support..."
	docker build -f Dockerfile.gpu -t shri-sudarshan:gpu .
	@echo "✓ Build complete"

# Run targets
SYMBOL ?= AAPL
START_DATE ?=
END_DATE ?=
LOG_LEVEL ?= INFO

run:
	@echo "Running analysis for $(SYMBOL)..."
	cd docker && docker compose run --rm shri-sudarshan \
		--symbol $(SYMBOL) \
		--log-level $(LOG_LEVEL) \
		$(if $(START_DATE),--start_date $(START_DATE)) \
		$(if $(END_DATE),--end_date $(END_DATE))

run-gpu:
	@echo "Running analysis for $(SYMBOL) with GPU..."
	docker run --gpus all --rm \
		--env-file .env \
		-v $(PWD)/data:/app/data \
		shri-sudarshan:gpu \
		--symbol $(SYMBOL) \
		--log-level $(LOG_LEVEL) \
		$(if $(START_DATE),--start_date $(START_DATE)) \
		$(if $(END_DATE),--end_date $(END_DATE))

# Docker Compose targets
up:
	@echo "Starting services..."
	cd docker && docker compose up -d
	@echo "✓ Services started"

down:
	@echo "Stopping services..."
	cd docker && docker compose down
	@echo "✓ Services stopped"

restart: down up

logs:
	cd docker && docker compose logs -f shri-sudarshan

# Development targets
shell:
	@echo "Opening interactive shell..."
	cd docker && docker compose run --rm --entrypoint /bin/bash shri-sudarshan

test:
	@echo "Running tests..."
	cd docker && docker compose run --rm --entrypoint pytest shri-sudarshan

validate:
	@echo "Validating Docker configuration..."
	@./docker/test_docker_setup.sh

# Cleanup targets
clean:
	@echo "Cleaning up containers and volumes..."
	cd docker && docker compose down -v
	@echo "✓ Cleanup complete"

clean-all: clean
	@echo "Removing Docker images..."
	docker rmi shri-sudarshan:latest shri-sudarshan:gpu 2>/dev/null || true
	@echo "Cleaning build cache..."
	docker builder prune -f
	@echo "✓ Full cleanup complete"

# Production targets
REGISTRY ?= your-registry
TAG ?= latest

tag:
	@echo "Tagging image for registry..."
	docker tag shri-sudarshan:latest $(REGISTRY)/shri-sudarshan:$(TAG)
	@echo "✓ Tagged as $(REGISTRY)/shri-sudarshan:$(TAG)"

push: tag
	@echo "Pushing image to registry..."
	docker push $(REGISTRY)/shri-sudarshan:$(TAG)
	@echo "✓ Image pushed"

# Multi-service targets
up-full:
	@echo "Starting all services (with PostgreSQL and Redis)..."
	cd docker && docker compose --profile full up -d
	@echo "✓ All services started"

up-production:
	@echo "Starting production services..."
	cd docker && docker compose --profile production up -d
	@echo "✓ Production services started"
