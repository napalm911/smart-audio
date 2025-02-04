import time
import wave
import pyaudio
from pydub import AudioSegment


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
        self._running = True
        self._stream = self._pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            input_device_index=self.device_index
        )
        self._frames = []

        while self._running:
            if not self._paused:
                data = self._stream.read(self.chunk, exception_on_overflow=False)
                self._frames.append(data)
            else:
                time.sleep(0.1)

        # Finalize .wav
        self._finalize_wav()

    def pause_recording(self):
        self._paused = True

    def resume_recording(self):
        self._paused = False

    def stop_recording(self):
        self._running = False

    def _finalize_wav(self):
        """Write frames to a WAV file."""
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        wf = wave.open(self.output_wav, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self._pyaudio_instance.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self._frames))
        wf.close()

    def convert_to_mp3(self, mp3_filename="output.mp3"):
        """
        Convert saved WAV file to MP3 using pydub.
        """
        try:
            sound = AudioSegment.from_wav(self.output_wav)
            sound.export(mp3_filename, format="mp3")
        except Exception as e:
            print(f"Error converting to MP3: {e}")
