# OmniAgent Windows Setup & Run Script
# Run with: powershell -ExecutionPolicy Bypass -File run_win.ps1

Write-Host "🤖 OmniAgent - Windows Setup & Launch" -ForegroundColor Cyan
Write-Host ("=" * 50)

# Check Python
Write-Host "📋 Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    $envContent = @"
OPENAI_API_KEY=REPLACE_ME
PRIVACY_DEFAULT=Normal
OLLAMA_BASE_URL=http://localhost:11434
LITELLM_LOG=info
LITELLM_TIMEOUT=30
"@
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env file created - edit it to add your OpenAI API key" -ForegroundColor Green
}

# Check if Ollama is running
Write-Host "🦙 Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -TimeoutSec 3 2>$null
    Write-Host "✅ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama not detected. Starting setup..." -ForegroundColor Yellow
    Write-Host "Please ensure Ollama is installed and running:" -ForegroundColor White
    Write-Host "  1. Download from: https://ollama.ai" -ForegroundColor White
    Write-Host "  2. Run: ollama serve" -ForegroundColor White
    Write-Host "  3. Pull models: ollama pull llama3:8b; ollama pull llava" -ForegroundColor White
    Write-Host ""
}

# Run tests
Write-Host "🧪 Running routing tests..." -ForegroundColor Yellow
python tests_routing.py

# Launch Streamlit
Write-Host ""
Write-Host "🚀 Launching OmniAgent..." -ForegroundColor Cyan
Write-Host "Access at: http://localhost:8501" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

streamlit run app.py

