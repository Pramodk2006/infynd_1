"""
Setup script to download and configure Phi3.5 model for Ollama
"""

import subprocess
import sys

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ollama is not installed or not running: {e}")
        print("   Please install Ollama from: https://ollama.com/download")
        return False

def pull_phi35():
    """Download Phi3.5 model"""
    print("📥 Downloading Phi3.5 model (this may take a few minutes)...")
    print("   Model size: ~2.2GB")
    
    try:
        # Pull phi3.5
        result = subprocess.run(
            ['ollama', 'pull', 'phi3.5:latest'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Phi3.5 downloaded successfully!")
            return True
        else:
            print(f"❌ Failed to download Phi3.5")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading Phi3.5: {e}")
        return False

def verify_model():
    """Verify that Phi3.5 is available"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'phi3.5' in result.stdout.lower():
            print("✅ Phi3.5 is ready to use!")
            return True
        else:
            print("⚠️  Phi3.5 not found in model list")
            return False
    except Exception as e:
        print(f"❌ Error verifying model: {e}")
        return False

def main():
    print("="*60)
    print("  Phi3.5 Model Setup for Enhanced Extraction")
    print("="*60)
    print()
    
    # Step 1: Check Ollama
    print("1️⃣  Checking Ollama installation...")
    if not check_ollama():
        sys.exit(1)
    print("   ✓ Ollama is running\n")
    
    # Step 2: Download Phi3.5
    print("2️⃣  Downloading Phi3.5 model...")
    if not pull_phi35():
        sys.exit(1)
    print()
    
    # Step 3: Verify
    print("3️⃣  Verifying installation...")
    if not verify_model():
        sys.exit(1)
    print()
    
    print("="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print()
    print("Phi3.5 is now ready for accurate data extraction.")
    print("The model will be used for:")
    print("  • Contact information extraction")
    print("  • People and team member identification")
    print("  • Certifications and compliance detection")
    print("  • Services and products extraction")
    print()
    print("Compared to regex-based extraction, Phi3.5 provides:")
    print("  ✓ Better accuracy for contact details")
    print("  ✓ Contextual understanding of roles and titles")
    print("  ✓ More reliable certification detection")
    print("  ✓ Smarter categorization of services")
    print()

if __name__ == "__main__":
    main()
