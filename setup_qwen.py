import requests
import sys
import time

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags')
        return response.status_code == 200
    except:
        return False

def pull_model(model_name="qwen2.5:7b"):
    """Pull the specified model"""
    print(f"⬇️  Pulling {model_name}...")
    
    try:
        response = requests.post(
            'http://localhost:11434/api/pull',
            json={'name': model_name},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                # Simple progress indicator
                if '"status":"pulling"' in data:
                    print(".", end="", flush=True)
                elif '"status":"success"' in data:
                    print("\n✅ Model pulled successfully!")
                    return True
                    
        return True
    except Exception as e:
        print(f"\n❌ Error pulling model: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Setting up Qwen 2.5 7B for Infynd Project")
    
    if not check_ollama():
        print("❌ Ollama is not running! Please start Ollama first.")
        sys.exit(1)
        
    print("✅ Ollama is running")
    pull_model()
    print("\n🎉 Setup complete! You can now run the extraction pipeline.")
