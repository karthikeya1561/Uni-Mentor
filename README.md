# 🎓 UniMentor - AI University Assistant

**UniMentor** is an advanced AI-powered chatbot designed to act as a personal academic advisor and career counselor for students. It leverages Google's **Gemini AI** to provide intelligent responses, analyze documents, and offer personalized career guidance.

## ✨ Key Features

*   **🧠 Intelligent Chat:** Powered by Gemini 1.5 Flash for human-like, context-aware conversations.
*   **📄 Resume Analysis:** Upload your PDF resume for instant ATS feedback, scoring, and improvement tips.
*   **📚 Study Helper:** Generate summarized notes and flashcards from uploaded academic textbooks or papers.
*   **💾 Conversation Memory:** The bot remembers previous interactions (up to 5 turns) for a seamless chat experience.
*   **🎨 Modern UI:** A beautiful, responsive interface built with Next.js and Tailwind CSS, featuring Markdown rendering.

## 🛠️ Tech Stack

*   **Frontend:** Next.js (React), Tailwind CSS, Framer Motion, React Markdown.
*   **Backend:** Python, Flask, Google Generative AI (Gemini).
*   **AI Model:** Gemini 1.5 Flash / Gemini Pro.

## 🚀 Getting Started

Follow these instructions to set up the project locally on your machine.

### Prerequisites

*   **Python** (3.9 or higher)
*   **Node.js** (18 or higher)
*   **Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))

### 1. Clone the Repository

```bash
git clone https://github.com/karthikeya1561/Uni-Mentor.git
cd Uni-Mentor
```

### 2. Backward Setup (Python)

Navigate to the root directory (where `run.py` is located):

```bash
# Optional: Create a virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Configuration:**
Create a `.env` file in the root directory and add your API credentials:

```env
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=your_random_secret_string
```

### 3. Frontend Setup (Next.js)

Open a new terminal and navigate to the `frontend` folder:

```bash
cd frontend

# Install Node dependencies
npm install
```

## ▶️ Running the Application

You need to run both the backend and frontend servers simultaneously.

**Terminal 1 (Backend):**
```bash
# Make sure you are in the root directory
python run.py
# Server will start on http://127.0.0.1:5000
```

**Terminal 2 (Frontend):**
```bash
# Make sure you are in the 'frontend' directory
cd frontend
npm run dev
# App will start on http://localhost:3000
```

## 👥 Usage

1.  Open your browser and visit `http://localhost:3000`.
2.  Start chatting! Ask about career paths, university tips, or study advice.
3.  Click the **Attachment Icon** (`📎`) to upload a specific PDF (Resume or Textbook).
    *   **Resume:** Ask "Analyze my resume" for feedback.
    *   **Textbook:** Ask "Generate study notes" or "Summarize this".

## 📄 License

This project is open-source and available for educational purposes.
