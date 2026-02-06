import sys
import os
import argparse
from unittest.mock import MagicMock
import torch

# --- 1. MOCKING NVDIFFRAST ---
# Ini harus dilakukan SEBELUM import apapun dari InstantMesh
print("[Wrapper] Setting up Mock Nvdiffrast...")

class MockContext:
    def __init__(self, *args, **kwargs):
        pass

def mock_rasterize(*args, **kwargs):
    # Return dummy tensors compatible with what expected
    # Usually: rast, rast_db
    # Shape logic might be needed if strict checking, but let's try generic
    return torch.zeros(1), torch.zeros(1)

def mock_interpolate(*args, **kwargs):
    return torch.zeros(1), torch.zeros(1)

def mock_antialias(*args, **kwargs):
    return torch.zeros(1)

# Create Mock Module
mock_nvdiffrast = MagicMock()
mock_nvdiffrast.RasterizeGLContext = MockContext

mock_torch = MagicMock()
mock_torch.rasterize = mock_rasterize
mock_torch.interpolate = mock_interpolate
mock_torch.antialias = mock_antialias

sys.modules["nvdiffrast"] = mock_nvdiffrast
sys.modules["nvdiffrast.torch"] = mock_torch

print("[Wrapper] Nvdiffrast mocked successfully.")

# --- 2. FORCE CPU ---
# Hook torch.cuda.is_available to always return False inside this process
# This forces InstantMesh to use CPU path if it checks availability
# But we also stick to "cpu" device string
original_is_available = torch.cuda.is_available
torch.cuda.is_available = lambda: False
print("[Wrapper] Forced CPU Mode (CUDA disabled).")

# --- 3. RUN INSTANTMESH LOGIC ---
# We need to add InstantMesh to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
instant_mesh_root = os.path.join(current_dir, "InstantMesh")
if instant_mesh_root not in sys.path:
    sys.path.insert(0, instant_mesh_root)

# Change working directory so InstantMesh finds its configs
os.chdir(instant_mesh_root)

# CLI Parser to match run.py expectation or forward args
# run.py usage: python run.py configs/instant-mesh-large.yaml examples/hatsune_miku.png --output_path output/
if __name__ == "__main__":
    # Remove the wrapper script name from argv so run.py sees correct args
    # We expect this script to be called exactly like run.py: with config and image args
    
    # Argv[0] is this script. 
    # run.py expects args start from index 1. 
    # So we can just invoke run.py main block inside this env.
    
    try:
        print(f"[Wrapper] Importing run.py logic from {instant_mesh_root}")
        
        # Method: Use runpy to execute the script in this process standardly
        import runpy
        
        # We need to ensure 'run' module is found if we use run_module, 
        # but since run.py is a script, we use run_path.
        run_path_target = "run.py"
        
        # Execute it!
        runpy.run_path(run_path_target, run_name="__main__")
        
    except Exception as e:
        print(f"[Wrapper] Error running InstantMesh: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
