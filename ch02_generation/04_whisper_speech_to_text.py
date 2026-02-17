"""
OpenAI Whisper Speech-to-Text Example
Quick example on how to use OpenAI's Whisper model for Speech-to-Text

pip install openai==2.8.0
"""

import httpx
from openai import OpenAI

client = OpenAI(http_client=httpx.Client(verify=False))

with open(
    "..\\datasets\\audio_files\\LJ037-0171.wav",
    "rb",
) as audio_file:
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",  # latest speech model name
        file=audio_file,
    )

print(transcript.text)
