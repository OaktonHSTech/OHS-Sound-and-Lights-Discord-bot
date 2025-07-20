#!/usr/bin/env python3
import os
import requests
import json

# Use the same configuration as the bot
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL = os.getenv("MODEL", "phi3:mini")

def test_ollama_connection():
    print(f"Testing connection to Ollama at: {OLLAMA_URL}")
    print(f"Using model: {MODEL}")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        response.raise_for_status()
        print("✓ Ollama service is reachable")
        
        # Check available models
        models_data = response.json()
        available_models = [model['name'] for model in models_data.get('models', [])]
        print(f"Available models: {available_models}")
        
        if MODEL in available_models:
            print(f"✓ Model '{MODEL}' is available")
        else:
            print(f"✗ Model '{MODEL}' is NOT available")
            print("Available models:", available_models)
            
        # Test a simple generation
        print("\nTesting generation...")
        test_response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": "Hello, say hi!"},
            stream=True,
            timeout=30
        )
        test_response.raise_for_status()
        
        response_text = ""
        for line in test_response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    response_text += data["response"]
        
        print(f"✓ Generation test successful: {response_text[:100]}...")
        
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("Make sure Ollama is running and accessible at the specified URL")
    except requests.exceptions.Timeout as e:
        print(f"✗ Request timed out: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    test_ollama_connection() 