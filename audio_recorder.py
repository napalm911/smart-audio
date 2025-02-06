import logging
import time
import wave
import pyaudio
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class AudioRecorder:
    def __init__(self, output_wav="output.wav", device_index=None,
                 channels=1, rate=44100, chunk=1024):
        self.output_wav = output_wav
        self.device_index = device_index
        self.channels = channels
        self.rate = rate
        self.chunk = chunk

        self._pyaudio_instance = pyaudio.PyAudio()
        self._stream = None
        self._frames = []
        self._running = False
        self._paused = False

    def start_recording(self):
        """
        Open PyAudio stream and continuously read frames until stopped.
        """
        logger.info("Starting recording. WAV output: %s", self.output_wav)

        # Defensive check: Make sure PyAudio can open the device
        try:
            self._stream = self._pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                input_device_index=self.device_index
            )
        except Exception as e:
            logger.error("Failed to open audio device (%s). Error: %s", self.device_index, e)
            return  # You might want to raise or handle it in the UI

        self._frames = []
        self._running = True

        while self._running:
            if not self._paused:
                try:
                    data = self._stream.read(self.chunk, exception_on_overflow=False)
                    self._frames.append(data)
                except IOError as io_err:
                    logger.warning("PyAudio read overflow: %s", io_err)
            else:
                time.sleep(0.1)

        self._finalize_wav()

    def pause_recording(self):
        logger.debug("Pausing recording.")
        self._paused = True

    def resume_recording(self):
        logger.debug("Resuming recording.")
        self._paused = False

    def stop_recording(self):
        logger.info("Stopping recording.")
        self._running = False

    def _finalize_wav(self):
        """Write frames to a WAV file."""
        logger.debug("Finalizing WAV file: %s", self.output_wav)
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        try:
            wf = wave.open(self.output_wav, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self._pyaudio_instance.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self._frames))
            wf.close()
            logger.info("WAV file written successfully: %s", self.output_wav)
        except Exception as e:
            logger.error("Failed to write WAV file. Error: %s", e)

    def convert_to_mp3(self, mp3_filename="output.mp3"):
        """
        Convert saved WAV file to MP3 using pydub.
        """
        logger.info("Converting %s -> %s (MP3)", self.output_wav, mp3_filename)
        try:
            sound = AudioSegment.from_wav(self.output_wav)
            sound.export(mp3_filename, format="mp3")
            logger.info("MP3 file created: %s", mp3_filename)
        except Exception as e:
            logger.error("Error converting to MP3: %s", e)
