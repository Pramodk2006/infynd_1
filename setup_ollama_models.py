"""
Setup Ollama models for classification pipeline.
"""

import subprocess
import sys


def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def pull_model(model_name: str):
    """Pull an Ollama model."""
    print(f"\n📥 Pulling {model_name}...")
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=False
        )
        if result.returncode == 0:
            print(f"✅ {model_name} downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download {model_name}")
            return False
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False


def main():
    """Setup Ollama models."""
    print("=" * 60)
    print("OLLAMA MODEL SETUP")
    print("=" * 60)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("\n❌ Ollama is not installed!")
        print("\n💡 Installation instructions:")
        print("   Windows: Download from https://ollama.com/download")
        print("   Mac: brew install ollama")
        print("   Linux: curl https://ollama.ai/install.sh | sh")
        sys.exit(1)
    
    print("\n✅ Ollama is installed")
    
    # List of models to pull
    models = [
        ("nomic-embed-text", "Embedding model (274MB, required)"),
        ("llama2:latest", "Classification LLM (3.8GB, required)")
    ]
    
    print("\nThe following models will be downloaded:")
    for model, desc in models:
        print(f"  • {model} - {desc}")
    
    print("\n⚠️  Total download size: ~4GB")
    response = input("\nProceed with download? (y/n): ")
    
    if response.lower() != 'y':
        print("Setup cancelled")
        sys.exit(0)
    
    # Pull each model
    success_count = 0
    for model, desc in models:
        if pull_model(model):
            success_count += 1
    
    print("\n" + "=" * 60)
    if success_count == len(models):
        print("✅ ALL MODELS DOWNLOADED SUCCESSFULLY")
        print("\nYou can now run: python test_ollama_pipeline.py")
    else:
        print(f"⚠️  {success_count}/{len(models)} models downloaded")
        print("\nSome models failed to download. Please check errors above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
