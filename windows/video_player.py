from PyQt6.QtCore import (
    QStandardPaths, 
    Qt,  
    QUrl
    )
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDialog, 
    QFileDialog,
    QMainWindow, 
    QStyle, 
    QToolBar
    )
from PyQt6.QtMultimedia import (
    QAudioOutput, 
    QMediaFormat,
    QMediaPlayer
    )
from PyQt6.QtMultimediaWidgets import QVideoWidget
import os
import sys
import shutil

AVI = "video/x-msvideo"

def get_supported_mime_types():
    result = []
    for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
        mime_type = QMediaFormat(f).mimeType()
        result.append(mime_type.name())
    return result


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.basedir = os.path.dirname(os.path.abspath(__file__))

        self.setWindowTitle("Video Player")

        # set up the video widget
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)

        #self.media_player.errorOccurred.connect(self.error_alert)
        self.tool_bar = QToolBar()
        self.tool_bar.setFloatable(False)
        self.addToolBar(self.tool_bar)

        # set up the play button
        self.play_action= QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            "Play"
            )
        self.tool_bar.addAction(self.play_action)
        self.play_action.triggered.connect(self.play)

        # set up the pause button
        self.pause_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause),
            "Pause"
            )
        self.tool_bar.addAction(self.pause_action)
        self.pause_action.triggered.connect(self.pause)

        # set up the stop button
        self.stop_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop),
            "Stop"
            )
        self.tool_bar.addAction(self.stop_action)
        self.stop_action.triggered.connect(self.stop)

        # set up the save button
        self.save_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown),
            "Save"
            )
        self.tool_bar.addAction(self.save_action)
        self.save_action.triggered.connect(self.save)

        # set up the exit button
        self.exit_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton),
            "Exit"
            )
        self.tool_bar.addAction(self.exit_action)
        self.exit_action.triggered.connect(self.exit)

        # set up the video widget
        self.video_widget = QVideoWidget()
        self.setCentralWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)

        #self.media_player.setSource(QUrl.fromLocalFile(os.path.join(self.basedir, "..", "VideoFiles", "output.avi")))
        
    def update_video(self):
        self.media_player.setSource(QUrl.fromLocalFile(os.path.join(self.basedir, "..", "VideoFiles", "output.avi")))
        self.media_player.play()

    def play(self):
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def stop(self):
        self.media_player.stop()

    def save(self):
        name = QFileDialog.getSaveFileName(
            self, 
            "Save File", 
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation) + "/output.avi", 
            "AVI (*.avi)"
            )
        if name[0]:
            shutil.copy2(
                os.path.join(self.basedir, "..", "VideoFiles", "output.avi"),
                name[0],
                follow_symlinks=True
            )

    def exit(self):
        # dialog to confirm exit
        dialog = QDialog(self)
        dialog.setWindowTitle("Exit")
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.resize(300, 100)
        dialog.exec()
        sys.exit()
        



