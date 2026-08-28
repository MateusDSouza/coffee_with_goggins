import os

import requests
from dotenv import load_dotenv


def generate_speech(api_key: str, output_file: str = "welcome.mp3") -> None:
    """Sends a TTS request to Fish Audio and saves the output to a file."""
    url = "https://api.fish.audio/v1/tts"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # The 'model' parameter belongs in the JSON payload alongside the text and format
    payload = {
        "text": "[excited] Hello! Welcome to Fish Audio. [laughing] This is my first AI-generated voice.",
        "reference_id": "ff5468d06c2443dba9b8d2f9c6aa26b0",
        "format": "mp3",
        "model": "s2.1-pro-free",
    }

    print("🎙️ Requesting audio generation...")
    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()

    with open(output_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"🎉 Audio successfully saved to {output_file}")


def main() -> None:
    # Load environment variables from the .env file
    load_dotenv()

    api_key = os.getenv("FISH_AUDIO_API_KEY")
    if not api_key:
        raise ValueError("❌ Critical Error: FISH_AUDIO_API_KEY is missing from the environment.")

    # Execute the script
    generate_speech(api_key=api_key)


if __name__ == "__main__":
    main()
