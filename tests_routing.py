#!/usr/bin/env python3
"""
Pure Python tests for OmniAgent routing logic
Run with: python tests_routing.py
"""

# Import functions from app.py
from app import is_creative_or_complex, route_model, EnvStatus

def test_is_creative_or_complex():
    """Test creative/complex detection per spec"""
    test_cases = [
        ("Hello", False),
        ("Write a poem about spring", True),  # keyword: poem
        ("x" * 200, True),  # length > 180
        ("Design a new architecture", True),  # keyword: design + architecture
        ("What is 2+2?", False),  # simple
        ("Research plan\n\nfor AI", True),  # keyword + multiple paragraphs
        ("Simple question here", False),
        ("Generate code for sorting", True),  # keyword: generate code
        ("Brainstorm ideas", True),  # keyword: brainstorm
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, expected in test_cases:
        result = is_creative_or_complex(text)
        status = "PASS" if result == expected else "FAIL"
        print(f"  {status}: is_creative_or_complex('{text[:30]}...') → {result} (expected {expected})")
        if result == expected:
            passed += 1
    
    print(f"is_creative_or_complex: {passed}/{total} tests passed\n")
    return passed == total

def test_route_model():
    """Test model routing logic per spec"""
    
    # Mock environment statuses
    env_openai_yes = EnvStatus(openai_available=True, ollama_available=True)
    env_openai_no = EnvStatus(openai_available=False, ollama_available=True)
    
    test_cases = [
        # Format: (has_image, text, privacy, env, expected_model)
        (True, "What's in this image?", "Normal", env_openai_yes, "ollama/llava"),
        (True, "Describe the photo", "High", env_openai_yes, "ollama/llava"),
        (False, "Hello", "High", env_openai_yes, "ollama/llama3:8b"),
        (False, "Write a complex strategy document", "High", env_openai_yes, "ollama/llama3:8b"),
        (False, "Write a poem about nature", "Normal", env_openai_yes, "openai/gpt-4o"),
        (False, "Write a poem about nature", "Normal", env_openai_no, "ollama/llama3:8b"),
        (False, "What is 2+2?", "Normal", env_openai_yes, "ollama/llama3:8b"),
        (False, "x" * 200, "Normal", env_openai_yes, "openai/gpt-4o"),  # long text
        (False, "x" * 200, "Normal", env_openai_no, "ollama/llama3:8b"),  # long text, no openai
    ]
    
    passed = 0
    total = len(test_cases)
    
    for has_image, text, privacy, env, expected in test_cases:
        result = route_model(has_image, text, privacy, env)
        status = "PASS" if result == expected else "FAIL"
        description = f"image={has_image}, privacy={privacy}, openai={env.openai_available}, text='{text[:20]}...'"
        print(f"  {status}: route_model({description}) → {result} (expected {expected})")
        if result == expected:
            passed += 1
    
    print(f"route_model: {passed}/{total} tests passed\n")
    return passed == total

def main():
    """Run all tests"""
    print("OmniAgent Routing Tests")
    print("=" * 50)
    
    all_passed = True
    
    print("Testing is_creative_or_complex():")
    all_passed &= test_is_creative_or_complex()
    
    print("Testing route_model():")
    all_passed &= test_route_model()
    
    print("=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())

