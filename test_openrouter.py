#!/usr/bin/env python3
"""
Test OpenRouter API connection
"""

import os
from dotenv import load_dotenv
import litellm

# Load environment
load_dotenv()

print("🔍 Testing OpenRouter Setup")
print("=" * 40)

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key[:20] if api_key else 'None'}...")

if not api_key:
    print("❌ No API key found in .env file")
    exit(1)

if not api_key.startswith("sk-or-"):
    print("❌ This doesn't look like an OpenRouter key (should start with sk-or-)")
    print("💡 OpenRouter keys start with 'sk-or-v1-'")
    exit(1)

print("✅ OpenRouter key format looks correct")

# Test OpenRouter connection
print("\n🧪 Testing OpenRouter API...")
try:
    response = litellm.completion(
        model="openrouter/anthropic/claude-3.5-sonnet",
        messages=[{"role": "user", "content": "Hello, just testing the connection"}],
        api_key=api_key,
        timeout=30
    )
    print("✅ OpenRouter connection successful!")
    print(f"✅ Response: {response.choices[0].message.content[:100]}...")
except Exception as e:
    print(f"❌ OpenRouter connection failed: {e}")
    if "401" in str(e):
        print("💡 This is an authentication error - check your API key")
    elif "402" in str(e):
        print("💡 This is a billing error - check your OpenRouter credits")

print("\n🎉 Test complete!")
