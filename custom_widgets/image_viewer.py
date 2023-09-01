from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)
    
    def update_image(self, image_path):
        self.image_path = image_path
        self.image_label.setPixmap(QPixmap(self.image_path).scaledToWidth(300))
        
