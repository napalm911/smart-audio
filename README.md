# Smart Audio

A proof-of-concept Python application that:

- Lists available input/output audio devices.
- Records audio (with pause/resume).
- Converts to MP3.
- Transcribes using Google Cloud Speech-to-Text.
- Attempts speaker diarization (who said what).

## Requirements

1. **Python 3.7+**  
2. **Poetry** (for dependency management)  
3. **Google Cloud** setup (if using Google Cloud Speech):
   - Enable the Speech-to-Text API in your Google Cloud project.
   - Generate service account credentials (JSON).
   - Set your environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
     ```

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/my_audio_app.git
   cd my_audio_app
   ```
2. Install dependencies:
   ```bash
   make install
   ```
   This runs `poetry install` under the hood.

## Running

```bash
make run
```

This will:

1. Launch the PyQt GUI.
2. Let you select your input (mic) & output (speaker) device.
3. Click **Record** to start. Pause/Resume as needed.
4. Press **Stop** to finalize the WAV file, convert to MP3, and transcribe.

## Transcription & Diarization

- Uses [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text).
- Diarization is controlled by `enable_speaker_diarization=True` in `transcriber.py`.
- If you prefer a local library, replace the code in `GoogleCloudTranscriber` with an alternative approach (e.g. Vosk, pyannote.audio, etc.).

## Testing

```bash
make test
```

Runs the unit tests in `tests/`.

## Contributing

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/new-stuff`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-stuff`).
5. Open a Pull Request.

## License

[MIT](LICENSE)
