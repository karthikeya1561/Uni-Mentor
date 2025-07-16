from advisor_module import handle_academic_query
from career_module import handle_career_query, handle_resume_query
from interview_module import handle_interview_query
from pdf_summary_module import extract_text_from_pdf, summarize_pdf, generate_notes_from_pdf
from lm_module import handle_llm_query, set_pdf_context

class ChatbotState:
    def __init__(self):
        self.last_domain = None
        self.loaded_file_path = None
        self.loaded_file_type = None
        self.last_llm_topic = None
        self.user_interest_field = None
        self.project_suggested_once = False
        self.resume_outline_pending = False
        self.conversation_history = []
        self.last_response = None
        self.current_context = None

    def add_to_history(self, user_message, bot_response):
        self.conversation_history.append({
            "user": user_message,
            "bot": bot_response
        })
        self.last_response = bot_response

    def get_recent_context(self, num_messages=3):
        if len(self.conversation_history) == 0:
            return ""
        recent = self.conversation_history[-num_messages:]
        context = "\n".join([
            f"User: {exchange['user']}\nBot: {exchange['bot']}"
            for exchange in recent
        ])
        return context

    def clear_state(self):
        self.__init__()

# Initialize global state
chatbot_state = ChatbotState()

def chatbot_response(message):
    global chatbot_state

    message = message.lower().strip()

    # Add conversation context to LLM queries
    recent_context = chatbot_state.get_recent_context()

    # Basic greetings with context awareness
    if message in ["hello", "hi", "hey"]:
        response = "Hey there! 😊 I'm your academic assistant. How can I help you today?"
        if chatbot_state.last_domain:
            response += f"\nWe were previously discussing {chatbot_state.last_domain}. Would you like to continue with that?"
        chatbot_state.add_to_history(message, response)
        return response

    elif "thank" in message:
        response = "You're welcome! 😊 Let me know if you need any other academic assistance!"
        chatbot_state.add_to_history(message, response)
        return response

    # Check if query is academic-related
    academic_terms = [
        "pdf", "document", "resume", "study", "notes", "academic", "subject",
        "career", "job", "interview", "project", "timetable", "schedule",
        "backlog", "course", "college", "university", "exam", "assignment",
        "homework", "research", "thesis", "paper", "education"
    ]

    # If message doesn't contain any academic terms and no previous context exists
    if not any(term in message.lower() for term in academic_terms) and not chatbot_state.last_domain:
        response = (
            "I am specifically designed to assist with academic and career-related matters. "
            "Here are the things I can help you with:\n\n"
            "1. 📄 PDF Document Analysis\n"
            "   - Summarize academic papers\n"
            "   - Generate study notes\n\n"
            "2. 📝 Resume Services\n"
            "   - Review your resume\n"
            "   - Provide resume writing tips\n\n"
            "3. 🎓 Academic Advising\n"
            "   - Course selection guidance\n"
            "   - Study planning\n\n"
            "4. 💼 Career Guidance\n"
            "   - Career path suggestions\n"
            "   - Industry insights\n\n"
            "5. 🤝 Interview Preparation\n"
            "   - Interview tips\n"
            "   - Common questions\n\n"
            "6. 🚀 Project Ideas\n"
            "   - Academic project suggestions\n"
            "   - Project planning help\n\n"
            "7. 📅 Schedule Management\n"
            "   - Timetable creation\n"
            "   - Backlog management\n\n"
            "How can I assist you with any of these academic areas?"
        )
        chatbot_state.add_to_history(message, response)
        return response

    # Reset topic if unrelated to projects
    if any(kw in message for kw in ["timetable", "schedule", "backlog", "resume", "interview", "pdf"]):
        chatbot_state.last_llm_topic = None
        chatbot_state.user_interest_field = None

    # PDF Upload
    if "upload pdf" in message:
        file_path = input("Enter PDF file path: ")
        pdf_text = extract_text_from_pdf(file_path)
        set_pdf_context(pdf_text)
        chatbot_state.loaded_file_path = file_path
        chatbot_state.loaded_file_type = "pdf"
        response = (
            "✅ PDF uploaded successfully.\n\n"
            "You can now:\n"
            "1. Type 'summarize pdf' for a quick overview\n"
            "2. Type 'generate notes' for detailed study notes"
        )
        chatbot_state.add_to_history(message, response)
        return response

    # Resume Upload
    elif "upload resume" in message:
        file_path = input("Enter resume file path: ")
        if file_path.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_path)
            set_pdf_context(resume_text)
            chatbot_state.loaded_file_path = file_path
            chatbot_state.loaded_file_type = "resume"
            response = "✅ Resume uploaded. Type 'review my resume' to get feedback."
            chatbot_state.add_to_history(message, response)
            return response
        else:
            response = "⚠️ Please upload a valid PDF file for your resume."
            chatbot_state.add_to_history(message, response)
            return response

    # Review Resume
    elif "review" in message and "resume" in message:
        from pdf_summary_module import cached_text
        if not cached_text.strip():
            response = "❌ Please upload your resume first."
            chatbot_state.add_to_history(message, response)
            return response
        response = handle_llm_query(f"Context: {recent_context}\nCan you review this resume for clarity, formatting, and impact?")
        chatbot_state.add_to_history(message, response)
        return response

    # Resume Tips
    elif "resume" in message:
        response = handle_resume_query(message)
        if "generate a resume outline" in response.lower():
            chatbot_state.resume_outline_pending = True
        chatbot_state.add_to_history(message, response)
        return response

    # Summarize PDF
    elif any(phrase in message for phrase in ["summarize pdf", "pdf summary", "quick summary", "overview"]):
        from pdf_summary_module import cached_text
        if not cached_text.strip():
            response = "❌ Please upload a PDF first."
            chatbot_state.add_to_history(message, response)
            return response
        response = summarize_pdf()
        chatbot_state.add_to_history(message, response)
        return response
    
    # Generate Notes
    elif any(phrase in message for phrase in ["generate notes", "create notes", "make notes", "take notes", "notes from pdf", "pdf notes"]):
        from pdf_summary_module import cached_text, generate_notes_from_pdf
        if not cached_text.strip():
            response = "❌ Please upload a PDF first."
            chatbot_state.add_to_history(message, response)
            return response
        notes = generate_notes_from_pdf()
        if notes.startswith("Error") or notes.startswith("❌"):
            response = "I apologize, but I encountered an error while generating notes. Please try uploading the PDF again."
            chatbot_state.add_to_history(message, response)
            return response
        chatbot_state.add_to_history(message, notes)
        return notes

    # Academic Queries
    elif "academic" in message or "subject" in message:
        response = handle_academic_query(message, chatbot_state.last_domain)
        chatbot_state.add_to_history(message, response)
        return response

    # Career Queries
    elif "career" in message or "job" in message or "roadmap" in message or chatbot_state.last_domain == "career":
        fields = ["ai", "ml", "mechanical", "civil", "electrical", "computer science", "psychology", "biology"]
        
        for field in fields:
            if field in message:
                chatbot_state.last_domain = None
                response = handle_llm_query(f"Context: {recent_context}\nSuggest some career paths for someone interested in {field}")
                chatbot_state.add_to_history(message, response)
                return response

        response, new_domain = handle_career_query(message, chatbot_state.last_domain)
        chatbot_state.last_domain = new_domain
        chatbot_state.add_to_history(message, response)
        return response

    # Interview Queries
    elif "interview" in message:
        response = handle_interview_query(message)
        chatbot_state.add_to_history(message, response)
        return response

    # Project Queries
    elif "project" in message:
        chatbot_state.last_llm_topic = "projects"
        if chatbot_state.project_suggested_once:
            response = "✅ I've already shared project ideas. Ask anything else or say 'more projects' for more ideas."
            chatbot_state.add_to_history(message, response)
            return response
        if chatbot_state.user_interest_field:
            chatbot_state.project_suggested_once = True
            response = handle_llm_query(f"Context: {recent_context}\nSuggest academic project ideas in {chatbot_state.user_interest_field} with real-world relevance.")
            chatbot_state.add_to_history(message, response)
            return response
        response = "🧠 What field are you interested in? (e.g., computer science, electrical, mechanical)"
        chatbot_state.add_to_history(message, response)
        return response

    # Handling project interest after asking field
    elif chatbot_state.last_llm_topic == "projects":
        fields = ["computer science", "electrical", "mechanical", "civil", "biology", "psychology", "ai", "ml"]
        for field in fields:
            if field in message:
                chatbot_state.user_interest_field = field
                chatbot_state.project_suggested_once = True
                chatbot_state.last_llm_topic = None
                response = handle_llm_query(f"Context: {recent_context}\nSuggest academic project ideas in {field} with real-world relevance.")
                chatbot_state.add_to_history(message, response)
                return response
        response = "🔍 Please mention a valid field (e.g., computer science, electrical, mechanical)."
        chatbot_state.add_to_history(message, response)
        return response

    # Timetable & Backlog
    elif "timetable" in message or "schedule" in message:
        response = handle_llm_query(f"Context: {recent_context}\nCreate a personalized timetable based on this query: {message}")
        chatbot_state.add_to_history(message, response)
        return response
    elif "backlog" in message:
        response = handle_llm_query(f"Context: {recent_context}\nHelp me plan and clear academic backlogs. Query: {message}")
        chatbot_state.add_to_history(message, response)
        return response

    elif chatbot_state.resume_outline_pending and message in ["yes", "yeah", "please do", "go ahead", "okay"]:
        chatbot_state.resume_outline_pending = False
        response = (
            "Here's a simple resume outline you can use:\n"
            "1. **Name & Contact Info**\n"
            "2. **Professional Summary**\n"
            "3. **Skills** (technical & soft)\n"
            "4. **Projects** (title, tech stack, what you did)\n"
            "5. **Internships or Experience**\n"
            "6. **Education**\n"
            "7. **Certifications or Achievements**\n\n"
            "Let me know if you want help filling it in!"
        )
        chatbot_state.add_to_history(message, response)
        return response

    # Default Fallback with context
    response = handle_llm_query(f"Context from previous messages:\n{recent_context}\n\nNew message: {message}")
    chatbot_state.add_to_history(message, response)
    return response


def main():
    print("Welcome to Smart ChatBot! (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break
        response = chatbot_response(user_input)
        print("Chatbot:", response)

if __name__ == "__main__":
    main()
