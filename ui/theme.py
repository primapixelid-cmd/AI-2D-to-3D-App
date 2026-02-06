
DARK_THEME = """
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

QTabBar::tab {
    background: #2d2d2d;
    color: #b0b0b0;
    padding: 8px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background: #3d3d3d;
    color: #ffffff;
    border-bottom: 2px solid #007acc;
}

QPushButton {
    background-color: #007acc;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #0098ff;
}

QPushButton:pressed {
    background-color: #005c99;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    padding: 4px;
    border-radius: 4px;
}

QComboBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    padding: 4px;
    border-radius: 4px;
}

QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #007acc;
}

QGroupBox {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    margin-top: 1em;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}

/* Splitter & ScrollArea */
QSplitter::handle {
    background-color: #3d3d3d;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #007acc;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #2d2d2d;
    width: 10px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #555;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Menu Bar */
QMenuBar {
    background-color: #252525;
    color: #e0e0e0;
    border-bottom: 1px solid #3d3d3d;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 12px;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenu {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
}

QMenu::item {
    padding: 6px 24px;
}

QMenu::item:selected {
    background-color: #007acc;
}

/* Drag & Drop Styles */
QLabel#DropZone {
    border: 2px dashed #555;
    border-radius: 8px;
    background-color: #252525;
    color: #aaa;
    padding: 10px;
}

QLabel#DropZone:hover {
    border-color: #007acc;
    background-color: #2a2a2a;
    color: #fff;
}
"""
