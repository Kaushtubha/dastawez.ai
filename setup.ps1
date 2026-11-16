# Dastawez.ai (DocuMind) - Quick Start Script for Windows PowerShell

Write-Host "🚀 Welcome to Dastawez.ai (DocuMind) Setup!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 18+ first." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "📦 Setting up Python virtual environment (.venv)..." -ForegroundColor Blue
if (-not (Test-Path .venv)) {
    python -m venv .venv
}

# Install Python dependencies using direct venv binary
Write-Host ""
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Blue
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Set up environment file
if (-not (Test-Path .env)) {
    Write-Host ""
    Write-Host "⚙️ Creating environment configuration..." -ForegroundColor Blue
    Copy-Item .env.example .env
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host "⚠️ Please review and update .env with your settings" -ForegroundColor Yellow
}

# Install frontend dependencies
Write-Host ""
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Blue
Set-Location frontend
if (Get-Command npm.cmd -ErrorAction SilentlyContinue) {
    & npm.cmd install
} else {
    npm install
}
Set-Location ..

# Initialize database
Write-Host ""
Write-Host "🗄️ Initializing database..." -ForegroundColor Blue
& .\.venv\Scripts\python.exe -c "from app.db.metadata import init_db; init_db()"

# Create uploads and static directories
if (-not (Test-Path uploads)) {
    New-Item -ItemType Directory -Path uploads | Out-Null
}
if (-not (Test-Path app\static)) {
    New-Item -ItemType Directory -Path app\static | Out-Null
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Review and update .env file with your settings" -ForegroundColor White
Write-Host ""
Write-Host "2. Start the backend server:" -ForegroundColor White
Write-Host "   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. In a new terminal, start the frontend (development mode):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Yellow
Write-Host "   npm run dev" -ForegroundColor Yellow
Write-Host ""
Write-Host "   OR build frontend into backend for single-port serving:" -ForegroundColor White
Write-Host "   cd frontend; npm.cmd run build" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Access the application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
