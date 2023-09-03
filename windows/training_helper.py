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
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget

class TrainingHelper(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

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

        #image
        self.image_layout = QHBoxLayout()
        self.image_label = QLabel("Image folder: ")
        self.image_layout.addWidget(self.image_label)

        self.image_input=QLineEdit()
        #self.image_input.textChanged.connect(self.image_input_changed)
        self.image_layout.addWidget(self.image_input)

        self.image_button = QPushButton("Open Folder")
        self.image_button.clicked.connect(self.get_image_folder)
        self.image_layout.addWidget(self.image_button)

        self.layout.addLayout(self.image_layout)

        #log
        self.log_layout = QHBoxLayout()
        self.log_label = QLabel("Log folder: ")
        self.log_layout.addWidget(self.log_label)

        self.log_input=QLineEdit()
        #self.log_input.textChanged.connect(self.log_input_changed)
        self.log_layout.addWidget(self.log_input)

        self.log_button = QPushButton("Open Folder")
        self.log_button.clicked.connect(self.get_log_folder)
        self.log_layout.addWidget(self.log_button)

        self.layout.addLayout(self.log_layout)

        #model
        self.model_layout = QHBoxLayout()
        self.model_label = QLabel("Model folder: ")
        self.model_layout.addWidget(self.model_label)

        self.model_input=QLineEdit()
        #self.model_input.textChanged.connect(self.model_input_changed)
        self.model_layout.addWidget(self.model_input)

        self.model_button = QPushButton("Open Folder")
        self.model_button.clicked.connect(self.get_model_folder)
        self.model_layout.addWidget(self.model_button)

        self.layout.addLayout(self.model_layout)

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

        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute)
        self.execute_button.setFont((QFont("Arial", 20)))
        self.button_layout.addWidget(self.execute_button)

        self.execute_button.setFixedHeight(60)
        self.interrupt_button.setFixedHeight(60)
        self.process_button.setFixedHeight(60)
        self.execute_button.setStyleSheet("background-color: green")
        self.process_button.setStyleSheet("background-color: orange")
        self.interrupt_button.setStyleSheet("background-color: red")

        self.layout.addLayout(self.button_layout)


        self.setLayout(self.layout)

    def get_video_file(self):
        """Opens a file dialog and returns the selected file path of a video."""
        initial_dir =""
        caption=''
        filename, _ = QFileDialog.getOpenFileName(self, caption=caption, directory=initial_dir, filter="*")
        self.video_input.setText(filename)

    
    def get_image_folder(self):
        """Opens a file dialog and returns the selected file path of a video."""
        initial_dir =""
        caption=''
        folder= QFileDialog.getExistingDirectory(self, caption=caption, directory=initial_dir)
        self.image_input.setText(folder)

    def get_log_folder(self):
        """Opens a file dialog and returns the selected file path of a video."""
        initial_dir =""
        caption=''
        folder= QFileDialog.getExistingDirectory(self, caption=caption, directory=initial_dir)
        self.log_input.setText(folder)
    
    def get_model_folder(self):
        """Opens a file dialog and returns the selected file path of a video."""
        initial_dir =""
        caption=''
        folder= QFileDialog.getExistingDirectory(self, caption=caption, directory=initial_dir)
        self.model_input.setText(folder)

    def update_blur_label(self):
        self.blur_label.setText("blur: "+str(self.blur_slider.value()))
    
    def interrupt(self):
        pass

    def process(self):
        pass

    def execute(self):
        pass


        