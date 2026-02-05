import google.generativeai as genai
import os
from flask import current_app
from typing import Tuple, Optional, Dict

class LLMService:
    """Service to handle LLM interactions and generated responses."""

    @staticmethod
    def call_gemini_api(prompt: str) -> str:
        """Call Google Gemini API as a fallback."""
        api_key = os.environ.get('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY')
        
        if not api_key:
            return (
                "🎓 **Academic Assistance:**\n\n"
                "I'm here to help! Please configure the `GEMINI_API_KEY` to enable "
                "advanced AI responses for this query.\n\n"
                "In the meantime, I can help with:\n"
                "• Career Guidance\n"
                "• Resume Tips\n"
                "• Interview Prep\n"
                "• Study Schedules"
            )

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # University Mentor System Prompt
            system_instruction = (
                "You are UniMentor, a professional, encouraging, and knowledgeable university academic advisor and career counselor. "
                "Your goal is to help students succeed academically and professionally. "
                "Tone: Professional, empathetic, structured, and clear. Avoid slang but remain accessible. "
                "Format: Use Markdown for readability (bullet points, bold text). "
                "If analyzing a document, provide specific, constructive feedback. "
                "If asked about careers, provide realistic and actionable roadmaps. "
                "Always conclude with an encouraging or guiding follow-up question.\n\n"
            )
            
            full_prompt = system_instruction + prompt
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return "⚠️ I'm having trouble connecting to my brain right now. Please try again later."

    @staticmethod
    def handle_llm_query(prompt: str) -> str:
        """
        Handle LLM queries with a fallback response.
        If no static rule matches, use Gemini API.
        """
        prompt_lower = prompt.lower()
        
        # Bypass static responses for direct analysis requests (coming from internal methods)
        if prompt.strip().startswith("Please analyze") or prompt.strip().startswith("Generate"):
             return LLMService.call_gemini_api(prompt)
        
        if "career" in prompt_lower:
            return LLMService.generate_career_response(prompt)
        elif "resume" in prompt_lower:
            return LLMService.generate_resume_response(prompt)
        elif "interview" in prompt_lower:
            return LLMService.generate_interview_response(prompt)
        elif "project" in prompt_lower:
            return LLMService.generate_project_response(prompt)
        elif "timetable" in prompt_lower or "schedule" in prompt_lower:
            return LLMService.generate_schedule_response(prompt)
        elif "backlog" in prompt_lower:
            return LLMService.generate_backlog_response(prompt)
        else:
            # Fallback to Gemini instead of general static response
            return LLMService.call_gemini_api(prompt)

    # --- Response Generators (from backend/model.py & main.py) ---
    # Kept for specific structured responses, but could also be replaced by Gemini if desired.
    # User asked: "if static response doesnt match it should redirect to google gemini api"
    # So we keep specific handlers and only fallback on the rest.

    @staticmethod
    def generate_career_response(prompt: str) -> str:
        return (
            "🎯 **Career Guidance:**\n\n"
            "Based on your query, here are some career suggestions:\n"
            "• Research current industry trends in your field of interest\n"
            "• Build relevant skills through online courses and certifications\n"
            "• Network with professionals in your target industry\n"
            "• Consider internships or entry-level positions to gain experience\n"
            "• Keep your resume updated with latest projects and achievements\n\n"
            "Would you like specific advice for a particular field?"
        )

    @staticmethod
    def generate_resume_response(prompt: str) -> str:
        return (
            "📝 **Resume Tips:**\n\n"
            "• Keep it concise (1-2 pages maximum)\n"
            "• Use action verbs and quantify achievements\n"
            "• Tailor your resume for each job application\n"
            "• Include relevant technical skills and certifications\n"
            "• Proofread carefully for grammar and formatting\n"
            "• Use a clean, professional layout\n\n"
            "Upload your resume for personalized feedback!"
        )

    @staticmethod
    def generate_interview_response(prompt: str) -> str:
        return (
            "🤝 **Interview Preparation:**\n\n"
            "• Research the company and role thoroughly\n"
            "• Practice common interview questions\n"
            "• Prepare specific examples using the STAR method\n"
            "• Dress professionally and arrive early\n"
            "• Prepare thoughtful questions about the role and company\n"
            "• Follow up with a thank-you email\n\n"
            "Would you like help with specific interview questions?"
        )

    @staticmethod
    def generate_project_response(prompt: str) -> str:
        return (
            "🚀 **Project Ideas:**\n\n"
            "Here are some general project suggestions:\n"
            "• Web application with user authentication\n"
            "• Data analysis and visualization project\n"
            "• Mobile app solving a real-world problem\n"
            "• Machine learning model for prediction\n"
            "• IoT project with sensor integration\n\n"
            "What field are you interested in for more specific suggestions?"
        )

    @staticmethod
    def generate_schedule_response(prompt: str) -> str:
        return (
            "📅 **Study Schedule Tips:**\n\n"
            "• Block time for each subject based on difficulty\n"
            "• Include regular breaks (Pomodoro technique)\n"
            "• Schedule review sessions before exams\n"
            "• Balance study time with extracurricular activities\n"
            "• Set realistic daily and weekly goals\n"
            "• Track your progress and adjust as needed\n\n"
            "Share your subjects and available time for a personalized schedule!"
        )

    @staticmethod
    def generate_backlog_response(prompt: str) -> str:
        return (
            "📚 **Backlog Management:**\n\n"
            "• Prioritize subjects by difficulty and importance\n"
            "• Break large topics into smaller, manageable chunks\n"
            "• Create a realistic timeline with milestones\n"
            "• Focus on understanding concepts, not just memorization\n"
            "• Seek help from teachers or peers when stuck\n"
            "• Use active learning techniques (practice problems, teaching others)\n\n"
            "What subjects do you need help catching up on?"
        )

    @staticmethod
    def generate_general_response(prompt: str) -> str:
        # This method is now effectively replaced by call_gemini_api in the main handler,
        # but kept if referenced elsewhere or for specific sub-logic.
        # But handle_general_query (below) still uses it.
        # Actually, let's make handle_general_query ALSO fallback to Gemini.
        return LLMService.call_gemini_api(prompt)
    
    # --- Enhanced Queries (from backend/model.py) ---
    
    @staticmethod
    def enhanced_career_query(message: str, last_domain: Optional[str] = None) -> Tuple[str, Optional[str]]:
        message_lower = message.lower()
        
        # Career roadmap queries
        if "roadmap" in message_lower or "path" in message_lower:
            if "software" in message_lower or "programming" in message_lower:
                return (
                    """
🛣️ **Software Development Career Roadmap:**

**Beginner Level (0-1 year):**
• Learn programming fundamentals (Python/JavaScript)
• Understand data structures and algorithms
• Build basic projects (calculator, to-do app)
• Learn version control (Git/GitHub)

**Intermediate Level (1-3 years):**
• Master a web framework (React, Django, Flask)
• Learn databases (SQL, NoSQL)
• Build full-stack applications
• Contribute to open-source projects

**Advanced Level (3+ years):**
• System design and architecture
• Cloud platforms (AWS, Azure, GCP)
• DevOps and CI/CD
• Leadership and mentoring skills

**Specialization Options:**
• Frontend Development
• Backend Development
• Full-Stack Development
• DevOps Engineering
• Data Science/ML Engineering
                    """.strip(), 
                    "software"
                )
            elif "data" in message_lower or "analytics" in message_lower:
                return (
                    """
📊 **Data Science Career Roadmap:**

**Foundation (0-6 months):**
• Statistics and probability
• Python/R programming
• SQL and database basics
• Excel/Google Sheets proficiency

**Core Skills (6-18 months):**
• Data manipulation (Pandas, NumPy)
• Data visualization (Matplotlib, Seaborn, Tableau)
• Machine learning basics (Scikit-learn)
• Statistical analysis

**Advanced Skills (18+ months):**
• Deep learning (TensorFlow, PyTorch)
• Big data tools (Spark, Hadoop)
• Cloud platforms for ML
• MLOps and model deployment

**Career Paths:**
• Data Analyst
• Data Scientist
• ML Engineer
• Business Intelligence Analyst
                    """.strip(), 
                    "data"
                )

        # Job search queries
        elif "job" in message_lower and ("search" in message_lower or "find" in message_lower):
            return (
                """
🔍 **Job Search Strategy:**

**Preparation Phase:**
• Update and optimize your resume
• Build a strong LinkedIn profile
• Create a portfolio showcasing your work
• Practice coding problems (if technical role)

**Search Channels:**
• Job boards (LinkedIn, Indeed, Glassdoor)
• Company websites directly
• Professional networking events
• Referrals from connections
• Recruitment agencies

**Application Process:**
• Tailor resume for each application
• Write compelling cover letters
• Follow up professionally
• Prepare for different interview formats

**Interview Preparation:**
• Research the company thoroughly
• Practice common interview questions
• Prepare technical examples (STAR method)
• Have questions ready for the interviewer
                """.strip(), 
                "job_search"
            )

        # Salary and compensation
        elif "salary" in message_lower or "compensation" in message_lower:
            return (
                 """
💰 **Career Compensation Guide:**

**Research Your Worth:**
• Use salary comparison sites (Glassdoor, PayScale)
• Consider location and cost of living
• Factor in experience level and skills
• Research industry standards

**Negotiation Tips:**
• Know your market value
• Highlight your unique contributions
• Consider total compensation package
• Be prepared to justify your request

**Beyond Base Salary:**
• Health insurance and benefits
• Retirement contributions (401k, PF)
• Stock options or equity
• Professional development budget
• Flexible work arrangements

**Career Growth Impact:**
• Continuous skill development
• Industry certifications
• Leadership experience
• Network building
                """.strip(), 
                "compensation"
            )
        
        else:
            return (
                """
🎯 **General Career Guidance:**

**Self-Assessment:**
• Identify your strengths and interests
• Assess current skills and gaps
• Define short and long-term goals
• Consider work-life balance preferences

**Skill Development:**
• Stay updated with industry trends
• Pursue relevant certifications
• Build both technical and soft skills
• Seek mentorship opportunities

**Professional Growth:**
• Network within your industry
• Attend conferences and workshops
• Contribute to professional communities
• Document your achievements

**Career Planning:**
• Set SMART career goals
• Create a development timeline
• Regularly review and adjust plans
• Seek feedback from supervisors

How can I help you with a specific aspect of your career journey?
                """.strip(), 
                "general"
            )

    @staticmethod
    def enhanced_resume_query(message: str) -> str:
        message_lower = message.lower()
        
        if "format" in message_lower or "template" in message_lower:
            return """
📝 **Resume Format & Template Guide:**

**Standard Resume Structure:**
1. **Header Section:**
   • Full name (larger font)
   • Phone number and email
   • LinkedIn profile URL
   • Location (city, state)

2. **Professional Summary (2-3 lines):**
   • Brief overview of experience
   • Key skills and strengths
   • Career objectives

3. **Core Sections:**
   • Work Experience (reverse chronological)
   • Education
   • Technical Skills
   • Projects (especially for students/new grads)

4. **Optional Sections:**
   • Certifications
   • Awards and Achievements
   • Volunteer Experience
   • Publications

**Formatting Tips:**
• Use consistent fonts (Arial, Calibri, Times New Roman)
• Keep font size 10-12pt
• Use bullet points for easy scanning
• Maintain consistent spacing
• Keep to 1-2 pages maximum
• Use action verbs to start bullet points

Would you like me to generate a resume outline for your specific field?
            """.strip()

        elif "skills" in message_lower:
            return """
🛠️ **Skills Section Optimization:**

**Technical Skills Categories:**
• Programming Languages: Python, Java, JavaScript
• Frameworks: React, Django, Flask, Node.js
• Databases: MySQL, PostgreSQL, MongoDB
• Tools: Git, Docker, AWS, Jenkins
• Operating Systems: Linux, Windows, macOS

**Soft Skills (integrate into experience):**
• Leadership and team management
• Problem-solving and analytical thinking
• Communication and presentation
• Project management
• Adaptability and learning agility

**Skills Presentation Tips:**
• Group similar skills together
• List proficiency levels if relevant
• Include years of experience
• Prioritize skills relevant to target job
• Update regularly with new skills

**Skills to Highlight by Field:**
• Software Development: Programming languages, frameworks, databases
• Data Science: Python/R, ML libraries, statistical tools
• Marketing: Analytics tools, CRM systems, content creation
• Finance: Excel, financial modeling, regulatory knowledge
            """.strip()

        elif "experience" in message_lower or "work" in message_lower:
            return """
💼 **Work Experience Section Guide:**

**Format for Each Role:**
• Job Title | Company Name | Location | Dates
• 3-5 bullet points describing achievements
• Use action verbs and quantify results
• Focus on impact, not just responsibilities

**Action Verbs by Category:**
• Leadership: Led, Managed, Directed, Coordinated
• Achievement: Achieved, Accomplished, Delivered, Exceeded
• Improvement: Optimized, Enhanced, Streamlined, Reduced
• Creation: Developed, Built, Designed, Implemented

**Quantifying Achievements:**
• Use numbers, percentages, dollar amounts
• "Increased sales by 25%" vs "Helped increase sales"
• "Managed team of 8 developers" vs "Managed team"
• "Reduced processing time by 40%" vs "Improved efficiency"

**For Students/New Grads:**
• Include internships, part-time jobs, projects
• Emphasize transferable skills
• Highlight academic achievements
• Include relevant coursework if applicable
            """.strip()

        elif "ats" in message_lower or "applicant tracking" in message_lower:
            return """
🤖 **ATS (Applicant Tracking System) Optimization:**

**ATS-Friendly Formatting:**
• Use standard fonts (Arial, Calibri, Times New Roman)
• Avoid images, graphics, and complex formatting
• Use standard section headings
• Save as .docx or .pdf (check job posting)
• Use simple bullet points (•, -, *)

**Keyword Optimization:**
• Mirror job posting language
• Include relevant technical terms
• Use industry-standard job titles
• Include both acronyms and full terms (AI, Artificial Intelligence)
• Naturally integrate keywords into content

**Section Headers to Use:**
• Work Experience (not "Professional Experience")
• Education (not "Academic Background")
• Skills (not "Core Competencies")
• Certifications (not "Professional Development")

**Common ATS Mistakes to Avoid:**
• Headers and footers with important info
• Tables and columns for layout
• Fancy fonts or formatting
• Images or logos
• Text in graphics
            """.strip()

        else:
            return """
📋 **General Resume Tips:**

**Content Guidelines:**
• Tailor resume for each job application
• Use active voice and strong action verbs
• Quantify achievements with specific metrics
• Keep descriptions concise but impactful
• Proofread carefully for errors

**What to Include:**
• Relevant work experience and internships
• Education (GPA if 3.5+ and recent grad)
• Technical and relevant skills
• Significant projects and achievements
• Professional certifications

**What to Avoid:**
• Personal information (age, marital status, photo)
• Irrelevant work experience
• Outdated or basic skills
• Negative language or explanations for gaps
• Unprofessional email addresses

**Final Checklist:**
✓ Contact information is current
✓ No spelling or grammar errors
✓ Consistent formatting throughout
✓ Relevant keywords from job posting
✓ Quantified achievements where possible
✓ Professional email address
✓ Appropriate length (1-2 pages)

Upload your resume for personalized feedback!
            """.strip()

    @staticmethod
    def enhanced_interview_query(message: str) -> str:
        message_lower = message.lower()
        
        if "technical" in message_lower:
            return """
💻 **Technical Interview Preparation:**

**Common Technical Interview Formats:**
• Coding challenges (algorithms, data structures)
• System design questions
• Technical knowledge assessment
• Code review and debugging
• Take-home assignments

**Preparation Strategy:**
• Practice coding problems daily (LeetCode, HackerRank)
• Review fundamental concepts (Big O, data structures)
• Study system design principles
• Prepare to explain your projects in detail
• Practice coding on whiteboard/shared screen

**Key Topics to Review:**
• Arrays, strings, linked lists
• Trees and graphs
• Sorting and searching algorithms
• Dynamic programming
• Database design and SQL
• Object-oriented programming

**During the Interview:**
• Think out loud while solving problems
• Ask clarifying questions
• Start with brute force, then optimize
• Test your solution with examples
• Discuss trade-offs and alternatives

**Common Technical Questions:**
• "Explain the difference between..."
• "How would you design..."
• "What's the time complexity of..."
• "Walk me through your approach to..."
            """.strip()

        elif "behavioral" in message_lower:
            return """
🗣️ **Behavioral Interview Preparation:**

**STAR Method Framework:**
• **Situation:** Set the context
• **Task:** Describe your responsibility
• **Action:** Explain what you did
• **Result:** Share the outcome

**Common Behavioral Questions:**
• "Tell me about a time you faced a challenge"
• "Describe a situation where you had to work with a difficult team member"
• "Give an example of when you showed leadership"
• "Tell me about a mistake you made and how you handled it"
• "Describe a time you had to learn something quickly"

**Preparation Tips:**
• Prepare 5-7 STAR stories covering different scenarios
• Include examples of leadership, teamwork, problem-solving
• Practice telling stories concisely (2-3 minutes each)
• Prepare examples from work, school, and personal projects
• Focus on your specific contributions and learnings

**Key Themes to Address:**
• Leadership and initiative
• Problem-solving and analytical thinking
• Teamwork and collaboration
• Adaptability and learning
• Communication and conflict resolution
• Time management and prioritization
            """.strip()

        elif "questions" in message_lower and "ask" in message_lower:
            return """
❓ **Questions to Ask the Interviewer:**

**About the Role:**
• "What does a typical day look like in this position?"
• "What are the biggest challenges facing the team right now?"
• "How do you measure success in this role?"
• "What opportunities are there for professional development?"

**About the Team:**
• "Can you tell me about the team I'd be working with?"
• "How does the team collaborate on projects?"
• "What's the management style like?"
• "How does the team handle work-life balance?"

**About the Company:**
• "What excites you most about working here?"
• "How has the company changed since you joined?"
• "What are the company's goals for the next year?"
• "How does the company support employee growth?"

**About Next Steps:**
• "What are the next steps in the interview process?"
• "When can I expect to hear back?"
• "Is there anything else you'd like to know about my background?"

**Questions to Avoid:**
• Salary and benefits (save for later rounds)
• Basic company information (research beforehand)
• Negative questions about the company
• Personal questions about the interviewer
            """.strip()

        else:
            return """
🎯 **General Interview Preparation:**

**Before the Interview:**
• Research the company thoroughly
• Review the job description carefully
• Prepare your elevator pitch (30-60 seconds)
• Plan your outfit and route
• Prepare questions to ask the interviewer

**Day of Interview:**
• Arrive 10-15 minutes early
• Bring multiple copies of your resume
• Bring a notebook and pen
• Turn off your phone
• Greet everyone professionally

**During the Interview:**
• Make eye contact and smile
• Listen actively to questions
• Take a moment to think before answering
• Be specific with examples
• Show enthusiasm for the role

**Common Interview Questions:**
• "Tell me about yourself"
• "Why are you interested in this position?"
• "What are your strengths and weaknesses?"
• "Where do you see yourself in 5 years?"
• "Why are you leaving your current job?"

**After the Interview:**
• Send a thank-you email within 24 hours
• Reiterate your interest in the position
• Address any concerns that came up
• Follow up appropriately if you don't hear back

**Red Flags to Watch For:**
• Vague job descriptions
• High turnover rates
• Poor communication during process
• Unrealistic expectations or demands
            """.strip()

    @staticmethod
    def handle_general_query(message: str) -> str:
        message_lower = message.lower()
        
        # Study-related queries
        if any(word in message_lower for word in ["study", "learn", "education", "academic"]):
            return """
📚 **Academic Success Tips:**

**Effective Study Strategies:**
• Use active learning techniques (summarizing, teaching others)
• Practice spaced repetition for better retention
• Create a dedicated study environment
• Break study sessions into manageable chunks
• Use the Pomodoro Technique (25-min focused sessions)

**Time Management:**
• Create a study schedule and stick to it
• Prioritize tasks by importance and deadlines
• Eliminate distractions during study time
• Take regular breaks to maintain focus
• Plan ahead for exams and assignments

**Note-Taking Tips:**
• Use structured formats (Cornell notes, mind maps)
• Review and revise notes regularly
• Combine visual and textual elements
• Create summaries of key concepts
• Use digital tools for organization

**Exam Preparation:**
• Start preparing well in advance
• Practice with past papers and mock tests
• Form study groups for discussion
• Seek help from teachers when needed
• Maintain a healthy sleep schedule

How can I help you with your specific academic goals?
            """.strip()
        
        # Motivation and productivity
        elif any(word in message_lower for word in ["motivation", "productivity", "focus", "procrastination"]):
            return """
🚀 **Motivation & Productivity Tips:**

**Overcoming Procrastination:**
• Break large tasks into smaller, manageable steps
• Use the "2-minute rule" for quick tasks
• Set specific, achievable goals
• Create accountability systems
• Reward yourself for completing tasks

**Maintaining Focus:**
• Eliminate distractions (phone, social media)
• Use time-blocking techniques
• Practice mindfulness and meditation
• Take regular breaks to recharge
• Create a conducive work environment

**Building Motivation:**
• Connect tasks to your long-term goals
• Visualize success and outcomes
• Celebrate small wins along the way
• Find an accountability partner
• Remember your "why" for pursuing goals

**Productivity Systems:**
• Getting Things Done (GTD)
• Eisenhower Matrix for prioritization
• Kanban boards for task management
• Time-blocking for schedule management
• Regular review and adjustment of systems

What specific area would you like help with?
            """.strip()
        
        # Default academic response
        else:
            return """
🎓 **Academic & Career Assistance:**

I'm here to help you succeed in your academic and professional journey! Here's how I can assist:

**📄 Document Analysis:**
• PDF summarization and note generation
• Resume review and optimization
• Academic paper analysis

**💼 Career Development:**
• Career path guidance and roadmaps
• Job search strategies
• Interview preparation
• Professional skill development

**📚 Academic Support:**
• Study planning and time management
• Project ideas and guidance
• Course selection advice
• Exam preparation strategies

**🎯 Specialized Areas:**
• Technical interview preparation
• Resume writing and formatting
• Academic research assistance
• Professional networking tips

Please let me know what specific area you'd like help with, and I'll provide detailed guidance tailored to your needs!
            """.strip()

    # --- Methods from lm_module.py that involve "LLM" prompt engineering ---
    
    @staticmethod
    def query_with_pdf_context(query: str, context: str, context_length: int = 2000) -> str:
        if not context:
            return "❌ No PDF context available. Please upload a PDF first."
        
        # Truncate context if too long
        truncated_context = context[:context_length] if len(context) > context_length else context
        
        # Create enhanced prompt with PDF context
        enhanced_prompt = f"""
        PDF Context:
        {truncated_context}
        
        User Query: {query}
        
        Please answer the query based on the PDF content provided above.
        """
        
        return LLMService.handle_llm_query(enhanced_prompt)

    @staticmethod
    def summarize_pdf_content(context: str, max_length: int = 500) -> str:
        if not context:
            return "❌ No PDF content available to summarize."
        
        # Create summary prompt
        prompt = f"""
        Please provide a concise summary of the following document:
        
        {context[:3000]}  # Limit context for summary
        
        Summary should be approximately {max_length} words and cover the main points.
        """
        
        return LLMService.handle_llm_query(prompt)

    @staticmethod
    def generate_study_notes(context: str, topic_focus: Optional[str] = None) -> str:
        if not context:
            return "❌ No PDF content available for note generation."
        
        focus_instruction = f" Focus specifically on: {topic_focus}" if topic_focus else ""
        
        prompt = f"""
        Generate comprehensive study notes from the following document:{focus_instruction}
        
        Document content:
        {context[:4000]}  # Limit context for notes
        
        Please format the notes with:
        - Key concepts and definitions
        - Important points and highlights
        - Structured bullet points
        - Clear headings and subheadings
        """
        
        return LLMService.handle_llm_query(prompt)

    @staticmethod
    def analyze_resume_content(context: str) -> str:
        if not context:
            return "❌ No resume content available for analysis."
        
        prompt = f"""
        Please analyze this resume and provide constructive feedback:
        
        Resume content:
        {context}
        
        Please provide feedback on:
        - Overall structure and formatting
        - Content clarity and impact
        - Skills presentation
        - Experience description
        - Areas for improvement
        - Strengths to highlight
        """
        
        return LLMService.handle_llm_query(prompt)

    @staticmethod
    def extract_key_information(context: str, info_type: str = "general") -> str:
        if not context:
            return "❌ No PDF content available for information extraction."
        
        if info_type == "technical":
            prompt = f"Extract all technical terms, technologies, and technical concepts from: {context[:2000]}"
        elif info_type == "dates":
            prompt = f"Extract all dates, deadlines, and time-related information from: {context[:2000]}"
        elif info_type == "names":
            prompt = f"Extract all names, organizations, and proper nouns from: {context[:2000]}"
        else:
            prompt = f"Extract the most important information and key points from: {context[:2000]}"
        
        return LLMService.handle_llm_query(prompt)
