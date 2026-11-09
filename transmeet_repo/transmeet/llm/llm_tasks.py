from transmeet.utils.json_parser import extract_json_from_text
from transmeet.utils.prompt_loader import load_prompt, format_prompt
from transmeet.llm.llm_manager import LLMManager



def generate_meeting_minutes(llm_client, transcribed_text, model_name, meeting_datetime=None):
    import time
    manager = LLMManager(provider=llm_client, model_name=model_name)
    system_prompt = load_prompt("meeting_minutes", "system")

    # Xử lý văn bản dài để tránh chạm giới hạn TPM (Tokens Per Minute) của Groq
    if len(transcribed_text) > 9000 and str(llm_client).lower() == "groq":
        chunk_size = 9000
        chunks = [transcribed_text[i:i+chunk_size] for i in range(0, len(transcribed_text), chunk_size)]
        partial_summaries = []
        for i, ch in enumerate(chunks):
            p = f"Dưới đây là phần {i+1}/{len(chunks)} của bản gỡ băng cuộc họp. Hãy tóm tắt cô đọng trong 300-400 từ các chủ đề thảo luận, quyết định và phân tích kỹ thuật:\n\n{ch}"
            summary = manager.generate_response(system_prompt=system_prompt, user_prompt=p)
            partial_summaries.append(f"### Phần {i+1}:\n{summary}")
            if i < len(chunks) - 1:
                time.sleep(28)
        
        combined_text = "\n\n".join(partial_summaries)
        time.sleep(25)
        user_prompt = load_prompt("meeting_minutes", "user")
        user_prompt = format_prompt(user_prompt, combined_text, meeting_datetime)
        return manager.generate_response(system_prompt=system_prompt, user_prompt=user_prompt)

    user_prompt = load_prompt("meeting_minutes", "user")
    user_prompt = format_prompt(user_prompt, transcribed_text, meeting_datetime)
    return manager.generate_response(system_prompt=system_prompt, user_prompt=user_prompt)


def segment_conversation_by_speaker(llm_client, transcribed_text, model_name):
    system_prompt = load_prompt("speaker_segmentation", "system")
    user_prompt = load_prompt("speaker_segmentation", "user") #replace("{transcribed_text}", transcribed_text)
    user_prompt = format_prompt(user_prompt, transcribed_text)

    manager = LLMManager(provider=llm_client, model_name=model_name)
    return manager.generate_response(system_prompt=system_prompt, user_prompt=user_prompt)


def create_podcast_dialogue(llm_client, transcribed_text, model_name):
    system_prompt = load_prompt("podcast_script", "system")
    user_prompt = load_prompt("podcast_script", "user")
    user_prompt = format_prompt(user_prompt, transcribed_text)

    manager = LLMManager(provider=llm_client, model_name=model_name)
    return manager.generate_response(system_prompt=system_prompt, user_prompt=user_prompt)


def transform_transcript_to_mind_map(llm_client, transcribed_text, model_name):
    system_prompt = load_prompt("mind_map", "system")
    user_prompt = load_prompt("mind_map", "user").replace("{transcribed_text}", transcribed_text)
    user_prompt = format_prompt(user_prompt, transcribed_text)

    manager = LLMManager(provider=llm_client, model_name=model_name)
    response = manager.generate_response(system_prompt=system_prompt, user_prompt=user_prompt)

    if not response:
        raise ValueError("The LLM did not return a valid response.")

    response = extract_json_from_text(response)
    return response if response else {}
