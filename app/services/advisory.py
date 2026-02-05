
from app.services.llm import LLMService

class AdvisoryService:
    
    @staticmethod
    def handle_academic_query(message: str, last_domain: str = None) -> str:
        """
        Handle academic-related queries.
        """
        if "subject" in message:
            prompt = f"As an academic advisor, help with this subject-related query: {message}"
        elif "timetable" in message or "schedule" in message:
            prompt = f"As an academic advisor, help create a study schedule for: {message}"
        elif "backlog" in message:
            prompt = f"As an academic advisor, provide guidance on managing academic backlogs: {message}"
        else:
            prompt = f"As an academic advisor, provide guidance on: {message}"
        
        return LLMService.handle_llm_query(prompt)
