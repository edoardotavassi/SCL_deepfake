import sys
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QPushButton,
    QStackedLayout,
    QLineEdit,
    QVBoxLayout,
    QSlider,
    QWidget,
    QTextEdit,
    QProgressBar
    
)

import os
from PyQt6.QtGui import QColor, QPalette, QPixmap,QFont
from PyQt6.QtWidgets import QWidget

from windows.file_menu import FileMenu
from windows.generation_window import GenerationWindow
from windows.video_player import VideoPlayer
from windows.training_helper import TrainingHelper


def dark_palette(app):
    """Create a dark palette for the application"""
    darkPalette = QPalette()
    darkPalette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))

    darkPalette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)

    darkPalette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))

    darkPalette.setColor(QPalette.ColorRole.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.ColorRole.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))

    darkPalette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)

    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))

    darkPalette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

    darkPalette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))

    darkPalette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))

    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))

    darkPalette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))

    app.setPalette(darkPalette)


class Color(QWidget):
    def __init__(self, color, height=0, width=0):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)
        if height:
            self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)            


basedir = os.path.dirname(__file__)


class MainWindow(QMainWindow):
    """Main Window of the application that contains the tabs"""
    def __init__(self):
        super().__init__()
        #defining the window
        self.setWindowTitle("SD DeepFakes")
        self.setFixedSize(600, 900)


        #defining the tabs
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(True)

        self.file_menu = FileMenu(tabs)
        self.generation_window = GenerationWindow(tabs)
        self.video_player = VideoPlayer()

        tabs.addTab(self.file_menu, "File Menu")
        tabs.addTab(self.generation_window, "Diffusion")
        tabs.addTab(self.video_player, "Video Export")
        tabs.addTab(TrainingHelper(), "Training Helper")

        self.generation_window.video_output_signal.connect(self.video_player.update_video)
        self.file_menu.generation_signal.connect(self.generation_window.handle_file_menu_signal)

        

        

        self.setCentralWidget(tabs)



# Main
app = QApplication(sys.argv)
# set dark theme and style
dark_palette(app)
app.setStyle("Fusion")

window = MainWindow()
window.show()
app.exec()


        