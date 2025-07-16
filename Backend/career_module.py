from lm_module import handle_llm_query  # already imported in your main

def handle_career_query(message, last_domain=None):
    # Prepare career-specific prompts based on the query
    if "roadmap" in message:
        prompt = f"Create a career roadmap for: {message}"
    elif "job" in message:
        prompt = f"Provide job-related guidance for: {message}"
    else:
        prompt = f"Provide career guidance for: {message}"
    
    response = handle_llm_query(prompt)
    return response, "career"  # Set the domain to career for context

def handle_resume_query(message):
    # Handle different types of resume-related queries
    if "format" in message or "template" in message:
        prompt = "Provide guidance on resume formatting and templates"
    elif "tips" in message:
        prompt = "Share effective resume writing tips and best practices"
    elif "review" in message:
        prompt = "Review the provided resume and give feedback"
    else:
        prompt = f"Provide resume-related guidance for: {message}"
    
    return handle_llm_query(prompt)

def handle_career_query(message, last_domain):
    message = message.lower()

    # Extract domain if any
    domains = [
        "ai", "ml", "artificial intelligence", "mechanical", "civil",
        "electrical", "electronics", "cybersecurity", "robotics", "datascience"
    ]

    for domain in domains:
        if domain in message:
            last_domain = domain
            prompt = f"Suggest career paths for a student interested in {domain}. Include common roles and required skills."
            return handle_llm_query(prompt), last_domain

    if last_domain:
        prompt = f"Suggest career paths for someone in {last_domain}. Include common roles and skills."
        return handle_llm_query(prompt), last_domain

    return "Tell me your area of interest (e.g., AI, Mechanical) and I'll suggest some career paths!", last_domain

def handle_resume_query(message):
    message = message.lower()

    if "format" in message or "template" in message:
        return "Here's a good resume format:\n- Name & Contact\n- Summary\n- Skills\n- Projects\n- Internships\n- Education\n- Certifications\nWant me to generate a resume outline for you?"

    elif "tips" in message:
        return (
            "Quick resume tips:\n"
            "• Keep it to 1 page\n"
            "• Tailor it to the job role\n"
            "• Use action verbs (e.g. 'Developed', 'Led')\n"
            "• Highlight projects and impact"
        )

    elif "review" in message:
        return "Please upload your resume text and I'll review it for clarity, formatting, and impact."
    
    elif "yes" in message or "generate" in message or "outline" in message:
        return (
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

    return "I'm here to help with resume format, tips, reviews, or if you'd like to upload your resume for analysis type - UPLOAD RESUME"    