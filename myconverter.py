import os
import sys
from moviepy.video.io.VideoFileClip import VideoFileClip
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QLineEdit, 
                            QMessageBox, QSlider, QGraphicsView, QGraphicsScene)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem



class VideoCompressorApp(QWidget):
    def __init__(self):
        super().__init__()
        
      
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_item = QGraphicsVideoItem()
        self.scene = QGraphicsScene(self)
        
        self.clip = None
        self.start_time = 0
        self.end_time = 0
        self.input_file_path = None
        self.duration = 0
        self.is_playing = False
        
        self.initUI()
        self.setup_media_player()

    def initUI(self):
        self.setWindowTitle("")
        self.setFixedSize(450, 400)
        self.setGeometry(100, 100, 900, 700)

        main_layout = QVBoxLayout()

    
        self.video_view = QGraphicsView(self)
        self.scene.addItem(self.video_item)
        self.video_view.setScene(self.scene)
        main_layout.addWidget(self.video_view, 1)
     
        control_layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        self.btn_choose_file = QPushButton("выбрать видео", self)
        self.btn_choose_file.clicked.connect(self.choose_file)
        file_layout.addWidget(self.btn_choose_file)

        self.btn_play_pause = QPushButton("▶", self)
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        self.btn_play_pause.setEnabled(False)
        file_layout.addWidget(self.btn_play_pause)
        control_layout.addLayout(file_layout)

      
        trim_layout = QVBoxLayout()

        start_layout = QHBoxLayout()
        self.start_label = QLabel("начало: 00:00:00")
        start_layout.addWidget(self.start_label)
        
        self.start_slider = QSlider(Qt.Horizontal)
        self.start_slider.setRange(0, 0)
        self.start_slider.sliderPressed.connect(lambda: self.slider_pressed(self.start_slider))
        self.start_slider.sliderReleased.connect(lambda: self.slider_released(self.start_slider))
        start_layout.addWidget(self.start_slider)
        trim_layout.addLayout(start_layout)

        end_layout = QHBoxLayout()
        self.end_label = QLabel("конец: 00:00:00")
        end_layout.addWidget(self.end_label)
        
        self.end_slider = QSlider(Qt.Horizontal)
        self.end_slider.setRange(0, 0)
        self.end_slider.sliderPressed.connect(lambda: self.slider_pressed(self.end_slider))
        self.end_slider.sliderReleased.connect(lambda: self.slider_released(self.end_slider))
        end_layout.addWidget(self.end_slider)
        trim_layout.addLayout(end_layout)

        control_layout.addLayout(trim_layout)

        btn_layout = QHBoxLayout()
        self.btn_trim = QPushButton("обрезать видео", self)
        self.btn_trim.clicked.connect(self.trim_video)
        self.btn_trim.setEnabled(False)
        btn_layout.addWidget(self.btn_trim)

        self.btn_compress = QPushButton("сжать видео", self)
        self.btn_compress.clicked.connect(self.compress_video)
        btn_layout.addWidget(self.btn_compress)
        control_layout.addLayout(btn_layout)

        settings_layout = QHBoxLayout()
        
        bitrate_layout = QVBoxLayout()
        self.bitrate_label = QLabel("битрейт:", self)
        bitrate_layout.addWidget(self.bitrate_label)
        self.bitrate_input = QLineEdit(self)
        self.bitrate_input.setText("500k")
        bitrate_layout.addWidget(self.bitrate_input)
        settings_layout.addLayout(bitrate_layout)

        resolution_layout = QVBoxLayout()
        self.resolution_label = QLabel("разрешение:", self)
        resolution_layout.addWidget(self.resolution_label)
        self.resolution_input = QLineEdit(self)
        self.resolution_input.setText("640x360")
        resolution_layout.addWidget(self.resolution_input)
        settings_layout.addLayout(resolution_layout)

        control_layout.addLayout(settings_layout)
        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

    def setup_media_player(self):
        self.media_player.setVideoOutput(self.video_item)
        self.media_player.error.connect(self.handle_media_error)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(100)

    def handle_media_error(self, error):
        QMessageBox.warning(self, "ошибка воспроизведения", 
                          f"ошибка при воспроизведении: {self.media_player.errorString()}")

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "выберите видео", "", 
                                                 "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv)")
        if file_path:
            self.input_file_path = file_path
            self.load_video(file_path)

    def load_video(self, file_path):
        try:
            self.clip = VideoFileClip(file_path)
            self.duration = self.clip.duration
            self.start_time = 0
            self.end_time = self.duration
     
            max_value = int(self.duration * 1000)
            self.start_slider.setRange(0, max_value)
            self.end_slider.setRange(0, max_value)
            self.end_slider.setValue(max_value)
     
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            
            self.update_time_labels()
            self.btn_trim.setEnabled(True)
            self.btn_play_pause.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"Не удалось загрузить видео: {str(e)}")

    def toggle_play_pause(self):
        if self.is_playing:
            self.media_player.pause()
            self.btn_play_pause.setText("▶")
        else:
            self.media_player.play()
            self.btn_play_pause.setText("⏸")
        self.is_playing = not self.is_playing

    def slider_pressed(self, slider):
        self.media_player.pause()
        self.btn_play_pause.setText("▶")
        self.is_playing = False

    def slider_released(self, slider):
        position = slider.value()
        self.media_player.setPosition(position)
        
        if slider == self.start_slider:
            self.start_time = position / 1000
            if self.start_time >= self.end_time:
                self.start_time = max(0, self.end_time - 0.1)
                self.start_slider.setValue(int(self.start_time * 1000))
        else:
            self.end_time = position / 1000
            if self.end_time <= self.start_time:
                self.end_time = min(self.duration, self.start_time + 0.1)
                self.end_slider.setValue(int(self.end_time * 1000))
        
        self.update_time_labels()

    def update_duration(self, duration):
        self.duration = duration / 1000
        self.start_slider.setRange(0, duration)
        self.end_slider.setRange(0, duration)
        self.end_slider.setValue(duration)
        self.update_time_labels()

    def update_position(self, position):
        if not self.start_slider.isSliderDown() and not self.end_slider.isSliderDown():
            current_time = position / 1000
            if current_time < self.start_time:
                self.media_player.setPosition(int(self.start_time * 1000))
            elif current_time > self.end_time:
                self.media_player.setPosition(int(self.start_time * 1000))
                self.media_player.pause()
                self.btn_play_pause.setText("▶")
                self.is_playing = False

    def update_ui(self):
        current_pos = self.media_player.position() / 1000
        if self.start_slider.isSliderDown() or self.end_slider.isSliderDown():
            return
            
        if current_pos < self.start_time:
            self.media_player.setPosition(int(self.start_time * 1000))
        elif current_pos > self.end_time:
            self.media_player.setPosition(int(self.start_time * 1000))
            self.media_player.pause()
            self.btn_play_pause.setText("▶")
            self.is_playing = False
            
        self.update_time_labels()

    def update_time_labels(self):
        self.start_label.setText(f"начало: {self.format_time(self.start_time)}")
        self.end_label.setText(f"конец: {self.format_time(self.end_time)}")

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def trim_video(self):
        if not self.input_file_path or not self.clip:
            QMessageBox.warning(self, "ошибка", "файл не загружен")
            return

        output_file_path, _ = QFileDialog.getSaveFileName(self, "сохранить обрезанное видео", "", "Video Files (*.mp4)")

        if not output_file_path:
            return

        try:
            start = max(0, min(self.start_time, self.duration - 0.1))
            end = max(0.1, min(self.end_time, self.duration))
            
            if start >= end:
                QMessageBox.warning(self, "ошибка", "некорректный интервал обрезки (начало должно быть раньше конца)")
                return
                
            trimmed_clip = self.clip.subclip(start, end)
            trimmed_clip.write_videofile(
                output_file_path,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                preset="fast",
                ffmpeg_params=["-crf", "23"]
            )
            QMessageBox.information(self, "готово", f"видео успешно обрезано и сохранено как:\n{output_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"не удалось обрезать видео: {str(e)}")

    def compress_video(self):
        if not self.input_file_path:
            QMessageBox.warning(self, "ошибка", "файл не выбран")
            return

        bitrate = self.bitrate_input.text().strip()
        resolution_str = self.resolution_input.text().strip()

        try:
            resolution = tuple(map(int, resolution_str.split("x")))
        except ValueError:
            QMessageBox.warning(self, "ошибка", "некорректный формат разрешения (используйте 500x500)")
            return

        output_file_path, _ = QFileDialog.getSaveFileName(self, "сохранить сжатое видео", "", "Video Files (*.mp4)")

        if not output_file_path:
            return 

        try:
            compress_video(self.input_file_path, output_file_path, bitrate=bitrate, resolution=resolution)
            QMessageBox.information(self, "готово", f"видео успешно сжато и сохранено как:\n{output_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"ошибка при сжатии: {str(e)}")


def compress_video(input_path, output_path, bitrate="500k", resolution=None):
    video = VideoFileClip(input_path)
    if resolution:
        video = video.resize(resolution)
    video.write_videofile(
        output_path,
        bitrate=bitrate,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="fast",
        ffmpeg_params=["-crf", "23"]
    )

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoCompressorApp()
    window.show()
    sys.exit(app.exec_())