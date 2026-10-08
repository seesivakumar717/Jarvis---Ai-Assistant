"""Voice I/O. DISABLED until voice.enabled: true in config.yaml.

Left as a stub because the right STT/TTS stack depends on your OS and
hardware. Two solid local (no-cloud) options:

  STT: faster-whisper (pip install faster-whisper) + sounddevice for mic capture
  TTS: piper-tts (pip install piper-tts), fully offline, many voices

Example faster-whisper wiring for listen_text():

    from faster_whisper import WhisperModel
    import sounddevice as sd
    import numpy as np

    _model = WhisperModel("base.en", device="cpu")

    def listen_text(seconds=5):
        audio = sd.rec(int(seconds * 16000), samplerate=16000, channels=1, dtype="float32")
        sd.wait()
        segments, _ = _model.transcribe(audio.flatten())
        return " ".join(s.text for s in segments).strip()

Example piper wiring for speak():

    import subprocess
    def speak(text):
        subprocess.run(["piper", "--model", "en_US-lessac-medium", "--output_file", "/tmp/out.wav"],
                        input=text.encode())
        subprocess.run(["aplay", "/tmp/out.wav"])   # or afplay on macOS, or a cross-platform player
"""
from jarvis.config import load_config


def _check_enabled():
    cfg = load_config()
    if not cfg.get("voice", {}).get("enabled", False):
        raise RuntimeError("voice is disabled in config.yaml.")


def speak(text: str):
    _check_enabled()
    raise NotImplementedError("Wire up a TTS engine here — see module docstring for a piper example.")


def listen_text(seconds: int = 5) -> str:
    _check_enabled()
    raise NotImplementedError("Wire up an STT engine here — see module docstring for a faster-whisper example.")


def listen_yes_no(seconds: int = 4):
    """Returns True/False, or None if unclear (caller should fall back to text)."""
    _check_enabled()
    text = listen_text(seconds).lower()
    if any(w in text for w in ("yes", "yeah", "confirm", "proceed", "go ahead")):
        return True
    if any(w in text for w in ("no", "stop", "cancel", "don't")):
        return False
    return None
