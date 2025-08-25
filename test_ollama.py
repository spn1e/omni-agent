#!/usr/bin/env python3
"""
Simple test to debug Ollama connection
"""

import requests
import litellm
import os

print("🧪 Testing Ollama Connection")
print("=" * 40)

# Test 1: HTTP API
print("1. Testing HTTP API...")
try:
    response = requests.get("http://localhost:11434/api/version", timeout=5)
    print(f"✅ HTTP Status: {response.status_code}")
    print(f"✅ Response: {response.json()}")
except Exception as e:
    print(f"❌ HTTP Error: {e}")
    exit(1)

# Test 2: LiteLLM with environment
print("\n2. Testing LiteLLM...")
os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"

try:
    response = litellm.completion(
        model="ollama/llama3:8b",
        messages=[{"role": "user", "content": "Hello"}],
        timeout=15
    )
    print("✅ LiteLLM Success!")
    print(f"✅ Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ LiteLLM Error: {e}")
    print(f"❌ Error type: {type(e)}")

print("\n🎉 Test complete!")
