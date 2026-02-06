import os
import sys
import torch
import gc
from huggingface_hub import snapshot_download

try:
    import xatlas
except ImportError:
    print("Warning: xatlas not found. UV unwrapping might fail or be slow.")
    xatlas = None


# Mock Nvdiffrast if missing (to avoid crashes during import checks)
try:
    import nvdiffrast
except ImportError:
    from unittest.mock import MagicMock
    print("Warning: nvdiffrast not found. Mocking for CPU mode.")
    sys.modules["nvdiffrast"] = MagicMock()
    sys.modules["nvdiffrast.torch"] = MagicMock()

class BackendManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BackendManager, cls).__new__(cls)
            cls._instance.pipeline = None
            cls._instance.model_loaded = False
            cls._instance._is_running = False
            cls._instance._stop_requested = False
        return cls._instance

    def check_instantmesh_install(self):
        """Checks if InstantMesh is cloned in the backend folder."""
        instant_mesh_path = os.path.join(os.path.dirname(__file__), 'InstantMesh')
        if not os.path.exists(instant_mesh_path):
            raise ImportError("InstantMesh repository not found at backend/InstantMesh. Please clone it.")
        
        # Add to sys path to allow imports
        if instant_mesh_path not in sys.path:
            sys.path.append(instant_mesh_path)

    def load_model(self, low_vram=False):
        """Loads the InstantMesh model."""
        if self.model_loaded:
            return

        print("Loading InstantMesh model...")
        self.check_instantmesh_install()
        
        # Import dynamically to avoid top-level errors if rep missing
        try:
            from src.utils.infer_util import remove_background, resize_foreground
            # We will use the pipeline logic in pipeline.py, 
            # but here we might want to pre-load weights if possible
            # For now, we'll let the pipeline handle lazy loading or init
        except ImportError as e:
            raise ImportError(f"Failed to import InstantMesh modules: {e}")

        # Check/Download Weights
        weight_path = os.path.join(os.path.dirname(__file__), 'InstantMesh', 'ckpts')
        if not os.path.exists(os.path.join(weight_path, 'instant_mesh_large.ckpt')):
            print("Downloading weights from HuggingFace...")
            snapshot_download(repo_id="TencentARC/InstantMesh", local_dir=weight_path)
        
        self.model_loaded = True
        print("Model Environment Ready.")

    def unload_model(self):
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
        
        gc.collect()
        torch.cuda.empty_cache()
        self.model_loaded = False
        print("Model Unloaded.")

    def get_device(self):
        # Auto-switch to CPU if CUDA not available or if forced
        if not torch.cuda.is_available():
            print("CUDA not available. Using CPU.")
            return "cpu"
        return "cuda"
        
    def set_running(self, running: bool):
        self._is_running = running
        if running:
            self._stop_requested = False # Reset stop flag on start
            
    def request_stop(self):
        print("Stop requested...")
        self._stop_requested = True
        
    def should_stop(self):
        return self._stop_requested
