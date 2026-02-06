from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
import datetime

class LogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setObjectName("LogWidget")
        self.setStyleSheet("""
            QTextEdit#LogWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)

    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color = "#d4d4d4"
        if level == "WARNING":
            color = "#de9e48"
        elif level == "ERROR":
            color = "#e51400"
        elif level == "SUCCESS":
            color = "#00cc66"
            
        formatted_message = f'<span style="color:#666;">[{timestamp}]</span> <span style="color:{color};">[{level}] {message}</span>'
        self.append(formatted_message)
        
    def info(self, message):
        self.log(message, "INFO")
        
    def warning(self, message):
        self.log(message, "WARNING")
        
    def error(self, message):
        self.log(message, "ERROR")
        
    def success(self, message):
        self.log(message, "SUCCESS")
