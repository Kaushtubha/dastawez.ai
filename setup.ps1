# DocuMind AI - Quick Start Script for Windows PowerShell

Write-Host "🚀 Welcome to DocuMind AI Setup!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 16+ first." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "📦 Setting up Python virtual environment..." -ForegroundColor Blue
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host ""
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Blue
python -m pip install --upgrade pip
pip install -r requirements.txt

# Set up environment file
if (-not (Test-Path .env)) {
    Write-Host ""
    Write-Host "⚙️  Creating environment configuration..." -ForegroundColor Blue
    Copy-Item .env.example .env
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host "⚠️  Please review and update .env with your settings" -ForegroundColor Yellow
}

# Install frontend dependencies
Write-Host ""
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Blue
Set-Location frontend
npm install
Set-Location ..

# Initialize database
Write-Host ""
Write-Host "🗄️  Initializing database..." -ForegroundColor Blue
python -c "from app.db.metadata import init_db; init_db()"

# Create uploads directory if it doesn't exist
if (-not (Test-Path uploads)) {
    New-Item -ItemType Directory -Path uploads | Out-Null
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Review and update .env file with your settings" -ForegroundColor White
Write-Host ""
Write-Host "2. Start the backend server:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. In a new terminal, start the frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Yellow
Write-Host "   npm run dev" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Access the application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
