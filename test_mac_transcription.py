#!/usr/bin/env python3
"""
Smoke-test the configured Mac FreeFlow transcription API without audio hardware.
"""

import io
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from freeflow_linux import MacTranscriptionClient, load_config


def make_test_wav() -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".wav") as wav:
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "flite=text=Testing free flow transcription from Linux.",
                "-ar",
                "16000",
                "-ac",
                "1",
                "-y",
                wav.name,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return Path(wav.name).read_bytes()


def main():
    cfg = load_config()
    transcription_url = cfg.get("transcription_url", "").strip()
    if not transcription_url:
        print("ERROR: Set transcription_url in config or FREEFLOW_TRANSCRIPTION_URL.")
        sys.exit(1)

    client = MacTranscriptionClient(transcription_url)
    health = client.health()
    print(f"Health: ok={health.get('ok')} backend={health.get('backend')}")
    if not health.get("ok"):
        print(f"ERROR: unhealthy response: {health!r}")
        sys.exit(1)

    audio = io.BytesIO(make_test_wav())
    audio.name = "freeflow-test.wav"
    transcript = client.transcribe(audio)
    print(f"Transcript: {transcript!r}")
    assert "testing free flow transcription from linux" in transcript.lower()

    print("All tests passed. Mac transcription API is reachable and transcribing.")


if __name__ == "__main__":
    main()
