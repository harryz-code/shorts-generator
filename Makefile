.PHONY: help install install-dev install-gpu test lint format clean build run cli dashboard install-ffmpeg

help: ## Show this help message
	@echo "Short Video Generator - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

install-gpu: ## Install GPU-accelerated dependencies
	pip install -e ".[gpu]"

install-social: ## Install social media API dependencies
	pip install -e ".[social-media]"

install-ffmpeg: ## Install FFmpeg (macOS)
	@echo "Installing FFmpeg..."
	@if command -v brew >/dev/null 2>&1; then \
		brew install ffmpeg; \
	else \
		echo "Homebrew not found. Please install FFmpeg manually:"; \
		echo "https://ffmpeg.org/download.html"; \
	fi

test: ## Run tests
	python -m pytest tests/ -v

lint: ## Run linting checks
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	mypy .

format: ## Format code with black
	black . --line-length=88

clean: ## Clean up temporary files and build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf temp/*
	rm -rf output/*
	rm -rf logs/*.log

build: ## Build the package
	python setup.py sdist bdist_wheel

run: ## Run the main application
	python main.py

cli: ## Run the CLI interface
	python cli.py --help

dashboard: ## Start the web dashboard
	python -c "from web.dashboard import start_dashboard; import asyncio; asyncio.run(start_dashboard())"

install-system: install-ffmpeg install install-dev ## Install all system dependencies

setup-dev: install-system format lint test ## Setup development environment

docker-build: ## Build Docker image
	docker build -t short-video-generator .

docker-run: ## Run Docker container
	docker run -p 8000:8000 short-video-generator

docker-clean: ## Clean Docker images
	docker rmi short-video-generator

venv: ## Create virtual environment
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "source venv/bin/activate  # On macOS/Linux"
	@echo "venv\\Scripts\\activate     # On Windows"

venv-activate: ## Show virtual environment activation command
	@echo "To activate the virtual environment:"
	@echo "source venv/bin/activate  # On macOS/Linux"
	@echo "venv\\Scripts\\activate     # On Windows"

check-deps: ## Check for missing dependencies
	@echo "Checking for missing dependencies..."
	@python -c "import pkg_resources; pkg_resources.require(open('requirements.txt').readlines())" 2>/dev/null || echo "Some dependencies are missing. Run 'make install' to install them."

check-system: ## Check system requirements
	@echo "Checking system requirements..."
	@python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
	@python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
	@python -c "import PIL; print(f'Pillow version: {PIL.__version__}')"
	@if command -v ffmpeg >/dev/null 2>&1; then \
		echo "FFmpeg: ✓ Installed"; \
	else \
		echo "FFmpeg: ✗ Not installed. Run 'make install-ffmpeg'"; \
	fi

logs: ## Show recent logs
	tail -f logs/*.log

reset-db: ## Reset database (WARNING: This will delete all data)
	@echo "WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f data/*.db data/*.sqlite*; \
		echo "Database reset complete."; \
	else \
		echo "Database reset cancelled."; \
	fi

backup: ## Create backup of data and configuration
	@echo "Creating backup..."
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	@cp -r data/ backups/$(shell date +%Y%m%d_%H%M%S)/data/
	@cp -r config/ backups/$(shell date +%Y%m%d_%H%M%S)/config/
	@cp .env backups/$(shell date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "No .env file to backup"
	@echo "Backup created in backups/$(shell date +%Y%m%d_%H%M%S)/"

deploy: clean build ## Clean, build, and prepare for deployment
	@echo "Deployment package ready in dist/"

.PHONY: help
.DEFAULT_GOAL := help
