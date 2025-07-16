import os
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client with API key from environment
client = groq.Client(api_key=os.getenv('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'))

# Global variables
cached_text = ""

def set_pdf_context(text):
    global cached_text
    cached_text = text

def clear_context():
    global cached_text
    cached_text = ""

def generate_notes_with_llm():
    try:
        if not cached_text.strip():
            return "❌ No PDF content available to generate notes from."

        # Limit the text to first 8000 characters for better context while still being fast
        text_sample = cached_text[:8000]

        prompt = f"""Please generate detailed, well-structured study notes from the following text. Format your response with clear organization:

Content: {text_sample}

FORMAT REQUIREMENTS:
1. Use # for main section headers (e.g., # Introduction)
2. Use ## for subsection headers (e.g., ## Key Components)
3. Use bullet points (•) for listing key concepts and important points
4. Use numbered lists (1., 2., etc.) for sequential steps or processes
5. Include brief explanations after bullet points where needed
6. Bold important terms or concepts using **term**
7. Organize content logically with clear hierarchy
8. Include a brief introduction and conclusion

The notes should be comprehensive yet concise, focusing on the most important information from the text. Make sure to identify and highlight key concepts, definitions, and relationships between ideas."""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert academic note-taker who creates well-structured, detailed notes with perfect formatting. You excel at organizing information hierarchically with clear headings, subheadings, and bullet points."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.3,  # Lower temperature for more consistent formatting
            max_tokens=2000   # Increased token count for more detailed notes
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating notes: {str(e)}"

def handle_llm_query(query):
    try:
        # Check if query is PDF-related but no PDF is loaded
        pdf_related_terms = ["pdf", "document", "text", "content", "summarize", "notes"]
        if any(term in query.lower() for term in pdf_related_terms) and not cached_text.strip():
            return "❌ Please upload a PDF first before asking about its content."

        # If there's cached text from a PDF, include it in the context
        context = f"Context from PDF: {cached_text}\n" if cached_text.strip() else ""

        # Prepare the prompt
        prompt = f"{context}Query: {query}\nResponse:"

        # Call the language model
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=1000
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"
