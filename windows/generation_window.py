from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QThreadPool
)
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QSlider,
    QWidget,
    QTextEdit,
    QProgressBar,
    QToolButton  
)

import os
from PyQt6.QtGui import QFont
from custom_widgets.image_viewer import ImageViewer
from .generation_worker import Worker


class GenerationWindow(QWidget):

    video_output_signal = pyqtSignal()

    def __init__(self, tabs):
        super().__init__()
        self.tabs = tabs
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.setWindowTitle("Generation")

        #signal for when the video is finished
        # 

        self.threadpool = QThreadPool()
        self.frame_number = 0
        
        self.layout = QVBoxLayout()

        # next button and back button
        self.layout_image = QHBoxLayout()
        self.back_button = QToolButton()
        self.back_button.setArrowType(Qt.ArrowType.LeftArrow)
        self.back_button.setFixedSize(50, 50)
        self.back_button.clicked.connect(self.back)

        self.next_button = QToolButton()
        self.next_button.setArrowType(Qt.ArrowType.RightArrow)
        self.next_button.setFixedSize(50, 50)
        self.next_button.clicked.connect(self.next)

        self.layout_image.addWidget(self.back_button)

        # image viewer
        self.image_widget = ImageViewer()
        self.layout_image.addWidget(self.image_widget)

        self.layout_image.addWidget(self.next_button)
        self.layout.addLayout(self.layout_image)

        #general progress bar
        self.layout.addWidget(QLabel("Total Progress"))
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 100)
        self.layout.addWidget(self.loading_bar)

        #progress bar for each step
        self.image_progress_label = QLabel("Image Progress")
        self.layout.addWidget(self.image_progress_label)
        self.image_bar = QProgressBar()
        self.image_bar.setRange(0, 100)
        self.layout.addWidget(self.image_bar)

        # prompt
        self.prompt_label = QLabel("Prompt")
        self.layout.addWidget(self.prompt_label)
        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("Enter your prompt here")
        self.prompt.setFixedHeight(100)
        self.prompt.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.prompt.setTabChangesFocus(True)
        self.layout.addWidget(self.prompt) 

        #negative prompt
        self.negative_prompt_label = QLabel("Negative Prompt")
        self.layout.addWidget(self.negative_prompt_label)
        self.negative_prompt = QTextEdit()
        self.negative_prompt.setPlaceholderText("Enter your negative prompt here")
        self.negative_prompt.setFixedHeight(100)
        self.negative_prompt.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.negative_prompt.setTabChangesFocus(True)
        self.layout.addWidget(self.negative_prompt)

        #steps slider
        self.steps_label= QLabel("Steps: 12")
        self.layout.addWidget(self.steps_label)
        self.steps_slider = QSlider(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.steps_slider)
        self.steps_slider.setRange(0, 150)
        self.steps_slider.setValue(12)
        self.steps_slider.valueChanged.connect(self.update_steps_label)

        #Denoising slider
        self.denoise_label= QLabel("Denoising: 0.3")
        self.layout.addWidget(self.denoise_label)
        self.denoising_slider = QSlider(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.denoising_slider)
        self.denoising_slider.setRange(0, 10)
        self.denoising_slider.setValue(3)
        self.denoising_slider.valueChanged.connect(self.update_denoise_label)

        #CFG slider
        self.cfg_label= QLabel("CFG: 7")
        self.layout.addWidget(self.cfg_label)
        self.cfg_slider = QSlider(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.cfg_slider)
        self.cfg_slider.setRange(0, 10)
        self.cfg_slider.setValue(7)
        self.cfg_slider.valueChanged.connect(self.update_cfg_label)

        #Generate button and interrupt button
        self.generate_button = QPushButton("Generate")
        self.test_button = QPushButton("Test")
        self.interrupt_button = QPushButton("Interrupt")
        self.generate_button.setFixedHeight(60)
        self.test_button.setFixedHeight(60)
        self.interrupt_button.setFixedHeight(60)
        self.generate_button.setFont(QFont("Arial", 20))
        self.test_button.setFont(QFont("Arial", 20))
        self.interrupt_button.setFont(QFont("Arial", 20))

        self.generate_button.setStyleSheet("background-color: green")
        self.test_button.setStyleSheet("background-color: orange")
        self.interrupt_button.setStyleSheet("background-color: red")

        self.test_button.clicked.connect(self.test)
        self.generate_button.clicked.connect(self.generate)
        self.interrupt_button.clicked.connect(self.interrupt)
    
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.interrupt_button)
        self.button_layout.addWidget(self.test_button)
        self.button_layout.addWidget(self.generate_button)

        self.layout.addLayout(self.button_layout)
        
        self.setLayout(self.layout)

        self.deactivate_all_interrupt()
    
    def back(self):
        if self.frame_number > 0:
            self.frame_number -= 1
            self.image_widget.update_image(os.path.join(self.basedir, "..", "VideoFiles", "cropped_frames", f"frame{self.frame_number}.png"))
        
    def next(self):
        if self.frame_number < 54:
            self.frame_number += 1
            self.image_widget.update_image(os.path.join(self.basedir, "..", "VideoFiles", "cropped_frames", f"frame{self.frame_number}.png"))

    def test(self):
        """Test the model on a single image"""
        self.test_button.setEnabled(False)
        self.worker = Worker(
            self.frame_number, 
            self.prompt.toPlainText(), 
            self.negative_prompt.toPlainText(),
            self.steps_slider.value(), 
            self.denoising_slider.value(), 
            self.cfg_slider.value()
            )
        
        self.worker.signals.progress_image.connect(self.update_image_progress)
        # Execute
        self.threadpool.start(self.worker)
        self.worker.signals.finished_image.connect(self.update_image)

    def generate(self):
        """Generate all the images and save them to a folder"""
        self.generate_button.setEnabled(False)
        self.test_button.hide()
        self.next_button.setEnabled(False)
        self.back_button.setEnabled(False)
        self.worker = Worker(
            self.frame_number, 
            self.prompt.toPlainText(), 
            self.negative_prompt.toPlainText(),
            self.steps_slider.value(), 
            self.denoising_slider.value(), 
            self.cfg_slider.value(),
            single_frame_flag=False
            )
        

        self.worker.signals.progress_image.connect(self.update_image_progress)
        self.worker.signals.progress_batch.connect(self.update_batch_progress)
        self.worker.signals.finished_image.connect(self.update_image)
        self.worker.signals.finished_batch.connect(self.send_to_video_player)
        self.worker.signals.application_signal.connect(self.deactivate_all)
        # Execute
        self.threadpool.start(self.worker)

    def interrupt(self):
        """Interrupts the process."""
        self.worker.kill()
        self.restore_buttons()
        
        

    def deactivate_all(self):
        """Deactivates all buttons and sliders"""
        self.next_button.hide()
        self.back_button.hide()
        self.steps_label.hide()
        self.steps_slider.hide()
        self.denoise_label.hide()
        self.denoising_slider.hide()
        self.cfg_label.hide()
        self.cfg_slider.hide()
        self.prompt_label.hide()
        self.prompt.hide()
        self.negative_prompt_label.hide()
        self.negative_prompt.hide()

    def deactivate_all_interrupt(self):
        self.generate_button.setEnabled(False)
        self.test_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.back_button.setEnabled(False)
        self.interrupt_button.setEnabled(False)

    def restore_buttons(self):
        self.generate_button.setEnabled(True)
        self.test_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.back_button.setEnabled(True)
        self.interrupt_button.setEnabled(True)
        self.test_button.show()

        self.next_button.show()
        self.back_button.show()
        self.steps_label.show()
        self.steps_slider.show()
        self.denoise_label.show()
        self.denoising_slider.show()
        self.cfg_label.show()
        self.cfg_slider.show()
        self.prompt_label.show()
        self.prompt.show()
        self.negative_prompt_label.show()
        self.negative_prompt.show()
        
    def send_to_video_player(self):
        self.restore_buttons()
        self.video_output_signal.emit()
        self.tabs.setCurrentIndex(2)

    def update_batch_progress(self, str, progress):
        #self.loading_bar.setText(str)
        self.loading_bar.setValue(progress)
    
    def update_image_progress(self, str, progress):
        self.image_progress_label.setText(str)
        self.image_bar.setValue(progress)

    def handle_file_menu_signal(self):
        self.restore_buttons()
        self.image_widget.update_image(os.path.join(self.basedir, "..", "VideoFiles", "cropped_frames", f"frame{self.frame_number}.png"))

    def update_image(self):
        self.test_button.setEnabled(True)
        self.image_widget.update_image(os.path.join(self.basedir, "..", "VideoFiles", "temp.png"))

    def update_steps_label(self, value):
        self.steps_label.setText("Steps: " + str(value))
    
    def update_denoise_label(self, value):
        value = value / 10
        self.denoise_label.setText("Denoising: " + str(value))
    
    def update_cfg_label(self, value):
        self.cfg_label.setText("CFG: " + str(value))