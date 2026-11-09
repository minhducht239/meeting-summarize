# cython: language_level=3
import argparse
import sys
from pathlib import Path
from transmeet import generate_meeting_transcript_and_minutes


def main():
    parser = argparse.ArgumentParser(
        description="🎤 TransMeet: Transcribe audio and generate meeting minutes using Groq or Google."
    )

    parser.add_argument(
        "-i", "--audio-path", required=True,
        help="Path to the audio file (.wav, .mp3, etc.)"
    )

    parser.add_argument(
        "-o", "--output-dir", default="output",
        help="Directory where output (transcript + minutes) will be saved"
    )

    parser.add_argument(
        "--transcription-client", choices=["groq", "openai"], default="groq",
        help="Transcription backend to use (default: groq)"
    )

    parser.add_argument(
        "--transcription-model", default="whisper-large-v3-turbo",
        help="Transcription model to use (default: whisper-large-v3-turbo)"
    )

    parser.add_argument(
        "--llm-client", choices=["groq", "openai"], default="groq",
        help="LLM backend to use for generating meeting minutes (default: groq)"
    )

    parser.add_argument(
        "--llm-model", default="openai/gpt-oss-120b",
        help="LLM model to use for generating minutes (default: openai/gpt-oss-120b)"
    )

    parser.add_argument(
        "--chunk-size-mb", type=float, default=18,
        help="Size of audio chunks in MB (default: 18)"
    )

    parser.add_argument(
        "--chunk-overlap", type=float, default=0.5,
        help="Overlap ratio between audio chunks (default: 0.5)"
    )

    args = parser.parse_args()

    try:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        transcript, meeting_minutes = generate_meeting_transcript_and_minutes(
            meeting_audio_file=args.audio_path,
            output_dir=str(output_dir),
            transcription_client=args.transcription_client,
            transcription_model=args.transcription_model,
            llm_client=args.llm_client,
            llm_model=args.llm_model,
            audio_chunk_size_mb=args.chunk_size_mb,
            audio_chunk_overlap=args.chunk_overlap,
        )

        base_name = Path(args.audio_path).stem
        transcript_path = output_dir / f"transcript_{base_name}.txt"
        minutes_path = output_dir / f"meeting_minutes_{base_name}.md"

        print(f"✅ Transcript saved to {transcript_path}")
        print(f"✅ Meeting minutes saved to {minutes_path}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
