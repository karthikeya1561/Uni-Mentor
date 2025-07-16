from flask import Flask, request, jsonify, send_from_directory
from main import ChatbotState, handle_llm_query, handle_academic_query
from pdf_summary_module import extract_text_from_pdf, summarize_pdf
from lm_module import set_pdf_context
from model import enhanced_career_query, enhanced_resume_query, enhanced_interview_query, handle_general_query

# Track the last career domain for context
last_career_domain = None

app = Flask(__name__, static_folder='.')

# Enable CORS manually
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Create a session-based state dictionary to handle multiple users
user_states = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('css', path)

@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)

@app.route('/favicons/<path:path>')
def serve_favicons(path):
    return send_from_directory('favicons', path)

@app.route('/notes/<path:path>')
def serve_notes(path):
    return send_from_directory('notes', path)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

def get_or_create_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = ChatbotState()
    return user_states[user_id]

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    user_id = request.remote_addr  # Use IP address as a simple user identifier

    if not user_message:
        return jsonify({'reply': 'Please provide a message.'}), 400

    # Get or create user state
    state = get_or_create_state(user_id)

    # Process the message using a modified version of chatbot_response logic
    bot_response = process_message(user_message, state)

    return jsonify({'reply': bot_response})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'reply': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'reply': 'No file selected'}), 400

    user_id = request.remote_addr
    state = get_or_create_state(user_id)

    if file and file.filename.endswith('.pdf'):
        # Process the PDF directly with the file object
        file_bytes = file.read()
        pdf_text = extract_text_from_pdf(file_bytes)
        set_pdf_context(pdf_text)

        # Update state
        state.loaded_file_path = file.filename

        if 'resume' in file.filename.lower():
            state.loaded_file_type = "resume"
            response = "✅ Resume uploaded. Type 'review my resume' to get feedback."
        else:
            state.loaded_file_type = "pdf"
            response = (
                "✅ PDF uploaded successfully.\n\n"
                "You can now:\n"
                "1. Type 'summarize pdf' for a quick overview\n"
                "2. Type 'generate notes' for detailed study notes"
            )

        state.add_to_history("upload " + file.filename, response)
        return jsonify({'reply': response})

    return jsonify({'reply': "⚠️ Please upload a valid PDF file."}), 400

def process_message(message, state):
    message = message.lower().strip()

    # Add conversation context to LLM queries
    recent_context = state.get_recent_context()

    # Basic greetings with context awareness
    if message in ["hello", "hi", "hey"]:
        response = "Hey there! 😊 I'm your academic assistant. How can I help you today?"
        if state.last_domain:
            response += f"\nWe were previously discussing {state.last_domain}. Would you like to continue with that?"
        state.add_to_history(message, response)
        return response

    elif "thank" in message:
        response = "You're welcome! 😊 Let me know if you need any other academic assistance!"
        state.add_to_history(message, response)
        return response

    # Check if query is academic-related
    academic_terms = [
        "pdf", "document", "resume", "study", "notes", "academic", "subject",
        "career", "job", "interview", "project", "timetable", "schedule",
        "backlog", "course", "college", "university", "exam", "assignment",
        "homework", "research", "thesis", "paper", "education"
    ]

    # If message doesn't contain any academic terms and no previous context exists
    if not any(term in message.lower() for term in academic_terms) and not state.last_domain:
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
        state.add_to_history(message, response)
        return response

    # Reset topic if unrelated to projects
    if any(kw in message for kw in ["timetable", "schedule", "backlog", "resume", "interview", "pdf"]):
        state.last_llm_topic = None
        state.user_interest_field = None

    # PDF Upload - handled by the /upload endpoint now
    if "upload pdf" in message or "upload resume" in message:
        response = "Please use the upload button to upload your file."
        state.add_to_history(message, response)
        return response

    # Review Resume
    elif "review" in message and "resume" in message:
        from pdf_summary_module import cached_text
        if not cached_text.strip():
            response = "❌ Please upload your resume first."
            state.add_to_history(message, response)
            return response
        response = handle_llm_query(f"Context: {recent_context}\nCan you review this resume for clarity, formatting, and impact?")
        state.add_to_history(message, response)
        return response

    # Resume Tips
    elif "resume" in message:
        response = enhanced_resume_query(message)
        if "generate a resume outline" in response.lower():
            state.resume_outline_pending = True
        state.add_to_history(message, response)
        return response

    # Summarize PDF
    elif any(phrase in message for phrase in ["summarize pdf", "pdf summary", "quick summary", "overview"]):
        from pdf_summary_module import cached_text
        if not cached_text.strip():
            response = "❌ Please upload a PDF first."
            state.add_to_history(message, response)
            return response
        # Save to file if explicitly requested
        save_to_file = "save" in message.lower() or "download" in message.lower() or "file" in message.lower()
        # Generate PDF if requested
        generate_pdf = "pdf" in message.lower() or "print" in message.lower()
        response = summarize_pdf(save_to_file=save_to_file, generate_pdf=generate_pdf)
        state.add_to_history(message, response)
        return response

    # Generate Notes
    elif any(phrase in message for phrase in ["generate notes", "create notes", "make notes", "take notes", "notes from pdf", "pdf notes"]):
        from pdf_summary_module import cached_text, generate_notes_from_pdf
        if not cached_text.strip():
            response = "❌ Please upload a PDF first."
            state.add_to_history(message, response)
            return response
        notes = generate_notes_from_pdf(cached_text)
        if notes.startswith("Error") or notes.startswith("❌"):
            response = "I apologize, but I encountered an error while generating notes. Please try uploading the PDF again."
            state.add_to_history(message, response)
            return response
        state.add_to_history(message, notes)
        return notes

    # Academic Queries
    elif "academic" in message or "subject" in message:
        response = handle_academic_query(message, state.last_domain)
        state.add_to_history(message, response)
        return response

    # Career Queries
    elif "career" in message or "job" in message or "roadmap" in message or state.last_domain == "career":
        global last_career_domain
        fields = ["ai", "ml", "mechanical", "civil", "electrical", "computer science", "psychology", "biology"]

        for field in fields:
            if field in message:
                state.last_domain = None
                response = handle_llm_query(f"Context: {recent_context}\nSuggest some career paths for someone interested in {field}")
                state.add_to_history(message, response)
                return response

        response, new_domain = enhanced_career_query(message, last_career_domain)
        last_career_domain = new_domain
        state.last_domain = "career" if new_domain else state.last_domain
        state.add_to_history(message, response)
        return response

    # Interview Queries
    elif "interview" in message:
        response = enhanced_interview_query(message)
        state.add_to_history(message, response)
        return response

    # Project Queries
    elif "project" in message:
        state.last_llm_topic = "projects"
        if state.project_suggested_once:
            response = "✅ I've already shared project ideas. Ask anything else or say 'more projects' for more ideas."
            state.add_to_history(message, response)
            return response
        if state.user_interest_field:
            state.project_suggested_once = True
            response = handle_llm_query(f"Context: {recent_context}\nSuggest academic project ideas in {state.user_interest_field} with real-world relevance.")
            state.add_to_history(message, response)
            return response
        response = "🧠 What field are you interested in? (e.g., computer science, electrical, mechanical)"
        state.add_to_history(message, response)
        return response

    # Handling project interest after asking field
    elif state.last_llm_topic == "projects":
        fields = ["computer science", "electrical", "mechanical", "civil", "biology", "psychology", "ai", "ml"]
        for field in fields:
            if field in message:
                state.user_interest_field = field
                state.project_suggested_once = True
                state.last_llm_topic = None
                response = handle_llm_query(f"Context: {recent_context}\nSuggest academic project ideas in {field} with real-world relevance.")
                state.add_to_history(message, response)
                return response
        response = "🔍 Please mention a valid field (e.g., computer science, electrical, mechanical)."
        state.add_to_history(message, response)
        return response

    # Timetable & Backlog
    elif "timetable" in message or "schedule" in message:
        response = handle_llm_query(f"Context: {recent_context}\nCreate a personalized timetable based on this query: {message}")
        state.add_to_history(message, response)
        return response
    elif "backlog" in message:
        response = handle_llm_query(f"Context: {recent_context}\nHelp me plan and clear academic backlogs. Query: {message}")
        state.add_to_history(message, response)
        return response

    elif state.resume_outline_pending and message in ["yes", "yeah", "please do", "go ahead", "okay"]:
        state.resume_outline_pending = False
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
        state.add_to_history(message, response)
        return response

    # Default Fallback with context
    response = handle_general_query(message)
    state.add_to_history(message, response)
    return response

if __name__ == '__main__':
    print("Starting Flask server on port 5000...")
    app.run(debug=True, port=5000, host='127.0.0.1')
