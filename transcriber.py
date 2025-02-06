import os
import logging
from PyQt5.QtCore import QThread, pyqtSignal
from google.cloud import speech

logger = logging.getLogger(__name__)

class TranscriberWorker(QThread):
    # Signals that can be received in the UI thread
    transcription_finished = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, wav_file, sample_rate=44100, language_code="en-US",
                 enable_diarization=False, speaker_count=2, parent=None):
        super().__init__(parent)
        self.wav_file = wav_file
        self.sample_rate = sample_rate
        self.language_code = language_code
        self.enable_diarization = enable_diarization
        self.speaker_count = speaker_count

    def run(self):
        try:
            transcript = self._transcribe()
            self.transcription_finished.emit(transcript)
        except Exception as e:
            logger.error("Transcription error: %s", e)
            self.error_signal.emit(str(e))

    def _transcribe(self):
        client = speech.SpeechClient()

        with open(self.wav_file, 'rb') as f:
            content = f.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code=self.language_code,
            enable_speaker_diarization=self.enable_diarization,
            diarization_speaker_count=self.speaker_count
        )

        logger.info("Starting Google Cloud transcription for %s", self.wav_file)
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=300)
        logger.info("Transcription finished for %s", self.wav_file)

        transcript_text = ""
        for result in response.results:
            alternative = result.alternatives[0]
            if self.enable_diarization:
                for word in alternative.words:
                    transcript_text += f"Speaker {word.speaker_tag}: {word.word} "
            else:
                transcript_text += alternative.transcript + "\n"

        return transcript_text
