from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal
import pyqtgraph.opengl as gl
import numpy as np

class ViewportWidget(QWidget):
    fullscreen_signal = Signal(bool) # emitted when fullscreen is toggled

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_fullscreen = False
        
        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize OpenGL View Widget
        self.view_widget = gl.GLViewWidget()
        self.view_widget.setCameraPosition(distance=40)
        self.view_widget.setBackgroundColor('#1e1e1e')
        
        # Add a grid for reference
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        self.view_widget.addItem(grid)
        
        self.layout.addWidget(self.view_widget)
        
        # Fullscreen Button (Overlay logic in resizeEvent)
        self.fs_btn = QPushButton("⛶", self)
        self.fs_btn.setToolTip("Toggle Fullscreen (F11)")
        self.fs_btn.setFixedSize(80, 40)
        self.fs_btn.setCursor(Qt.PointingHandCursor)
        self.fs_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(45, 45, 45, 200);
                color: #e0e0e0;
                border: 1px solid #555;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #007acc;
                border: 1px solid #007acc;
                color: white;
            }
        """)
        self.fs_btn.clicked.connect(self.request_toggle)
        self.fs_btn.show()
        
        self.current_mesh_item = None

    def take_screenshot(self, save_path):
        """Captures the current viewport and saves to file."""
        try:
            image = self.view_widget.grabFrameBuffer()
            image.save(save_path)
            print(f"Screenshot saved to {save_path}")
            return True
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return False

    def resizeEvent(self, event):
        # Position button at top right
        m = 10 # margin
        self.fs_btn.move(self.width() - self.fs_btn.width() - m, m)
        super().resizeEvent(event)
        
    def request_toggle(self):
        # We verify state but let the main window handle the true toggle logic
        self.fullscreen_signal.emit(not self.is_fullscreen)

    def set_fullscreen_state(self, is_fullscreen):
        """Called by MainWindow to update button state logic"""
        self.is_fullscreen = is_fullscreen
        if self.is_fullscreen:
            self.fs_btn.setText("BACK")
            self.fs_btn.setToolTip("Exit Fullscreen (Esc)")
        else:
            self.fs_btn.setText("⛶")
            self.fs_btn.setToolTip("Toggle Fullscreen (F11)")

    def update_mesh(self, mesh_data):
        """
        Update the 3D view with new mesh data.
        """
        if self.current_mesh_item:
            self.view_widget.removeItem(self.current_mesh_item)
            self.current_mesh_item = None
            
        if mesh_data is None:
            return

        try:
            verts = mesh_data.vertices
            faces = mesh_data.faces
            
            # Simple uniform color
            colors = np.ones((verts.shape[0], 4))
            colors[:, 0] = 0.5
            colors[:, 1] = 0.5
            colors[:, 2] = 0.8
            colors[:, 3] = 1.0
            
            mesh_item = gl.GLMeshItem(vertexes=verts, faces=faces, faceColors=colors, smooth=True, shader='balloon')
            self.view_widget.addItem(mesh_item)
            self.current_mesh_item = mesh_item
            
        except Exception as e:
            print(f"Error updating mesh: {e}")
