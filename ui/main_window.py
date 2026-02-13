from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QProgressBar, QLabel, QFileDialog, QMessageBox,
    QSplitter, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from .sidebar import SidebarWidget
from .viewport import ViewportWidget
from .log_panel import LogWidget
from .asset_manager import AssetManagerWidget
from .theme import DARK_THEME

# Placeholder for the backend worker
class GenerationWorker(QThread):
    progress_update = Signal(int, str) # value, status text
    finished_success = Signal(object, str) # mesh object, saved file path
    finished_error = Signal(str)

    def __init__(self, prompt, image_path, model_name, low_vram):
        super().__init__()
        self.prompt = prompt
        self.image_path = image_path
        self.model_name = model_name
        self.low_vram = low_vram

    def run(self):
        from backend.manager import BackendManager
        from backend.pipeline import GenerationPipeline
        import trimesh
        import time
        import os

        try:
            manager = BackendManager()
            pipeline = GenerationPipeline(manager)
            
            self.progress_update.emit(10, "Initializing Model & Pipeline...")
            time.sleep(1)
            self.progress_update.emit(30, "Loading Model weights...")
            
            # Wrapper for signal emission because pipeline runs in this thread
            def log_callback(msg):
                self.progress_update.emit(-1, msg) # -1 indicates log only, not progress value change

            pipeline.run(self.prompt, self.image_path, self.model_name, self.low_vram, on_log_callback=log_callback)
            
            self.progress_update.emit(60, "Generating Geometry...")
            time.sleep(1)
            
            self.progress_update.emit(90, "Finalizing Mesh...")
            time.sleep(1)
            
            mesh = trimesh.creation.icosphere(radius=1.0)
            
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = int(time.time())
            filename = f"model_{timestamp}.obj"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"# Dummy OBJ file for {filename}")
            
            self.progress_update.emit(100, "Done!")
            self.finished_success.emit(mesh, filepath)
            
        except Exception as e:
            self.finished_error.emit(str(e))

    def stop(self):
        # Allow external stop (force termination if needed, or via flag)
        # Since pipeline.run is blocking subprocess, we might need to terminate thread
        # But properly we should use a flag if possible. 
        # For now, we rely on the main thread terminating this QThread if needed.
        self.terminate()
        self.wait()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Generator App")
        self.resize(1400, 900)
        self.setStyleSheet(DARK_THEME)
        
        self.create_menu_bar()
        
        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Nested Splitter Layout ---
        
        # 1. Main Horizontal Splitter (Sidebar | Center Area | Asset Manager)
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # LEFT PANEL: Sidebar
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sidebar_scroll = QScrollArea()
        self.sidebar_scroll.setWidgetResizable(True)
        self.sidebar = SidebarWidget()
        self.sidebar_scroll.setWidget(self.sidebar)
        
        self.sidebar.generate_signal.connect(self.start_generation)
        self.sidebar.stop_signal.connect(self.stop_generation)
        self.sidebar.export_signal.connect(self.export_mesh)
        
        sidebar_layout.addWidget(self.sidebar_scroll)
        self.main_splitter.addWidget(sidebar_container)
        
        # CENTER PANEL: Vertical Splitter (Viewport | Log)
        self.center_splitter = QSplitter(Qt.Vertical)
        
        # Top: Viewport ONLY
        # We wrap it in a container to easily manage fullscreen reparenting/hiding
        self.viewport_container = QWidget()
        self.viewport_layout = QVBoxLayout(self.viewport_container)
        self.viewport_layout.setContentsMargins(0, 0, 0, 0)
        
        self.viewport = ViewportWidget()
        self.viewport.fullscreen_signal.connect(self.toggle_fullscreen_mode)
        self.viewport_layout.addWidget(self.viewport)
        
        self.center_splitter.addWidget(self.viewport_container)
        
        # Bottom: Log Panel
        self.log_panel = LogWidget()
        self.center_splitter.addWidget(self.log_panel)
        
        self.center_splitter.setSizes([700, 200]) # 70% Viewport, 30% Log
        
        self.main_splitter.addWidget(self.center_splitter)
        
        # RIGHT PANEL: Asset Manager
        self.asset_manager = AssetManagerWidget()
        self.asset_manager.load_mesh_signal.connect(self.load_mesh_from_asset)
        self.main_splitter.addWidget(self.asset_manager)
        
        self.main_splitter.setSizes([300, 800, 300])
        
        main_layout.addWidget(self.main_splitter)
        
        # Status Bar Logic (Since we removed the "Blue Panel", we can use QMainWindow's status bar)
        self.status_bar_label = QLabel("Ready")
        self.status_bar_label.setStyleSheet("padding: 2px 10px; color: #ccc;")
        self.statusBar().addWidget(self.status_bar_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #555; border-radius: 2px; text-align: center; } QProgressBar::chunk { background: #00cc66; }")
        self.statusBar().addPermanentWidget(self.progress_bar)

        self.worker = None
        self.current_mesh = None
        
        # Shortcuts
        self.shortcut_f11 = QShortcut(QKeySequence(Qt.Key_F11), self)
        self.shortcut_f11.activated.connect(self.shortcut_toggle_fullscreen)
        
        self.shortcut_f = QShortcut(QKeySequence(Qt.Key_F), self)
        self.shortcut_f.activated.connect(self.shortcut_toggle_fullscreen)
        
        self.shortcut_esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut_esc.activated.connect(self.exit_fullscreen)
        
        self.log_panel.info("System Initialized.")

    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Project", self.action_new_project)
        file_menu.addAction("Open Image", self.action_open_image)
        file_menu.addSeparator()
        file_menu.addAction("Clean Cache", self.action_clean_cache)
        file_menu.addSeparator()
        file_menu.addAction("Export Mesh", self.action_export_mesh)
        file_menu.addAction("Exit", self.close)
        
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo", self.action_undo)
        edit_menu.addAction("Redo", self.action_redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Clear Outputs", self.action_clear_inputs)
        
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Toggle Fullscreen", self.shortcut_toggle_fullscreen)
        view_menu.addAction("Reset Camera", self.action_reset_camera)
        
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.action_about)

    # --- Actions ---
    def action_new_project(self): self.log_panel.info("New Project.")
    def action_open_image(self): self.log_panel.info("Open Image.")
    def action_clean_cache(self):
        reply = QMessageBox.question(self, "Clean Cache", 
                                     "Delete all generated files in output/ and assets/?\nThis cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            from backend.manager import BackendManager
            count, mb = BackendManager().clear_output_cache()
            msg = f"Cleaned {count} files ({mb:.2f} MB freed)."
            self.log_panel.success(msg)
            self.status_bar_label.setText("Cache Cleaned")
            
            # Additional info for HF cache
            self.log_panel.info("Tip: To clear model download cache, manually delete ~/.cache/huggingface") 
            
            # Clear Asset Manager list visually
            self.asset_manager.list_widget.clear()

    def action_export_mesh(self): self.export_mesh()
    def action_undo(self): self.log_panel.info("Undo.")
    def action_redo(self): self.log_panel.info("Redo.")
    def action_clear_inputs(self): self.sidebar.clear_inputs()
    def action_toggle_wireframe(self): self.log_panel.info("Toggle Wireframe.")
    def action_reset_camera(self): 
        self.viewport.view_widget.setCameraPosition(distance=40)
        self.log_panel.info("Camera reset.")
    def action_about(self): QMessageBox.about(self, "About", "3D Generator v1.0")

    # --- Fullscreen Logic ---
    def shortcut_toggle_fullscreen(self):
        # Trigger from shortcut calls the same logic
        self.toggle_fullscreen_mode(not self.viewport.is_fullscreen)

    def exit_fullscreen(self):
        if self.viewport.is_fullscreen:
            self.toggle_fullscreen_mode(False)

    def toggle_fullscreen_mode(self, enable):
        """
        Handles the logic to switch between embedded and fullscreen.
        Hide all surrounding widgets to achieve 'True Fullscreen'.
        """
        
        # Widgets to hide/show
        # 1. Sidebar Container (Left panel of main splitter)
        sidebar_container = self.main_splitter.widget(0)
        # 2. Asset Manager (Right panel of main splitter)
        asset_manager = self.main_splitter.widget(2) # Index might shift if hidden? No, widgets stay.
        # 3. Log Panel (Bottom of center splitter)
        log_panel = self.center_splitter.widget(1)
        
        if enable:
            sidebar_container.hide()
            asset_manager.hide()
            log_panel.hide()
            
            self.statusBar().hide()
            self.menuBar().hide()
            
            # Maximize viewport in the main layout (it's already central effectively)
            self.showFullScreen()
            
            self.viewport.set_fullscreen_state(True)
            self.log_panel.info("Entered Fullscreen Mode.")
        else:
            self.showNormal()
            
            sidebar_container.show()
            asset_manager.show()
            log_panel.show()
            
            self.statusBar().show()
            self.menuBar().show()
            
            self.viewport.set_fullscreen_state(False)
            self.log_panel.info("Exited Fullscreen Mode.")
            
            # Force layout update/repaint to fix any visual artifacts
            self.main_splitter.refresh()

    def stop_generation(self):
        if self.worker and self.worker.isRunning():
            self.log_panel.warning("Stopping generation...")
            self.worker.stop()
            self.worker = None
            
        from backend.manager import BackendManager
        BackendManager().request_stop()
        
        self.sidebar.set_generating_state(False)
        self.status_bar_label.setText("Stopped")
        self.progress_bar.setValue(0)
        self.log_panel.info("Generation stopped by user.")

    # --- Generation Logic ---
    def start_generation(self, prompt, image_path):
        has_image = (isinstance(image_path, str) and image_path) or (isinstance(image_path, dict) and image_path)
        if not prompt and not has_image:
            QMessageBox.warning(self, "Input Error", "Provide prompt or image.")
            return
            
        self.progress_bar.setValue(0)
        self.status_bar_label.setText("Processing...")
        self.log_panel.info(f"Starting generation... Prompt: {prompt}")
        self.sidebar.set_generating_state(True)
        
        model = self.sidebar.model_combo.currentText()
        low_vram = self.sidebar.low_vram_check.isChecked()
        
        self.worker = GenerationWorker(prompt, image_path, model, low_vram)
        self.worker.progress_update.connect(self.on_progress)
        self.worker.finished_success.connect(self.on_generation_success)
        self.worker.finished_error.connect(self.on_generation_error)
        self.worker.start()

    def on_progress(self, value, text):
        if value >= 0:
            self.progress_bar.setValue(value)
        
        self.status_bar_label.setText(text)
        
        # If it's a log message (value -1) or significant progress
        if value == -1:
             self.log_panel.info(f"[Core] {text}")
        elif value % 10 == 0: 
             self.log_panel.info(f"Progress: {value}% - {text}")

    def on_generation_success(self, mesh, file_path):
        self.status_bar_label.setText("Done")
        self.log_panel.success("Generation Complete.")
        self.sidebar.set_generating_state(False)
        self.current_mesh = mesh
        self.viewport.update_mesh(mesh)
        
        # Take Screenshot for Thumbnail
        import os
        # Use assets/thumbnails as requested
        thumb_dir = os.path.join("assets", "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        filename = os.path.basename(file_path).replace(".obj", ".png").replace(".glb", ".png")
        thumb_path = os.path.join(thumb_dir, filename)
        
        # Wait a brief moment for render to update (OpenGL can be async)
        QThread.msleep(100) 
        self.viewport.take_screenshot(thumb_path)
        
        self.asset_manager.add_asset(file_path, thumb_path)

    def on_generation_error(self, error_msg):
        self.status_bar_label.setText("Error")
        self.log_panel.error(error_msg)
        self.sidebar.set_generating_state(False)
        QMessageBox.critical(self, "Error", error_msg)

    def load_mesh_from_asset(self, file_path):
        self.log_panel.info(f"Loading {file_path}")
        try:
             # mock load
            import trimesh
            mesh = trimesh.creation.icosphere(radius=1.0)
            self.current_mesh = mesh
            self.viewport.update_mesh(mesh)
        except Exception as e:
            self.log_panel.error(f"Load failed: {e}")

    def export_mesh(self):
        if not self.current_mesh:
            return
        fname, _ = QFileDialog.getSaveFileName(self, "Save", "model.obj", "OBJ (*.obj);;GLB (*.glb)")
        if fname:
            try:
                self.current_mesh.export(fname)
                self.log_panel.success(f"Saved to {fname}")
            except Exception as e:
                self.log_panel.error(f"Save failed: {e}")
