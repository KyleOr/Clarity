import os
import json
from model_processor import generate_response, get_available_models, set_model, get_model_info, initialize_chatbot

base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "output")

# Ensure output folder exists
os.makedirs(output_dir, exist_ok=True)

def select_model():
    """Let user select which model to use"""
    models = get_available_models()
    
    if not models:
        print("❌ No model files (.gguf) found in the 'model' directory!")
        print("   Please add some GGUF model files to the model folder.")
        return False
    
    print(f"\n{'='*60}")
    print("SELECT CLARITY CHATBOT MODEL")
    print(f"{'='*60}")
    
    if len(models) == 1:
        print(f"📄 Only one model available: {models[0]}")
        return set_model(models[0])
    
    print("Available models:")
    for i, model in enumerate(models, 1):
        # Show file size
        model_path = os.path.join(base_dir, "model", model)
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print(f"{i:2d}. {model} ({size_mb:.1f} MB)")
        else:
            print(f"{i:2d}. {model}")
    
    while True:
        try:
            selection = input(f"\nSelect model (1-{len(models)}): ").strip()
            index = int(selection) - 1
            
            if 0 <= index < len(models):
                selected_model = models[index]
                if set_model(selected_model):
                    print(f"✅ Selected model: {selected_model}")
                    return True
                else:
                    print(f"❌ Failed to initialize model: {selected_model}")
                    return False
            else:
                print(f"❌ Please enter a number between 1 and {len(models)}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
            return False

def test_model_setup():
    """Test the model setup and CUDA configuration"""
    print(f"\n{'='*60}")
    print("TESTING MODEL SETUP")
    print(f"{'='*60}")
    
    # Get model info
    info = get_model_info()
    
    if "error" in info:
        print(f"❌ {info['error']}")
        return False
    
    print(f"📄 Model: {info['name']}")
    print(f"📁 Path: {info['path']}")
    print(f"📏 Size: {info['size_mb']} MB")
    print(f"⚡ Executable: {info['executable']}")
    print(f"🚀 CUDA Available: {'✅ Yes' if info['cuda_available'] else '❌ No'}")
    
    # Test with a simple prompt
    print("\n🧪 Running test inference...")
    test_prompt = "Hello, I am Clarity, an AI assistant for digital safety. I help users understand"
    
    try:
        response = generate_response(test_prompt, n_tokens=50, temperature=0.7)
        print(f"✅ Test successful!")
        print(f"📝 Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_build_instructions():
    """Show instructions for building llama.cpp with CUDA"""
    print(f"\n{'='*60}")
    print("LLAMA.CPP BUILD INSTRUCTIONS")
    print(f"{'='*60}")
    print("To build llama.cpp with CUDA support:")
    print()
    print("1. Open Command Prompt/PowerShell as Administrator")
    print("2. Navigate to the llama.cpp directory:")
    print(f"   cd {os.path.join(base_dir, 'llama.cpp')}")
    print()
    print("3. Create build directory:")
    print("   mkdir build")
    print("   cd build")
    print()
    print("4. Configure with CUDA (requires CUDA Toolkit installed):")
    print("   cmake .. -DLLAMA_CUDA=ON")
    print()
    print("5. Build (this may take several minutes):")
    print("   cmake --build . --config Release")
    print()
    print("6. The executable will be in build/bin/ or build/x64/Release/")
    print()
    print("📋 Prerequisites:")
    print("   - CUDA Toolkit (11.8+ recommended)")
    print("   - Visual Studio 2019/2022 with C++ tools")
    print("   - CMake 3.18+")

def check_prerequisites():
    """Check if prerequisites are installed"""
    print(f"\n{'='*60}")
    print("CHECKING PREREQUISITES")
    print(f"{'='*60}")
    
    # Check if llama.cpp directory exists
    llama_dir = os.path.join(base_dir, "llama.cpp")
    if os.path.exists(llama_dir):
        print("✅ llama.cpp directory found")
    else:
        print("❌ llama.cpp directory not found")
        return False
    
    # Check for executable
    from model_processor import find_llama_executable
    exe_path = find_llama_executable()
    
    if exe_path:
        print(f"✅ llama.cpp executable found: {exe_path}")
    else:
        print("❌ llama.cpp executable not found")
        print("   Build llama.cpp first (see build instructions)")
        return False
    
    # Check for models
    models = get_available_models()
    if models:
        print(f"✅ {len(models)} model(s) found: {', '.join(models)}")
    else:
        print("❌ No GGUF models found in model/ directory")
        return False
    
    return True

def main():
    print("🎯 Clarity Chatbot Controller")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n⚠️  Prerequisites not met.")
        show_build_instructions()
        return
    
    # Try to auto-initialize
    if initialize_chatbot():
        print("✅ Auto-initialized with default model")
    else:
        # Manual model selection
        if not select_model():
            return
    
    # Test the setup
    if test_model_setup():
        print("\n🎉 Clarity chatbot is ready!")
        print("   You can now integrate it with the browser extension.")
        
        # Show integration info
        print(f"\n{'='*60}")
        print("INTEGRATION INFORMATION")
        print(f"{'='*60}")
        print("To integrate with Clarity extension:")
        print("1. Import: from chatbot.chatbot import generate_chat_response")
        print("2. Use: response = generate_chat_response(user_question, analysis_context)")
        print("3. The chatbot will use CUDA automatically if available")
        
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")

if __name__ == "__main__":
    main()
