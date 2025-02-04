import sys
import time
from datetime import timedelta
import threading

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit
)
from PyQt5.QtCore import QTimer, Qt

import pyaudio

from .audio_recorder import AudioRecorder
from .transcriber import GoogleCloudTranscriber


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Recorder & Transcriber")

        # PyAudio instance for device enumeration
        self.audio = pyaudio.PyAudio()

        # Internal state
        self.is_recording = False
        self.is_paused = False

        # Timer stuff
        self.record_start_time = 0.0
        self.accumulated_time = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_label)

        # Filenames
        self.wav_filename = "output.wav"
        self.mp3_filename = "output.mp3"

        # Recorder/transcriber references
        self.recorder = None
        self.recording_thread = None
        self.transcriber = GoogleCloudTranscriber()

        # Build the UI
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Device Selection
        device_layout = QHBoxLayout()

        self.input_device_combo = QComboBox()
        self.populate_input_devices()
        device_layout.addWidget(QLabel("Input Device: "))
        device_layout.addWidget(self.input_device_combo)

        self.output_device_combo = QComboBox()
        self.populate_output_devices()
        device_layout.addWidget(QLabel("Output Device: "))
        device_layout.addWidget(self.output_device_combo)

        main_layout.addLayout(device_layout)

        # Buttons
        btn_layout = QHBoxLayout()

        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.handle_record)
        btn_layout.addWidget(self.record_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.handle_pause)
        self.pause_button.setEnabled(False)
        btn_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.handle_stop)
        self.stop_button.setEnabled(False)
        btn_layout.addWidget(self.stop_button)

        main_layout.addLayout(btn_layout)

        # Timer Label
        self.timer_label = QLabel("Recorded: 00:00:00")
        main_layout.addWidget(self.timer_label, alignment=Qt.AlignCenter)

        # Transcription Text
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText("Transcription will appear here...")
        main_layout.addWidget(self.transcription_text)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def populate_input_devices(self):
        """Populate combo box with available input (mic) devices."""
        num_devices = self.audio.get_device_count()
        for i in range(num_devices):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info.get('maxInputChannels', 0) > 0:
                self.input_device_combo.addItem(device_info.get('name'), i)

    def populate_output_devices(self):
        """Populate combo box with available output (speaker) devices."""
        num_devices = self.audio.get_device_count()
        for i in range(num_devices):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info.get('maxOutputChannels', 0) > 0:
                self.output_device_combo.addItem(device_info.get('name'), i)

    def handle_record(self):
        if not self.is_recording:
            self.is_recording = True
            self.is_paused = False
            self.record_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)

            self.record_start_time = time.time()
            self.accumulated_time = 0.0
            self.timer.start(100)

            input_index = self.input_device_combo.currentData()

            # Initialize the recorder
            self.recorder = AudioRecorder(
                output_wav=self.wav_filename,
                device_index=input_index
            )

            # Launch in a background thread
            self.recording_thread = threading.Thread(target=self.recorder.start_recording)
            self.recording_thread.start()

    def handle_pause(self):
        if self.is_recording:
            if not self.is_paused:
                # Pause
                self.is_paused = True
                self.pause_button.setText("Resume")
                self.accumulated_time += time.time() - self.record_start_time
                if self.recorder:
                    self.recorder.pause_recording()
            else:
                # Resume
                self.is_paused = False
                self.pause_button.setText("Pause")
                self.record_start_time = time.time()
                if self.recorder:
                    self.recorder.resume_recording()

    def handle_stop(self):
        if self.is_recording:
            self.is_recording = False
            self.is_paused = False
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.record_button.setEnabled(True)
            self.timer.stop()

            # Stop recorder
            if self.recorder:
                self.recorder.stop_recording()
            if self.recording_thread:
                self.recording_thread.join()

            # Convert to MP3 & transcribe
            if self.recorder:
                self.recorder.convert_to_mp3(self.mp3_filename)

            self.perform_transcription()

    def update_timer_label(self):
        if self.is_recording and not self.is_paused:
            elapsed = time.time() - self.record_start_time + self.accumulated_time
            self.timer_label.setText(f"Recorded: {str(timedelta(seconds=int(elapsed)))}")

    def perform_transcription(self):
        """
        Perform transcription (and diarization) using Google Cloud,
        then display results in the QTextEdit.
        """
        try:
            transcript = self.transcriber.transcribe(
                wav_file=self.wav_filename,
                sample_rate=44100,
                enable_diarization=True,
                speaker_count=2
            )
            self.transcription_text.setPlainText(transcript)
        except Exception as e:
            self.transcription_text.setPlainText(f"Error during transcription: {e}")
