#!/usr/bin/env python3
"""
Test environment variable loading
"""

import os
from dotenv import load_dotenv

print("🔍 Testing Environment Variables")
print("=" * 40)

# Load .env file
load_dotenv()

# Test API key
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key}")

if api_key:
    if api_key.startswith("sk-or-"):
        print("✅ OpenRouter key detected")
    elif api_key.startswith("sk-"):
        print("✅ OpenAI key detected")
    elif api_key == "REPLACE_ME":
        print("❌ Key not set (still REPLACE_ME)")
    else:
        print("⚠️  Unknown key format")
else:
    print("❌ No API key found")

# Test other variables
print(f"Privacy Default: {os.getenv('PRIVACY_DEFAULT')}")
print(f"Ollama URL: {os.getenv('OLLAMA_BASE_URL')}")
print(f"LiteLLM Timeout: {os.getenv('LITELLM_TIMEOUT')}")

print("\n🎯 Check if .env file exists:")
if os.path.exists(".env"):
    print("✅ .env file found")
    with open(".env", "r") as f:
        content = f.read()
        print(f"📄 .env content:\n{content[:200]}...")
else:
    print("❌ .env file not found!")
