#!/bin/bash

# AI Disease Diagnosis System Startup Script
# This script sets up and runs the disease diagnosis system

echo "🏥 AI Disease Diagnosis System Startup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi
print_success "Virtual environment activated"

# Check if requirements are installed
if [ ! -f "venv/pyvenv.cfg" ] || [ ! -f "venv/installed_packages.txt" ]; then
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    pip freeze > venv/installed_packages.txt
    print_success "Dependencies installed"
else
    print_status "Dependencies already installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    if [ -f ".env.example" ]; then
        print_status "Copying .env.example to .env..."
        cp .env.example .env
        print_warning "Please edit .env file with your database credentials"
        print_warning "Then run this script again"
        exit 1
    else
        print_error ".env.example not found. Please create .env file manually"
        exit 1
    fi
fi

# Check MySQL connection (optional - will be checked by the app)
print_status "Checking system requirements..."

# Initialize database if needed
if [ "$1" = "--init-db" ]; then
    print_status "Initializing database..."
    python init_db.py
    if [ $? -eq 0 ]; then
        print_success "Database initialized successfully"
    else
        print_error "Database initialization failed"
        exit 1
    fi
fi

# Start the application
print_status "Starting AI Disease Diagnosis System..."
echo ""
echo "🌐 Server will be available at:"
echo "   Main Page:      http://localhost:8000"
echo "   User Dashboard: http://localhost:8000/static/user/index.html"
echo "   Admin Panel:    http://localhost:8000/static/admin/index.html"
echo "   API Docs:       http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend && python main.py