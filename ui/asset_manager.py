import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QDesktopServices, QIcon, QPixmap
from PySide6.QtCore import QUrl, QSize

class AssetManagerWidget(QWidget):
    load_mesh_signal = Signal(str) # Path to mesh file

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Asset Manager")
        header.setStyleSheet("font-weight: bold; padding: 5px; background-color: #2d2d2d;")
        self.layout.addWidget(header)
        
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.list_widget.setIconSize(QSize(100, 100)) # Larger icons
        self.list_widget.setSpacing(5)
        self.layout.addWidget(self.list_widget)

    def add_asset_item(self, file_path, thumb_path=None):
        """Adds a file to the list with metadata and optional thumbnail."""
        if not os.path.exists(file_path):
            return

        file_name = os.path.basename(file_path)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        size_bytes = os.path.getsize(file_path)
        size_str = f"{size_bytes / 1024:.1f} KB"
        
        # Multiline text: Name on top, details below
        display_text = f"{file_name}\n{timestamp} | {size_str}"
        
        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, file_path) # Store full path
        
        # Handle Thumbnail
        icon_path = "assets/default_3d_icon.png" # Default
        if thumb_path and os.path.exists(thumb_path):
            icon_path = thumb_path
            
        if os.path.exists(icon_path):
             # Ensure aspect ratio is handled if needed, but QIcon handles it reasonably well usually
             item.setIcon(QIcon(icon_path))
        else:
             # Fallback if no default icon exists either
             pass
             
        self.list_widget.addItem(item)
        self.list_widget.scrollToBottom()

    def add_asset(self, file_path, thumb_path=None):
        # Alias for backward compatibility if needed, or just use add_asset_item
        self.add_asset_item(file_path, thumb_path)

    def on_item_double_clicked(self, item):
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.load_mesh_signal.emit(file_path)
        else:
            QMessageBox.warning(self, "Error", "File not found!")

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        menu = QMenu()
        open_folder_action = QAction("Open in Folder", self)
        delete_action = QAction("Delete", self)
        
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        
        if action == open_folder_action:
            file_path = item.data(Qt.UserRole)
            folder_path = os.path.dirname(file_path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            
        elif action == delete_action:
            file_path = item.data(Qt.UserRole)
            reply = QMessageBox.question(self, "Delete Asset", f"Are you sure you want to delete {os.path.basename(file_path)}?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    os.remove(file_path)
                    self.list_widget.takeItem(self.list_widget.row(item))
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not delete file: {e}")
