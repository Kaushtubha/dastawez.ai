#!/bin/bash

# DocuMind AI - Quick Start Script for Unix/Linux/macOS

echo "🚀 Welcome to DocuMind AI Setup!"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi

echo -e "${BLUE}✓ Python found:$(python3 --version)${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16+ first.${NC}"
    exit 1
fi

echo -e "${BLUE}✓ Node.js found:$(node --version)${NC}"

# Create virtual environment
echo ""
echo -e "${BLUE}📦 Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo -e "${BLUE}📥 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment file
if [ ! -f .env ]; then
    echo ""
    echo -e "${BLUE}⚙️  Creating environment configuration...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${BLUE}⚠️  Please review and update .env with your settings${NC}"
fi

# Install frontend dependencies
echo ""
echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Initialize database
echo ""
echo -e "${BLUE}🗄️  Initializing database...${NC}"
python -c "from app.db.metadata import init_db; init_db()"

# Create uploads directory if it doesn't exist
mkdir -p uploads

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "================================"
echo "🎯 Next Steps:"
echo ""
echo "1. Review and update .env file with your settings"
echo "2. Start the backend server:"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
