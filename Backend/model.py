from lm_module import handle_llm_query
import re

# Expanded list of domains with synonyms and related terms
CAREER_DOMAINS = {
    "ai": ["artificial intelligence", "machine learning", "ml", "deep learning", "neural networks", "ai"],
    "data_science": ["data science", "data analytics", "big data", "data engineering", "business intelligence", "datascience"],
    "software_development": ["software development", "programming", "coding", "software engineering", "app development", "web development"],
    "cybersecurity": ["cybersecurity", "information security", "network security", "cyber security", "security analyst", "ethical hacking"],
    "mechanical": ["mechanical engineering", "mechanical", "robotics", "automation", "manufacturing", "mechatronics"],
    "civil": ["civil engineering", "civil", "structural engineering", "construction", "architecture", "urban planning"],
    "electrical": ["electrical engineering", "electrical", "power systems", "electronics", "circuit design"],
    "electronics": ["electronics engineering", "electronics", "embedded systems", "microcontrollers", "hardware design"],
    "biotech": ["biotechnology", "biotech", "biomedical", "pharmaceutical", "genetic engineering", "bioinformatics"],
    "finance": ["finance", "banking", "investment", "financial analysis", "accounting", "fintech"],
    "healthcare": ["healthcare", "medical", "nursing", "health informatics", "public health", "telemedicine"],
    "marketing": ["marketing", "digital marketing", "market research", "brand management", "social media marketing"],
    "design": ["design", "ux design", "ui design", "graphic design", "product design", "industrial design"],
    "education": ["education", "teaching", "e-learning", "instructional design", "educational technology"],
    "environmental": ["environmental science", "sustainability", "renewable energy", "climate science", "green technology"]
}

# Comprehensive list of interview domains with synonyms and related terms
INTERVIEW_DOMAINS = {
    "data_science": ["data science", "data scientist", "data analysis", "data analytics", "data engineering"],
    "ai": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "neural networks"],
    "software_engineering": ["software engineering", "software development", "programming", "coding", "developer", "swe"],
    "web_development": ["web development", "web design", "frontend", "backend", "full stack", "web app"],
    "mobile_development": ["mobile development", "android", "ios", "app development", "mobile app"],
    "devops": ["devops", "cloud", "aws", "azure", "gcp", "infrastructure", "ci/cd", "kubernetes", "docker"],
    "cybersecurity": ["cybersecurity", "security", "infosec", "information security", "network security", "ethical hacking"],
    "data_engineering": ["data engineering", "data pipeline", "etl", "big data", "hadoop", "spark"],
    "product_management": ["product management", "product manager", "pm", "product owner", "scrum master"],
    "ux_design": ["ux", "user experience", "ui design", "user interface", "product design", "interaction design"],
    "business_analyst": ["business analyst", "ba", "business intelligence", "bi", "data analyst"],
    "project_management": ["project management", "project manager", "program manager", "agile", "scrum"],
    "marketing": ["marketing", "digital marketing", "seo", "content marketing", "social media marketing"],
    "sales": ["sales", "business development", "account management", "customer success"],
    "finance": ["finance", "financial analyst", "accounting", "investment banking", "financial planning"],
    "hr": ["hr", "human resources", "talent acquisition", "recruiting", "people operations"],
    "healthcare": ["healthcare", "medical", "nursing", "physician", "clinical", "health informatics"],
    "education": ["education", "teaching", "professor", "instructor", "academic", "edtech"],
    "consulting": ["consulting", "management consulting", "strategy consulting", "business consulting"],
    "legal": ["legal", "law", "attorney", "paralegal", "compliance", "regulatory"]
}

# Interview preparation aspects
INTERVIEW_ASPECTS = {
    "questions": ["question", "questions", "ask", "asked", "common questions", "typical questions"],
    "technical": ["technical", "coding", "algorithm", "data structure", "system design", "architecture"],
    "behavioral": ["behavioral", "behavior", "soft skills", "culture fit", "teamwork", "leadership"],
    "preparation": ["prepare", "preparation", "study", "practice", "get ready", "tips", "advice"],
    "mock": ["mock", "practice interview", "simulation", "role play", "rehearse"],
    "salary": ["salary", "compensation", "pay", "negotiate", "offer", "package", "benefits"],
    "remote": ["remote", "virtual", "online", "zoom", "teams", "video"],
    "assessment": ["assessment", "test", "assignment", "take home", "challenge", "project"],
    "resume": ["resume", "cv", "curriculum vitae", "application", "cover letter"],
    "portfolio": ["portfolio", "project", "github", "showcase", "demo"],
    "general": ["general", "overall", "comprehensive", "complete", "full", "all"]
}

def identify_career_domain(message):
    """Identify the career domain from the message"""
    message = message.lower()

    # Check for exact domain mentions
    for domain_key, terms in CAREER_DOMAINS.items():
        for term in terms:
            # Look for the term as a whole word
            if re.search(r'\b' + re.escape(term) + r'\b', message):
                return domain_key

    return None

def detect_career_query_type(message):
    """Detect the type of career query from the message"""
    message = message.lower()

    if any(term in message for term in ["skill", "skills", "abilities", "competencies", "what should i know"]):
        return "skills"
    elif any(term in message for term in ["education", "degree", "study", "college", "university", "school", "learn", "course"]):
        return "education"
    elif any(term in message for term in ["salary", "pay", "compensation", "earn", "income", "money"]):
        return "salary"
    elif any(term in message for term in ["trend", "trends", "future", "outlook", "growth", "emerging", "upcoming"]):
        return "trends"
    elif any(term in message for term in ["company", "companies", "organization", "employer", "work for", "hire", "hiring"]):
        return "companies"
    elif any(term in message for term in ["project", "projects", "portfolio", "build", "create", "develop", "showcase"]):
        return "projects"
    elif any(term in message for term in ["job", "jobs", "career", "careers", "profession", "role", "position"]):
        return "paths"
    else:
        return "general"  # Default to general career advice

def generate_career_prompt(domain_key, query_type):
    """Generate a specific prompt based on the domain and query type"""
    domain_name = CAREER_DOMAINS[domain_key][0]  # Use the first term as the canonical name

    prompts = {
        "paths": f"Suggest career paths for a student interested in {domain_name}. Include 5-7 specific job roles, required skills, education, and potential career progression for each.",
        "skills": f"List the most important technical and soft skills needed for a career in {domain_name}. Include both entry-level and advanced skills, and suggest ways to develop these skills.",
        "education": f"Explain the educational requirements and best degree programs for a career in {domain_name}. Include information about relevant certifications, online courses, and alternative learning paths.",
        "salary": f"Provide current salary information for different roles in {domain_name} at entry, mid, and senior levels. Include factors that affect salary and tips for salary negotiation.",
        "trends": f"Describe the current trends and future outlook for careers in {domain_name}. Include emerging technologies, changing job requirements, and how the field is expected to evolve in the next 5-10 years.",
        "companies": f"List the top companies and organizations hiring professionals in {domain_name}. Include information about work culture, interview processes, and tips for getting hired.",
        "projects": f"Suggest 5-7 practical projects that would help someone build skills and a portfolio in {domain_name}. Include project descriptions, skills developed, and how to showcase them to employers.",
        "general": f"Provide comprehensive career advice for someone interested in {domain_name}. Include information about career paths, required skills, education, salary expectations, industry trends, and top companies."
    }

    # Default to general career advice if query type not recognized
    return prompts.get(query_type, prompts["general"])

def enhanced_career_query(message, last_domain):
    """Enhanced version of handle_career_query with more sophisticated understanding"""
    message = message.lower()

    # Special case for the career guidance button
    if message == "career guidance":
        return """I can help with career guidance in many fields! Here are some areas I can provide information about:

1. *Technology Fields*:
   - Artificial Intelligence & Machine Learning
   - Software Development
   - Cybersecurity
   - Data Science
   - Web & Mobile Development

2. *Engineering Fields*:
   - Mechanical Engineering
   - Electrical Engineering
   - Civil Engineering
   - Electronics Engineering

3. *Other Professional Fields*:
   - Finance & Banking
   - Healthcare
   - Marketing
   - Design
   - Education

Tell me which field you're interested in, and I can provide information about:
- Career paths and job roles
- Required skills and how to develop them
- Education and certification requirements
- Salary expectations
- Industry trends and future outlook
- Top companies in the field
- Project ideas for your portfolio

What field would you like to explore?""", None

    # Try to identify domain from the current message
    domain_key = identify_career_domain(message)

    # If domain found in current message, update last_domain
    if domain_key:
        last_domain = domain_key
        query_type = detect_career_query_type(message)
        prompt = generate_career_prompt(domain_key, query_type)
        return handle_llm_query(prompt), last_domain

    # If no domain in current message but we have a last_domain
    if last_domain and last_domain in CAREER_DOMAINS:
        query_type = detect_career_query_type(message)
        prompt = generate_career_prompt(last_domain, query_type)
        return handle_llm_query(prompt), last_domain

    # No domain identified
    return "Tell me your area of interest (e.g., AI, Software Development, Cybersecurity) and I'll suggest some career paths!", None

def enhanced_resume_query(message):
    """Enhanced version of handle_resume_query with more sophisticated prompts"""
    message = message.lower()

    # Special case for the resume help button
    if message == "resume help" or message == "resume assistance":
        return """I can help you create, improve, and optimize your resume! Here's how I can assist:

*Resume Creation & Formatting*
1. *Resume Formats*: I can explain different resume formats (chronological, functional, combination) and when to use each
2. *Resume Templates*: I can provide guidance on effective resume templates and layouts
3. *Section Organization*: I can help you organize your resume sections for maximum impact

*Content Optimization*
1. *Action Verbs & Achievements*: I can help you highlight accomplishments with strong action verbs
2. *Skills Sections*: I can help you create effective technical and soft skills sections
3. *Work Experience*: I can help you describe your experience in impactful ways
4. *Education & Certifications*: I can help you present your educational background effectively

*Special Resume Needs*
1. *ATS Optimization*: I can provide tips to get past Applicant Tracking Systems
2. *Career Change Resumes*: I can help tailor your resume for career transitions
3. *Cover Letters*: I can help you create compelling cover letters to accompany your resume
4. *LinkedIn Profiles*: I can help align your LinkedIn profile with your resume

*Resume Review*
- Upload your resume and I can provide specific feedback on improving it

What specific aspect of resume help would you like assistance with?"""

    if "format" in message or "template" in message:
        prompt = "Provide a comprehensive guide on resume formats and templates for job seekers. Include different types of formats, when to use each, and examples of effective templates."
        return handle_llm_query(prompt)

    elif "tips" in message or "advice" in message:
        prompt = "Provide detailed resume writing tips and advice for job seekers. Include information on what to include, what to avoid, how to highlight skills and achievements, and how to tailor a resume for specific roles."
        return handle_llm_query(prompt)

    elif "review" in message or "feedback" in message:
        return "Please upload your resume and I'll review it for clarity, formatting, and impact. I can provide specific feedback on how to improve it."

    elif "ats" in message or "applicant tracking" in message:
        prompt = "Explain how to optimize a resume for Applicant Tracking Systems (ATS). Include tips on keywords, formatting, and common mistakes to avoid."
        return handle_llm_query(prompt)

    elif "cover letter" in message:
        prompt = "Provide guidance on writing effective cover letters. Include structure, content, customization tips, and examples."
        return handle_llm_query(prompt)

    elif "yes" in message or "generate" in message or "outline" in message or "create" in message:
        prompt = "Create a comprehensive resume outline with sections and explanations of what to include in each section. Make it suitable for a variety of professional fields."
        return handle_llm_query(prompt)

    elif "linkedin" in message or "profile" in message:
        prompt = "Provide guidance on creating an effective LinkedIn profile that complements your resume. Include tips for the summary, experience, skills sections, and how to optimize your profile for recruiters."
        return handle_llm_query(prompt)

    elif "career change" in message or "transition" in message:
        prompt = "Provide guidance on creating a resume for career changers. Include tips on highlighting transferable skills, addressing employment gaps, and positioning yourself for a new industry or role."
        return handle_llm_query(prompt)

    elif "skills" in message:
        prompt = "Provide guidance on creating effective skills sections in a resume. Include tips on technical skills, soft skills, how to organize them, and how to match them to job descriptions."
        return handle_llm_query(prompt)

    elif "experience" in message or "work history" in message:
        prompt = "Provide guidance on writing effective work experience sections in a resume. Include tips on describing responsibilities, highlighting achievements, using action verbs, and quantifying results."
        return handle_llm_query(prompt)

    # Default response
    prompt = "Provide a comprehensive guide on creating an effective resume. Include information on format, content, tips for standing out, common mistakes to avoid, and how to tailor a resume for specific roles."
    return handle_llm_query(prompt)

def identify_interview_domain(message):
    """Identify the interview domain from the message"""
    message = message.lower()

    # Check for exact domain mentions
    for domain_key, terms in INTERVIEW_DOMAINS.items():
        for term in terms:
            # Look for the term as a whole word
            if re.search(r'\b' + re.escape(term) + r'\b', message):
                return domain_key

    return None

def identify_interview_aspect(message):
    """Identify the interview aspect from the message"""
    message = message.lower()

    # Check for aspect mentions
    for aspect_key, terms in INTERVIEW_ASPECTS.items():
        for term in terms:
            if re.search(r'\b' + re.escape(term) + r'\b', message):
                return aspect_key

    return "general"  # Default to general interview preparation

def generate_interview_prompt(domain_key, aspect_key):
    """Generate a specific prompt based on the domain and aspect"""
    # Get the canonical name for the domain
    domain_name = INTERVIEW_DOMAINS[domain_key][0]

    # Base prompts for different aspects
    prompts = {
        "questions": f"Provide a comprehensive list of the most common and important interview questions for {domain_name} positions. Include both technical and behavioral questions, and explain what interviewers are looking for in the answers.",

        "technical": f"Explain the key technical concepts, skills, and knowledge that candidates should master for {domain_name} interviews. Include specific topics to study, coding challenges to practice, and technical assessment formats to expect.",

        "behavioral": f"Provide detailed guidance on preparing for behavioral interview questions in {domain_name} roles. Include common scenarios, the STAR method, examples of strong answers, and how to showcase relevant soft skills.",

        "preparation": f"Create a comprehensive 2-week interview preparation plan for {domain_name} positions. Include daily study topics, practice exercises, resources to use, and strategies for different types of interviews.",

        "mock": f"Provide a complete mock interview script for a {domain_name} position, including both technical and behavioral questions, with sample strong answers and explanations of what makes them effective.",

        "salary": f"Explain how to research and negotiate salary for {domain_name} positions. Include salary ranges by experience level, negotiation tactics, discussing benefits, and handling difficult compensation conversations.",

        "remote": f"Provide detailed tips for succeeding in remote/virtual interviews for {domain_name} positions. Include technical setup advice, virtual communication skills, and how to stand out in online interviews.",

        "assessment": f"Explain common technical assessments and take-home challenges for {domain_name} positions. Include types of problems, evaluation criteria, time management strategies, and tips for delivering high-quality solutions.",

        "resume": f"Provide detailed guidance on creating a resume and cover letter specifically for {domain_name} positions. Include key skills to highlight, formatting tips, ATS optimization, and examples of effective bullet points.",

        "portfolio": f"Explain how to build an impressive portfolio for {domain_name} positions. Include project ideas, documentation tips, presentation strategies, and how to discuss your work during interviews.",

        "general": f"Provide comprehensive interview preparation guidance for {domain_name} positions. Include common questions, technical preparation, behavioral preparation, resume tips, and strategies for different interview stages."
    }

    return prompts.get(aspect_key, prompts["general"])

def enhanced_interview_query(message):
    """Enhanced version of handle_interview_query with more sophisticated understanding"""
    message = message.lower()

    # Special case for the interview guidance button
    if message == "interview preparation" or message == "interview tips" or message == "interview help":
        return """I can help you prepare for interviews in many different fields! Here's how I can assist:

1. *Interview Types I Can Help With*:
   - Technical interviews
   - Behavioral interviews
   - Case interviews
   - Remote/virtual interviews
   - Assessment tests and take-home challenges

2. *Fields I Can Provide Interview Advice For*:
   - Software Engineering & Development
   - Data Science & AI
   - Product Management
   - UX/UI Design
   - Business Analysis
   - And many more professional fields

3. *Interview Preparation Areas*:
   - Common interview questions and effective answers
   - Technical preparation and practice problems
   - Behavioral question strategies (STAR method)
   - Research and company preparation
   - Salary negotiation tactics
   - Portfolio presentation tips

Tell me what type of interview you're preparing for and what field it's in, and I'll provide tailored advice to help you succeed!

For example:
- "Help me prepare for a software engineering interview"
- "What behavioral questions should I expect in a product management interview?"
- "How should I prepare for a data science technical assessment?"
"""

    # Try to identify domain and aspect from the message
    domain_key = identify_interview_domain(message)
    aspect_key = identify_interview_aspect(message)

    # If domain found, generate specific prompt
    if domain_key:
        prompt = generate_interview_prompt(domain_key, aspect_key)
        return handle_llm_query(prompt)

    # No specific domain identified - use a general prompt
    if "technical" in message:
        prompt = "Provide guidance on preparing for technical interviews. Include common technical questions, coding challenges, and system design problems."
    elif "behavioral" in message:
        prompt = "Provide guidance on preparing for behavioral interviews. Include common questions, the STAR method, and examples of strong answers."
    elif "question" in message:
        prompt = "List common interview questions and how to answer them effectively. Include both technical and behavioral questions."
    elif "prepare" in message or "preparation" in message:
        prompt = "Provide a comprehensive interview preparation guide. Include research, practice, common questions, and day-of tips."
    elif "salary" in message or "negotiate" in message:
        prompt = "Explain how to research and negotiate salary during interviews. Include timing, tactics, and handling difficult conversations."
    else:
        prompt = "Provide comprehensive interview preparation advice. Include research, common questions, technical preparation, behavioral preparation, and day-of strategies."

    return handle_llm_query(prompt)

# Function to handle general queries that don't fit into specific categories
def handle_general_query(message):
    """Handle general queries using the LLM"""
    # Create a more specific prompt based on the message
    prompt = f"""You are a helpful university assistant chatbot. Provide accurate, concise, and useful information.

The user has asked: '{message}'

Provide a helpful, accurate, and concise response that directly answers the question and offers practical advice when appropriate."""

    return handle_llm_query(prompt)
