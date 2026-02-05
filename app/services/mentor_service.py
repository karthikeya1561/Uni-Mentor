
from app.services.gemini_service import GeminiService
from app.services.pdf_manager import PDFManager
import logging

logger = logging.getLogger(__name__)

class MentorService:
    """
    The central 'Brain' of the UniMentor chatbot.
    Manages Personas, Context, and Intent Routing.
    """

    SYSTEM_PROMPT = (
        "You are UniMentor, a professional, encouraging, and knowledgeable university academic advisor and career counselor. "
        "Your goal is to help students succeed academically and professionally.\n"
        "Tone: Professional, empathetic, structured, and clear. Avoid slang but remain accessible.\n"
        "Format: Use Markdown for readability (bullet points, bold text).\n"
        "Capabilities: You can analyze resumes, generate study notes, summarize PDFs, and give career advice.\n"
        "If analyzing a document: Provide specific, constructive feedback (Strengths, Weaknesses, Actionable Tips).\n"
        "If asked about careers: Provide realistic and actionable roadmaps.\n"
        "Always conclude with an encouraging or guiding follow-up question."
    )

    @staticmethod
    def process_request(user_message: str, state) -> str:
        """
        Main entry point for processing a user message.
        Decides whether to use specific services (PDF, Advisory) or the LLM.
        """
        message_lower = user_message.lower().strip()
        
        # 1. Check for PDF-Specific Actions (if file is loaded)
        if state.pdf_text:
            if any(kw in message_lower for kw in ["analyze", "review", "critique", "evaluate"]):
                if "resume" in message_lower or state.loaded_file_type == "resume":
                    return MentorService.analyze_document(state.pdf_text, "resume")
                else:
                    return MentorService.analyze_document(state.pdf_text, "general")

            if any(kw in message_lower for kw in ["summarize", "summary", "overview"]):
                return PDFManager.generate_summary(state.pdf_text, save_to_file=False) # Simplified call
            
            if any(kw in message_lower for kw in ["notes", "study material"]):
                return PDFManager.generate_notes(state.pdf_text)

        # 2. Check for Career/Academic Static Logic (Legacy AdvisoryService)
        # We check this briefly, but prefer Gemini if the query is complex.
        # Simple keyword matching:
        # if "timetable" in message_lower or "schedule" in message_lower:
        #     return AdvisoryService.generate_schedule_response(user_message)
        
        # 3. Default: Chat with Gemini (The Mentor Persona)
        # Construct the context-aware prompt
        
        context_str = ""
        if state.pdf_text:
            # Add a snippet of the PDF context if available, or just mention it's loaded
            context_str = f"\n\n[Attached Document Context]:\n{state.pdf_text[:3000]}...\n(End of Context)"
        
        # Get Conversation History
        history_context = state.get_recent_context(num_exchanges=5)
        if history_context:
            history_context = f"\n\n[Conversation History]:\n{history_context}"
        else:
            history_context = ""

        # Combine System Prompt + Context + History + User Message
        full_prompt = (
            f"{MentorService.SYSTEM_PROMPT}\n"
            f"{context_str}"
            f"{history_context}\n\n"
            f"Student: {user_message}\n"
            f"UniMentor:"
        )

        return GeminiService.generate_response(full_prompt)

    @staticmethod
    def analyze_document(text_content: str, doc_type: str) -> str:
        """Specific prompt for deep analysis"""
        if doc_type == "resume":
            prompt = (
                f"{MentorService.SYSTEM_PROMPT}\n\n"
                f"Task: Analyze the following RESUME. Provide specific feedback on Layout, Content, Skills, and Impact.\n"
                f"Be critical but helpful. Suggest improvements for ATS optimization.\n\n"
                f"Resume Content:\n{text_content}\n"
            )
        else:
            prompt = (
                f"{MentorService.SYSTEM_PROMPT}\n\n"
                f"Task: Analyze the following ACADEMIC DOCUMENT. Summarize key points and explain difficult concepts.\n\n"
                f"Document Content:\n{text_content[:5000]}\n"
            )
        
        return GeminiService.generate_response(prompt)
