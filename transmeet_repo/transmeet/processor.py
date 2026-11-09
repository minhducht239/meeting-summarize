# cython: language_level=3
from pathlib import Path
from pydub import AudioSegment
from typing import Optional, Tuple

from transmeet.utils.general_utils import get_logger
from transmeet.utils.audio_utils import get_audio_size_mb
from transmeet.llm.llm_tasks import (
    generate_meeting_minutes,
    create_podcast_dialogue,
    transform_transcript_to_mind_map,
    segment_conversation_by_speaker
)
from transmeet.clients.transcription_client import process_audio_transcription

logger = get_logger(__name__)

def transcribe_audio_file(
    audio_path: str,
    llm_client: str = "groq",
    llm_model: str = "whisper-large-v3-turbo",
    audio_chunk_size_mb: int = 18,
    audio_chunk_overlap: float = 0.5
) -> str:
    """
    Transcribes an audio file using the specified LLM provider.

    Args:
        audio_path (str): Path to the audio file.
        llm_client (str): Transcription provider name.
        llm_model (str): Model name.
        audio_chunk_size_mb (int): Chunk size for processing.
        audio_chunk_overlap (float): Overlap between chunks.

    Returns:
        str: Transcribed text or error message.
    """
    try:
        audio_file_path = Path(audio_path)
        audio = AudioSegment.from_file(audio_file_path)
        file_size_mb = get_audio_size_mb(audio)

        transcript = process_audio_transcription(
            transcription_client=llm_client,
            transcription_model=llm_model,
            audio=audio,
            file_size_mb=file_size_mb,
            audio_chunk_size_mb=audio_chunk_size_mb,
            audio_chunk_overlap=audio_chunk_overlap
        )
        return transcript

    except Exception as e:
        logger.error(f"Error processing audio file {audio_path}: {e}", exc_info=True)
        return f"Error: {e}"


def generate_meeting_minutes_from_transcript(
    transcript: str,
    llm_client: str = "groq",
    llm_model: str = "llama-3.3-70b-versatile"
) -> Optional[str]:
    """
    Generates meeting minutes from a transcript using LLM.

    Args:
        transcript (str): Raw meeting transcript.
        llm_client (str): LLM provider name.
        llm_model (str): Model name.

    Returns:
        str: Generated meeting minutes markdown.
    """
    try:
        return generate_meeting_minutes(llm_client, transcript, llm_model)
    except Exception as e:
        logger.error(f"Error generating meeting minutes: {e}", exc_info=True)
        return f"Error: {e}"


def generate_mind_map_from_transcript(
    transcript: str,
    llm_client: str = "groq",
    llm_model: str = "llama-3.3-70b-versatile"
) -> dict:
    """
    Converts a transcript into a mind map JSON structure.

    Args:
        transcript (str): Raw meeting transcript.
        llm_client (str): LLM provider.
        llm_model (str): Model name.

    Returns:
        dict: Hierarchical JSON mind map.
    """
    try:
        return transform_transcript_to_mind_map(llm_client, transcript, llm_model)
    except Exception as e:
        logger.error(f"Error generating mind map: {e}", exc_info=True)
        return {"error": str(e)}


def generate_podcast_script_from_transcript(transcript: str, llm_client: str = "groq",
                                            llm_model: str = "llama-3.3-70b-versatile"
                                            ) -> Optional[str]:
    """
    Creates a podcast script from the meeting transcript.

    Args:
        transcript (str): Meeting transcript.
        llm_client (str): LLM provider.
        llm_model (str): Model name.

    Returns:
        Optional[str]: Podcast script or None in case of error.
    """
    try:
        return create_podcast_dialogue(llm_client, transcript, llm_model)
    except Exception as e:
        logger.error(f"Error generating podcast script: {e}", exc_info=True)
        return None

def segment_speech_by_speaker(transcript: str, llm_client: str = "groq",
                              llm_model: str = "llama-3.3-70b-versatile") -> Optional[str]:
    """
    Segments transcript into dialogue by speakers using context.

    Args:
        transcript (str): Raw transcript.
        llm_client (str): LLM provider.
        llm_model (str): Model name.

    Returns:
        str: Segmented speaker-based transcript.
    """
    try:
        return segment_conversation_by_speaker(llm_client, transcript, llm_model)
    except Exception as e:
        logger.error(f"Error segmenting speech by speaker: {e}", exc_info=True)
        return f"Error: {e}"


def generate_meeting_transcript_and_minutes(
    meeting_audio_file: str,
    output_dir: Optional[str] = None,
    transcription_client: str = "groq",
    transcription_model: str = "whisper-large-v3-turbo",
    llm_client: str = "groq",
    llm_model: str = "llama-3.3-70b-versatile",
    audio_chunk_size_mb: int = 18,
    audio_chunk_overlap: float = 0.5,
) -> Tuple[str, str]:
    """
    Transcribes audio and generates meeting minutes.

    Args:
        meeting_audio_file (str): Path to audio file.
        output_dir (Optional[str]): Directory to save output files.
        transcription_client (str): Provider for transcription (groq/openai).
        transcription_model (str): Model for transcription.
        llm_client (str): Provider for minutes generation (groq/openai).
        llm_model (str): Model for minutes generation.
        audio_chunk_size_mb (int): Chunk size in MB.
        audio_chunk_overlap (float): Overlap between chunks.

    Returns:
        Tuple[str, str]: (transcript, meeting_minutes)
    """
    transcript = transcribe_audio_file(
        audio_path=meeting_audio_file,
        llm_client=transcription_client,
        llm_model=transcription_model,
        audio_chunk_size_mb=audio_chunk_size_mb,
        audio_chunk_overlap=audio_chunk_overlap,
    )
    meeting_minutes = generate_meeting_minutes_from_transcript(
        transcript=transcript,
        llm_client=llm_client,
        llm_model=llm_model,
    )
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        base_name = Path(meeting_audio_file).stem
        transcript_file = out_path / f"transcript_{base_name}.txt"
        minutes_file = out_path / f"meeting_minutes_{base_name}.md"
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript or "")
        with open(minutes_file, "w", encoding="utf-8") as f:
            f.write(meeting_minutes or "")
    return transcript, meeting_minutes
