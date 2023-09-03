from PyQt6.QtCore import (
    pyqtSignal,
    QThreadPool
)
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QProgressBar ,
    QFileDialog 
)
import os
import sys
import shutil
from PyQt6.QtWidgets import QWidget
from custom_widgets.image_viewer import ImageViewer
from .file_worker import Worker

class FileMenu(QWidget):

    generation_signal = pyqtSignal()

    def __init__(self, tabs):
        super().__init__()
        self.threadpool = QThreadPool()
        self.tabs = tabs
        self.filename = ""
        self.layout = QVBoxLayout()

        #file button
        self.file_label = QLabel("File: ")
        self.layout.addWidget(self.file_label)

        self.file_button = QPushButton("Open File")
        self.file_button.clicked.connect(self.get_filename)
        self.layout.addWidget(self.file_button)

        #process button
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process)
        self.layout.addWidget(self.process_button)
        self.process_button.hide()

        #image preview
        basedir = os.path.abspath(os.path.dirname(__file__))
        self.image_preview = ImageViewer()
        self.layout.addWidget(self.image_preview)
        self.image_preview.hide()

        #general progress bar
        self.progress_label = QLabel("Progress")
        self.layout.addWidget(self.progress_label)
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 100)
        self.layout.addWidget(self.loading_bar)
        self.progress_label.hide()
        self.loading_bar.hide()

        #interrupt button
        self.interrupt_button = QPushButton("Interrupt")
        self.layout.addWidget(self.interrupt_button)
        self.interrupt_button.hide()

        #exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit)
        self.layout.addWidget(self.exit_button)

        self.setLayout(self.layout)

    def get_filename(self):
        """Opens a file dialog and returns the selected file path of a video."""
        initial_dir =""
        caption=''
        self.filename, _ = QFileDialog.getOpenFileName(self, caption=caption, directory=initial_dir, filter="*")
        self.file_label.setText("File: " + self.filename.split("/")[-1])
        if self.filename != "":
            self.show_widgets()

    def show_widgets(self):
        """Shows the widgets."""
        self.process_button.show()
        self.progress_label.show()
        self.loading_bar.show()
        self.interrupt_button.show()
        self.image_preview.show()
        
    
    def process(self):
        """Processes the video."""
        if self.filename == "":
            return
        self.clean_up()
        self.worker = Worker(self.filename)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.handle_finished)
        self.interrupt_button.clicked.connect(self.interrupt)

        # Execute
        self.threadpool.start(self.worker)

    def update_progress(self, string, progress):
        """Updates the progress bar."""
        self.progress_label.setText("Progress: " + string)
        self.loading_bar.setValue(progress)
        self.image_preview.update_image(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","VideoFiles","temp.png"))

    def handle_finished(self):
        """Handles the finished signal."""
        self.loading_bar.setValue(100)
        self.generation_signal.emit()
        self.tabs.setCurrentIndex(1)

    def interrupt(self):
        """Interrupts the process."""
        self.worker.kill()    
    
    def exit(self):
        """Exits the program."""
        self.clean_up()
        sys.exit()

    def clean_up(self):
        """Cleans up the program."""
        basedir = os.path.dirname(os.path.abspath(__file__))
        basedir = os.path.join(basedir,"..", "VideoFiles")
        if os.path.isdir(basedir):
            shutil.rmtree(basedir)

    



