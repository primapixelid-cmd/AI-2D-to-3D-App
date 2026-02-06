import os
import torch
import numpy as np
from PIL import Image
from backend.manager import BackendManager

class GenerationPipeline:
    def __init__(self, manager: BackendManager):
        self.manager = manager
        
    def run(self, prompt, image_path, model_name, low_vram=False, on_log_callback=None):
        """
        Runs the full 3D generation pipeline.
        
        Args:
            prompt (str): Not used for image-to-3d but kept for interface.
            image_path (str | dict): Path to input image, or dict for multiview? 
                                     Assume single image path for now.
            model_name (str): Identifier for model (e.g. "InstantMesh")
            low_vram (bool): Enable FP16 / Offloading
        """
        print(f"[Pipeline] Starting generation with {model_name}...")
        
        # 1. Ensure Dependecies and Model
        self.manager.load_model(low_vram)
        
        # Add InstantMesh to path again to be safe
        instant_mesh_path = os.path.join(os.path.dirname(__file__), 'InstantMesh')
        import sys
        if instant_mesh_path not in sys.path:
            sys.path.append(instant_mesh_path)
            
        # 2. Import InstantMesh Modules
        try:
            from src.utils.infer_util import remove_background, resize_foreground
            # Based on standard usage, we might need to instantiate a model class
            # But usually run.py uses a config based system.
            # We will try to simulate what run.py does or import the Main Class if available.
            # Since InstantMesh doesn't have a simple "Pipeline" class in root, 
            # we might need to subprocess output or reconstruct the logic.
            
            # SIMULATION OF LOGIC for Stability (Avoiding complex class reconstruction blindly):
            # If the user has not cloned the repo, this will fail in manager.check_instantmesh_install
            
            # --- REAL LOGIC STUB (Adapting from run.py) ---
            # device = self.manager.get_device()
            # config_path = os.path.join(instant_mesh_path, 'configs', 'instant-mesh-large.yaml')
            # config = OmegaConf.load(config_path)
            # model = instantiate_from_config(config.model).to(device)
            # model.load_state_dict(torch.load(ckpt_path), strict=False)
            
            # For this 'Agent' step, since we can't fully guarantee the repo structure existence
            # without the user cloning it first, we will Implement a subprocess caller 
            # which is more robust for "run.py" integration.
            pass
            
        except ImportError as e:
            raise ImportError(f"InstantMesh modules not found. Did you clone the repo? {e}")

        # 3. Processing
        try:
            # We will use subprocess to call run.py if possible, 
            # Or simplified logic.
            # Let's assume we are calling the internal logic for better control.
            
            # MOCKING THE HEAVY LIFTING FOR NOW TO PREVENT CRASH IF REPO MISSING
            # BUT PROVIDING THE REAL CODE STRUCTURE IN COMMENTS FOR THE USER
            
            # Real Implementation Plan for User:
            # 1. Load config
            # 2. Process Image (Rembg)
            # 3. Run MV Diffusion
            # 4. Run LGM Reconstruction
            # 5. Export Mesh
            
            # Since I cannot execute the real model here (no GPU/repo), I must provide
            # the code that *would* work if environment is correct.
            
            import subprocess
            
            cwd = instant_mesh_path
            # Input handling
            input_file = image_path if isinstance(image_path, str) else image_path.get('front')
            if not input_file or not os.path.exists(input_file):
                raise ValueError("Valid input image required.")
                
            output_dir = os.path.abspath("output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Construct command: Use backend/instantmesh_wrapper.py that handles mocking
            wrapper_script = os.path.join(os.path.dirname(__file__), "instantmesh_wrapper.py")
            if not os.path.exists(wrapper_script):
                 raise FileNotFoundError(f"Wrapper script not found at {wrapper_script}")

            # python backend/instantmesh_wrapper.py configs/instant-mesh-large.yaml input.png --output_path output/
            # Note: The wrapper chdirs to InstantMesh root internally
            
            cmd = [
                sys.executable,
                wrapper_script,
                "configs/instant-mesh-large.yaml",
                input_file,
                "--save_video", 
                "--output_path", output_dir
            ]
            


            print(f"Executing: {' '.join(cmd)}")
            
            # Env with PYTHONPATH
            env = os.environ.copy()
            env["PYTHONPATH"] = env.get("PYTHONPATH", "") + os.pathsep + cwd
            
            # We don't set cwd here because wrapper handles sys.path and chdir
            # We just pass environment if needed, but wrapper is smart enough
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, # Merge stderr to stdout for full logging
                text=True,
                bufsize=1, # Line buffering
                universal_newlines=True
            )
            
            # Real-time output reading
            full_stdout = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    stripped_line = line.strip()
                    if stripped_line:
                        full_stdout.append(stripped_line)
                        print(f"[InstantMesh] {stripped_line}") # Console debug
                        if on_log_callback:
                            on_log_callback(stripped_line)
                            
            return_code = process.poll()
            
            if return_code != 0:
                raise RuntimeError(f"InstantMesh Error (Code {return_code}). Check logs.")
                
            stdout = "\n".join(full_stdout)
            print("InstantMesh Finished.")
            
            # Find the output file
            # InstantMesh output naming might be based on input filename
            base_name = os.path.splitext(os.path.basename(input_file))[0]
             # It usually creates a folder or specific file
             # Let's assume it puts it in output_dir
             
             # Fallback check for generated obj
            result_path = None
            for f in os.listdir(output_dir):
                 if f.endswith('.obj') and base_name in f:
                     result_path = os.path.join(output_dir, f)
                     # Rename to timestamp to avoid overwrites and match App logic?
                     # Kept simple for now.
                     break
            
            if not result_path:
                 # If subprocess worked but file naming is different, verify
                 raise FileNotFoundError("Mesh generation finished but output file not found.")

        except Exception as e:
            # Re-raise to be caught by worker
            raise RuntimeError(f"Pipeline Failed: {e}")
