#!/usr/bin/env python3
"""
OmniAgent Setup Script
Helps configure the environment and download required models.
"""

import os
import subprocess
import sys
from pathlib import Path

def print_banner():
    """Print the setup banner"""
    print("=" * 60)
    print("🤖 OmniAgent Setup Script")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    print("\n🦙 Checking Ollama installation...")
    try:
        # Check if ollama command exists
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama found: {result.stdout.strip()}")
            
            # Check if ollama service is running
            try:
                subprocess.run(["ollama", "list"], capture_output=True, check=True, timeout=10)
                print("✅ Ollama service is running")
                return True
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                print("⚠️  Ollama service not responding. Please start it with: ollama serve")
                return False
        else:
            print("❌ Ollama not found")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed. Please install from https://ollama.ai")
        return False

def download_ollama_models():
    """Download required Ollama models"""
    print("\n📥 Downloading Ollama models...")
    models = ["llama3:8b", "llava"]
    
    for model in models:
        print(f"   Downloading {model}...")
        try:
            subprocess.run(["ollama", "pull", model], check=True)
            print(f"   ✅ {model} downloaded successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to download {model}: {e}")
            return False
    
    return True

def setup_openai_key():
    """Setup OpenAI API key"""
    print("\n🔑 OpenAI API Key Setup")
    print("This is optional but recommended for complex queries.")
    
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key:
        print(f"✅ OpenAI API key already set: {current_key[:8]}...")
        return True
    
    print("To set your OpenAI API key:")
    print("1. Get your API key from https://platform.openai.com/api-keys")
    print("2. Set the environment variable:")
    
    if os.name == 'nt':  # Windows
        print("   PowerShell: $env:OPENAI_API_KEY=\"your-api-key-here\"")
        print("   CMD: set OPENAI_API_KEY=your-api-key-here")
    else:  # Unix/Linux/macOS
        print("   export OPENAI_API_KEY=\"your-api-key-here\"")
    
    print("\nOr add it to your .env file:")
    print("   OPENAI_API_KEY=your-api-key-here")
    
    return True

def create_env_file():
    """Create a .env file template"""
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Creating .env file template...")
        with open(env_file, "w") as f:
            f.write("# OmniAgent Environment Variables\n")
            f.write("# Add your OpenAI API key here (optional)\n")
            f.write("OPENAI_API_KEY=your-api-key-here\n")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def run_tests():
    """Run basic tests to verify setup"""
    print("\n🧪 Running basic tests...")
    
    # Test imports
    try:
        import streamlit
        import litellm
        from PIL import Image
        print("✅ All Python packages imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test Ollama models
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if "llama3:8b" in result.stdout and "llava" in result.stdout:
            print("✅ Required Ollama models found")
        else:
            print("⚠️  Some required models may be missing")
    except Exception as e:
        print(f"⚠️  Could not verify Ollama models: {e}")
    
    return True

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Check Ollama
    ollama_ok = check_ollama()
    if not ollama_ok:
        print("\n⚠️  Ollama setup incomplete. Please:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Start the service: ollama serve")
        print("   3. Run this setup script again")
    
    # Download models if Ollama is available
    if ollama_ok:
        if not download_ollama_models():
            print("\n❌ Failed to download required models")
            sys.exit(1)
    
    # Setup OpenAI key
    setup_openai_key()
    
    # Create .env file
    create_env_file()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print("\nTo start OmniAgent:")
    print("   streamlit run app.py")
    print("\nThe application will open at http://localhost:8501")
    print("\nFor help, see README.md")

if __name__ == "__main__":
    main()
