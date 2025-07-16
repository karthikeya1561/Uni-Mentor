from lm_module import handle_llm_query

def handle_interview_query(message):
    # Prepare interview-specific prompts based on the query
    if "technical" in message:
        prompt = f"Provide technical interview preparation guidance for: {message}"
    elif "hr" in message or "behavioral" in message:
        prompt = f"Provide HR/behavioral interview preparation guidance for: {message}"
    elif "question" in message:
        prompt = f"Suggest common interview questions and answers for: {message}"
    else:
        prompt = f"Provide general interview preparation guidance for: {message}"
    
    return handle_llm_query(prompt)
