
from flask import Blueprint, request, jsonify, render_template, current_app, send_from_directory
from app.services.chat_manager import chat_manager
from app.services.mentor_service import MentorService
from app.services.pdf_manager import PDFManager
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'reply': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'reply': 'No file selected'}), 400

    user_id = request.remote_addr
    state = chat_manager.get_state(user_id)

    if file and file.filename.lower().endswith('.pdf'):
        # Process the PDF directly with the file object
        file_bytes = file.read()
        pdf_text = PDFManager.extract_text(file_bytes)
        
        # Update state with PDF context
        state.loaded_file_path = file.filename
        state.pdf_text = pdf_text

        # Determine type for smarter prompts later
        if 'resume' in file.filename.lower():
            state.loaded_file_type = "resume"
            response = "✅ Resume uploaded. You can ask me to 'Analyze this' for detailed feedback."
        else:
            state.loaded_file_type = "pdf"
            response = "✅ Document uploaded. Detailed analysis mode active."

        state.add_to_history("upload " + file.filename, response)
        return jsonify({'reply': response})

    return jsonify({'reply': "⚠️ Please upload a valid PDF file."}), 400

@main_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    user_id = request.remote_addr

    if not user_message:
        return jsonify({'reply': 'Please provide a message.'}), 400

    # Get or create user state
    state = chat_manager.get_state(user_id)

    # Process via MentorService (The Brain)
    bot_response = MentorService.process_request(user_message, state)
    
    # Update History
    state.add_to_history(user_message, bot_response)

    return jsonify({'reply': bot_response})
