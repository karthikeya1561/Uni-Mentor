from lm_module import handle_llm_query  # make sure this import is there

def handle_academic_query(message, last_domain=None):
    # Prepare a more specific prompt based on the query type
    if "subject" in message:
        prompt = f"As an academic advisor, help with this subject-related query: {message}"
    elif "timetable" in message or "schedule" in message:
        prompt = f"As an academic advisor, help create a study schedule for: {message}"
    elif "backlog" in message:
        prompt = f"As an academic advisor, provide guidance on managing academic backlogs: {message}"
    else:
        prompt = f"As an academic advisor, provide guidance on: {message}"
    
    return handle_llm_query(prompt)
