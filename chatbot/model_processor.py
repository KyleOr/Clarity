import os
import subprocess
import json
import tempfile
from typing import List, Optional

# Global variables
SELECTED_MODEL = None
LLAMA_CPP_PATH = None

def find_llama_executable():
    """Find the llama.cpp executable"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    llama_dir = os.path.join(base_dir, "llama.cpp")
    
    # Common executable names and paths
    possible_paths = [
        os.path.join(llama_dir, "build", "bin", "Release", "llama-cli.exe"),
        os.path.join(llama_dir, "build", "bin", "llama-cli.exe"),
        os.path.join(llama_dir, "build", "bin", "llama-cli"),
        os.path.join(llama_dir, "build", "bin", "main.exe"),
        os.path.join(llama_dir, "build", "bin", "main"),
        os.path.join(llama_dir, "llama-cli.exe"),
        os.path.join(llama_dir, "llama-cli"),
        os.path.join(llama_dir, "main.exe"),
        os.path.join(llama_dir, "main"),
        # Also check x64 build folder (Visual Studio builds)
        os.path.join(llama_dir, "build", "x64", "Release", "llama-cli.exe"),
        os.path.join(llama_dir, "build", "x64", "Release", "main.exe"),
    ]
    
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    
    return None

def get_available_models() -> List[str]:
    """Get list of available GGUF models"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "model")
    
    if not os.path.exists(model_dir):
        return []
    
    models = []
    for file in os.listdir(model_dir):
        if file.endswith('.gguf'):
            models.append(file)
    
    return sorted(models)

def set_model(model_name: str) -> bool:
    """Set the selected model"""
    global SELECTED_MODEL, LLAMA_CPP_PATH
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "model", model_name)
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return False
    
    # Find llama.cpp executable
    LLAMA_CPP_PATH = find_llama_executable()
    if not LLAMA_CPP_PATH:
        print("❌ llama.cpp executable not found!")
        print("   Please build llama.cpp first:")
        print("   1. cd chatbot/llama.cpp")
        print("   2. mkdir build && cd build")
        print("   3. cmake .. -DLLAMA_CUDA=ON (for CUDA support)")
        print("   4. cmake --build . --config Release")
        return False
    
    SELECTED_MODEL = model_path
    print(f"✅ Model set: {model_name}")
    print(f"✅ Executable: {LLAMA_CPP_PATH}")
    
    # Test CUDA availability
    if test_cuda_support():
        print("✅ CUDA support detected")
    else:
        print("⚠️  CUDA support not detected, will use CPU")
    
    return True

def test_cuda_support() -> bool:
    """Test if CUDA is available for llama.cpp"""
    if not LLAMA_CPP_PATH:
        return False
    
    try:
        # Run llama.cpp with --help to check for CUDA options
        result = subprocess.run([LLAMA_CPP_PATH, "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        # Check if GPU-related flags are available
        help_text = result.stdout.lower()
        return any(flag in help_text for flag in ['-ngl', '--n-gpu-layers', 'gpu', 'cuda'])
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False

def generate_response(prompt: str, n_tokens: int = 200, temperature: float = 0.7) -> str:
    """Generate response using llama.cpp with CUDA support"""
    if not SELECTED_MODEL or not LLAMA_CPP_PATH:
        return "❌ Model not initialized. Please run set_model() first."
    
    try:
        # Create temporary file for the prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(prompt)
            temp_prompt_path = temp_file.name
        
        # Build command with CUDA support
        cmd = [
            LLAMA_CPP_PATH,
            "-m", SELECTED_MODEL,
            "-f", temp_prompt_path,
            "-n", str(n_tokens),
            "--temp", str(temperature),
            "-ngl", "35",  # Use GPU layers (adjust based on your GPU VRAM)
            "--no-display-prompt",
            "-s", "42",  # Seed for reproducibility
            "--ctx-size", "2048",  # Context size
        ]
        
        # Run llama.cpp
        print(f"🚀 Running inference with CUDA...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Clean up temp file
        os.unlink(temp_prompt_path)
        
        if result.returncode != 0:
            print(f"❌ llama.cpp error: {result.stderr}")
            return "❌ Error generating response"
        
        # Extract the generated text
        output = result.stdout.strip()
        
        # Remove any system messages or prompts that might be echoed
        lines = output.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and system messages
            if line and not any(skip_phrase in line.lower() for skip_phrase in [
                'llama_print_timings',
                'prompt eval',
                'eval time',
                'total time',
                'load time',
                'sample time'
            ]):
                cleaned_lines.append(line)
        
        response = '\n'.join(cleaned_lines).strip()
        
        # If response is empty or too short, return a default message
        if len(response) < 10:
            return "I understand your question, but I need more context to provide a detailed response."
        
        return response
        
    except subprocess.TimeoutExpired:
        return "❌ Response generation timed out"
    except Exception as e:
        print(f"❌ Error: {e}")
        return "❌ Error generating response"

def get_model_info() -> dict:
    """Get information about the current model"""
    if not SELECTED_MODEL:
        return {"error": "No model selected"}
    
    model_name = os.path.basename(SELECTED_MODEL)
    model_size = os.path.getsize(SELECTED_MODEL) / (1024 * 1024)  # Size in MB
    
    return {
        "name": model_name,
        "path": SELECTED_MODEL,
        "size_mb": round(model_size, 1),
        "executable": LLAMA_CPP_PATH,
        "cuda_available": test_cuda_support()
    }

def initialize_chatbot() -> bool:
    """Initialize the chatbot with the first available model"""
    models = get_available_models()
    
    if not models:
        print("❌ No GGUF models found in the model directory!")
        return False
    
    # Try to set the first available model
    return set_model(models[0])

# Auto-initialize on import if models are available
if __name__ != "__main__":
    models = get_available_models()
    if models and not SELECTED_MODEL:
        set_model(models[0])
