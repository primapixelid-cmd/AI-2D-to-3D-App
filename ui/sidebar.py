from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QCheckBox, QListWidget, 
    QFileDialog, QGroupBox, QTabWidget, QGridLayout, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap

class ImageDropWidget(QLabel):
    image_dropped = Signal(str, str) # tag, file_path

    def __init__(self, tag, text="Drop Image Here", parent=None):
        super().__init__(parent)
        self.tag = tag
        self.setObjectName("DropZone")
        self.setText(f"{text}\n({tag})")
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self.file_path = None
        self.setStyleSheet("QLabel#DropZone { border: 2px dashed #555; border-radius: 8px; background-color: #252525; color: #aaa; }")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("QLabel#DropZone { border: 2px dashed #007acc; background-color: #2a2a2a; color: #fff; }")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("QLabel#DropZone { border: 2px dashed #555; border-radius: 8px; background-color: #252525; color: #aaa; }")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("QLabel#DropZone { border: 2px dashed #555; border-radius: 8px; background-color: #252525; color: #aaa; }")
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                self.set_image(file_path)
                event.acceptProposedAction()
            else:
                event.ignore()

    def set_image(self, file_path):
        self.file_path = file_path
        pixmap = QPixmap(file_path)
        self.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setStyleSheet("QLabel#DropZone { border: 2px solid #00cc66; background-color: #2a2a2a; color: #fff; }")
        self.image_dropped.emit(self.tag, file_path)
        
    def reset(self):
        self.file_path = None
        self.clear()
        self.setText(f"Drop Image Here\n({self.tag})")
        self.setStyleSheet("QLabel#DropZone { border: 2px dashed #555; border-radius: 8px; background-color: #252525; color: #aaa; }")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
            if file_name:
                self.set_image(file_name)


class SidebarWidget(QWidget):
    generate_signal = Signal(str, object) # text_prompt, image_data (str or dict)
    stop_signal = Signal()
    export_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_generating = False
        self.layout = QVBoxLayout(self)
        
        # --- Settings Section ---
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Hunyuan3D-V2", "InstantMesh"])
        settings_layout.addWidget(QLabel("Model:"))
        settings_layout.addWidget(self.model_combo)
        
        self.low_vram_check = QCheckBox("Low VRAM Mode (FP16)")
        self.low_vram_check.setChecked(True)
        settings_layout.addWidget(self.low_vram_check)
        
        settings_group.setLayout(settings_layout)
        self.layout.addWidget(settings_group)
        
        # --- Input Section ---
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout()
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter text prompt (optional)...")
        self.prompt_input.setMaximumHeight(60)
        input_layout.addWidget(QLabel("Text Prompt:"))
        input_layout.addWidget(self.prompt_input)
        
        # Clear Button Header
        clear_layout = QHBoxLayout()
        clear_layout.addStretch()
        self.clear_btn = QPushButton("Clear Input")
        self.clear_btn.setFixedSize(80, 25)
        self.clear_btn.setStyleSheet("background-color: #d9534f; font-size: 11px; padding: 2px;")
        self.clear_btn.clicked.connect(self.clear_inputs)
        clear_layout.addWidget(self.clear_btn)
        input_layout.addLayout(clear_layout)
        
        # Tabs for Single vs Multi View
        self.input_tabs = QTabWidget()
        
        # Tab 1: Single Image
        self.single_tab = QWidget()
        single_layout = QVBoxLayout(self.single_tab)
        self.single_drop = ImageDropWidget("Single")
        single_layout.addWidget(self.single_drop)
        self.input_tabs.addTab(self.single_tab, "Single Image")
        
        # Tab 2: Multi View
        self.multi_tab = QWidget()
        multi_layout = QGridLayout(self.multi_tab)
        
        self.multi_drops = {}
        views = [
            ("Front", 0, 1), ("Back", 2, 1),
            ("Left", 1, 0), ("Right", 1, 2),
            ("Top", 0, 0), ("Bottom", 2, 0) # Adjusted layout for visual logic
        ]
        
        # Let's use a simpler 2x3 grid:
        # Front, Back, Left
        # Right, Top, Bottom
        views_simple = [
            ("Front", 0, 0), ("Back", 0, 1), ("Left", 0, 2),
            ("Right", 1, 0), ("Top", 1, 1), ("Bottom", 1, 2)
        ]

        for name, r, c in views_simple:
            drop = ImageDropWidget(name, name)
            # drop.setMinimumHeight(60) # Smaller for grid
            multi_layout.addWidget(drop, r, c)
            self.multi_drops[name] = drop
            
        self.input_tabs.addTab(self.multi_tab, "Multi-View (6)")
        
        input_layout.addWidget(self.input_tabs)
        
        self.generate_btn = QPushButton("Generate 3D")
        self.generate_btn.setStyleSheet("background-color: #00cc66; font-weight: bold; padding: 8px;")
        self.generate_btn.clicked.connect(self.on_generate_click)
        input_layout.addWidget(self.generate_btn)
        
        input_group.setLayout(input_layout)
        self.layout.addWidget(input_group)
        
        # --- History Section ---
        history_group = QGroupBox("History")
        history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        history_group.setLayout(history_layout)
        self.layout.addWidget(history_group)
        
        # --- Export Section ---
        self.export_btn = QPushButton("Export Mesh (.obj)")
        self.export_btn.clicked.connect(self.export_signal.emit)
        self.layout.addWidget(self.export_btn)
        
        self.layout.addStretch()

    def on_generate_click(self):
        if self.is_generating:
             # Stop logic
             self.stop_signal.emit()
             # We don't reset immediately, we wait for MainWindow to confirm stop or worker finish
             # But for responsiveness:
             self.generate_btn.setText("Stopping...")
             self.generate_btn.setEnabled(False) # Prevent double click
        else:
             self.prepare_generation()

    def set_generating_state(self, is_running):
        self.is_generating = is_running
        self.generate_btn.setEnabled(True)
        if is_running:
            self.generate_btn.setText("Stop Generation")
            self.generate_btn.setStyleSheet("background-color: #d9534f; font-weight: bold; padding: 8px;")
        else:
            self.generate_btn.setText("Generate 3D")
            self.generate_btn.setStyleSheet("background-color: #00cc66; font-weight: bold; padding: 8px;")

    def prepare_generation(self):
        prompt = self.prompt_input.toPlainText()
        
        current_tab_idx = self.input_tabs.currentIndex()
        image_data = None
        
        if current_tab_idx == 0: # Single Image
            if self.single_drop.file_path:
                image_data = self.single_drop.file_path
        else: # Multi-View
            image_data = {}
            for tag, widget in self.multi_drops.items():
                if widget.file_path:
                    image_data[tag] = widget.file_path
            
            # If empty, set to None
            if not image_data:
                image_data = None
 
        # Only emit if valid
        has_input = prompt or image_data
        if has_input:
             self.generate_signal.emit(prompt, image_data)
        else:
             QMessageBox.warning(self, "Input Error", "Please provide a text prompt or an image.")

    def clear_inputs(self):
        self.single_drop.reset()
        for widget in self.multi_drops.values():
            widget.reset()
        self.prompt_input.clear()
        
        # Optional user feedback
        parent_window = self.window()
        if parent_window and hasattr(parent_window, "status_label"):
            parent_window.status_label.setText("Inputs cleared.")

    def add_to_history(self, item_name):
        self.history_list.addItem(item_name)
