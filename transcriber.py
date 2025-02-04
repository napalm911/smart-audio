import os
from dotenv import load_dotenv
from google.cloud import speech

load_dotenv()  # Load environment variables from .env

GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", 44100))
DIARIZATION_ENABLED = os.getenv("ENABLE_DIARIZATION", "False").lower() == "true"
SPEAKER_COUNT = int(os.getenv("DIARIZATION_SPEAKER_COUNT", 2))
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "en-US")



class GoogleCloudTranscriber:
    def __init__(self):
        # In practice, you'd configure environment variables or pass
        # the path to the service account JSON here.
        pass

    def transcribe(self, wav_file, sample_rate=44100, language_code="en-US",
                   enable_diarization=False, speaker_count=2):
        """
        Transcribe a WAV file using Google Cloud Speech-to-Text.
        Optionally enable speaker diarization.
        """
        client = speech.SpeechClient()

        with open(wav_file, 'rb') as f:
            content = f.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=language_code,
            enable_speaker_diarization=enable_diarization,
            diarization_speaker_count=speaker_count
        )

        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=300)  # Wait up to 5 minutes

        transcript_text = ""
        for result in response.results:
            # We only look at the first alternative for brevity
            alternative = result.alternatives[0]
            if enable_diarization:
                # Word-level info with speaker tags
                for word in alternative.words:
                    speaker_tag = word.speaker_tag
                    transcript_text += f"Speaker {speaker_tag}: {word.word} "
            else:
                # No speaker diarization
                transcript_text += alternative.transcript + "\n"

        return transcript_text
