from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QSlider,
    QWidget,
    QProgressBar ,
    QFileDialog,
    QLineEdit
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QThreadPool
)
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget

from .training_worker import Worker

class TrainingHelper(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.threadpool = QThreadPool()


        #video
        self.video_layout = QHBoxLayout()
        self.video_label = QLabel("Video file: ")
        self.video_layout.addWidget(self.video_label)

        self.video_input=QLineEdit()
        #self.video_input.textChanged.connect(self.video_input_changed)
        self.video_layout.addWidget(self.video_input)

        self.video_button = QPushButton("Open file")
        self.video_button.clicked.connect(self.get_video_file)
        self.video_layout.addWidget(self.video_button)

        self.layout.addLayout(self.video_layout)

       

        #blurr threshold
        self.blur_layout = QHBoxLayout()
        self.blur_label= QLabel("blur: 40")
        self.blur_layout.addWidget(self.blur_label)
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_layout.addWidget(self.blur_slider)
        self.blur_slider.setRange(0, 100)
        self.blur_slider.setValue(40)
        self.blur_slider.valueChanged.connect(self.update_blur_label)
        self.layout.addLayout(self.blur_layout)

        #model name
        self.name_layout = QHBoxLayout()
        self.training_name_label = QLabel("Training name: ")
        self.name_layout.addWidget(self.training_name_label)
        self.training_name_input=QLineEdit()
        self.name_layout.addWidget(self.training_name_input)

        self.output_name_label = QLabel("Output name: ")
        self.name_layout.addWidget(self.output_name_label)
        self.output_name_input=QLineEdit()
        self.name_layout.addWidget(self.output_name_input)



        self.layout.addLayout(self.name_layout)


        #progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        #self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Progress: ")
        self.layout.addWidget(self.progress_label)

        #execute and interrupt buttons
        self.button_layout = QHBoxLayout()
        self.interrupt_button = QPushButton("Interrupt")
        self.interrupt_button.clicked.connect(self.interrupt)
        self.interrupt_button.setFont((QFont("Arial", 20)))
        self.button_layout.addWidget(self.interrupt_button)

        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process)
        self.process_button.setFont((QFont("Arial", 20)))
        self.button_layout.addWidget(self.process_button)

        self.interrupt_button.setFixedHeight(60)
        self.process_button.setFixedHeight(60)
        self.process_button.setStyleSheet("background-color: green")
        self.interrupt_button.setStyleSheet("background-color: red")
        self.interrupt_button.setEnabled(False)

        self.layout.addLayout(self.button_layout)


        self.setLayout(self.layout)

    def get_video_file(self):
        """Opens a file dialog and returns the selected file path of a video."""
        initial_dir =""
        caption=''
        filename, _ = QFileDialog.getOpenFileName(self, caption=caption, directory=initial_dir, filter="*")
        self.video_input.setText(filename)

    def update_blur_label(self):
        self.blur_label.setText("blur: "+str(self.blur_slider.value()))
    
    def interrupt(self):
        """Interrupt the process"""
        self.worker.kill()

    def process(self):
        """Generate all the images and save them to a folder"""
        self.process_button.setEnabled(False)
        self.interrupt_button.setEnabled(True)
        self.worker = Worker(
            self.video_input.text(),
            self.training_name_input.text(),
            self.output_name_input.text(),
            self.blur_slider.value(),
            )
        
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.process_finished)
        self.worker.signals.error.connect(self.process_finished)

    
        # Execute
        self.threadpool.start(self.worker)

    def update_progress(self, str, progress):
        self.progress_label.setText(f"Progress: {str}")
        self.progress_bar.setValue(progress)

    def process_finished(self):
        self.progress_label.setText("Finished!")
        self.progress_bar.setValue(0)
        self.interrupt_button.setEnabled(False)
        self.process_button.setEnabled(True)
        



        