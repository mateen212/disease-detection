# Makefile for AI Disease Diagnosis System

.PHONY: help install setup run clean test docs

# Default target
help:
	@echo "🏥 AI Disease Diagnosis System - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install     - Install dependencies and setup environment"
	@echo "  make setup       - Complete setup including database initialization"
	@echo ""
	@echo "Run Commands:"
	@echo "  make run         - Start the application server"
	@echo "  make dev         - Start in development mode with auto-reload"
	@echo ""
	@echo "Database Commands:"
	@echo "  make init-db     - Initialize database tables"
	@echo "  make reset-db    - Reset database (WARNING: destroys all data)"
	@echo ""
	@echo "Development Commands:"
	@echo "  make test        - Run test suite"
	@echo "  make lint        - Run code linting"
	@echo "  make format      - Format code with black"
	@echo "  make docs        - Generate documentation"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean       - Clean temporary files and caches"
	@echo "  make requirements - Update requirements.txt"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully"

# Complete setup
setup: install
	@echo "🔧 Setting up environment..."
	@if [ ! -f ".env" ]; then \
		cp .env.example .env; \
		echo "⚠️  Please edit .env file with your database credentials"; \
	fi
	@echo "🗄️  Initializing database..."
	python init_db.py
	@echo "✅ Setup completed successfully"

# Run the application
run:
	@echo "🚀 Starting AI Disease Diagnosis System..."
	cd backend && python main.py

# Run in development mode
dev:
	@echo "🛠️  Starting in development mode..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Initialize database
init-db:
	@echo "🗄️  Initializing database..."
	python init_db.py

# Reset database (WARNING: destroys all data)
reset-db:
	@echo "⚠️  WARNING: This will destroy all data in the database!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		python -c "from backend.db.database import engine; from backend.models.database_models import Base; Base.metadata.drop_all(engine); print('Database reset completed')"; \
		python init_db.py; \
	else \
		echo "Operation cancelled"; \
	fi

# Run tests
test:
	@echo "🧪 Running test suite..."
	python -m pytest tests/ -v --cov=backend --cov-report=html
	@echo "📊 Coverage report generated in htmlcov/"

# Lint code
lint:
	@echo "🔍 Running code linting..."
	flake8 backend/ --max-line-length=100 --ignore=E203,W503
	pylint backend/ --disable=C0114,C0116

# Format code
format:
	@echo "🎨 Formatting code..."
	black backend/ --line-length=100
	isort backend/ --profile black

# Generate documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "API Documentation available at: http://localhost:8000/docs"
	@echo "System documentation in README.md"

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Update requirements
requirements:
	@echo "📝 Updating requirements.txt..."
	pip freeze > requirements.txt
	@echo "✅ Requirements updated"

# Docker commands (if using Docker in the future)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t disease-diagnosis-system .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 disease-diagnosis-system

# Development database with sample data
sample-data:
	@echo "📊 Loading sample data..."
	cd backend && python -c "from ml.random_forest_model import RandomForestModel; rf = RandomForestModel(); rf.train(); print('Sample data generated and model trained')"

# Check system health
health-check:
	@echo "💓 Checking system health..."
	curl -s http://localhost:8000/api/v1/health | python -m json.tool

# Performance test
performance:
	@echo "⚡ Running performance tests..."
	@echo "Install 'ab' (Apache Bench) for load testing"
	ab -n 100 -c 10 http://localhost:8000/api/v1/health