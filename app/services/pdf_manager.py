import io
import os
from typing import Optional, Union, Dict
from datetime import datetime
from app.services.gemini_service import GeminiService

class PDFManager:
    """Service to handle PDF file processing operation."""

    @staticmethod
    def extract_text(pdf_data: Union[bytes, str]) -> str:
        """Extract text from PDF file."""
        try:
            # Try to import PyPDF2 for PDF processing
            try:
                import PyPDF2
                
                if isinstance(pdf_data, bytes):
                    pdf_file = io.BytesIO(pdf_data)
                else:
                    pdf_file = open(pdf_data, 'rb')
                
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                
                for page in pdf_reader.pages:
                    text_page = page.extract_text()
                    if text_page:
                        text += text_page + "\n"
                
                if isinstance(pdf_data, str):
                    pdf_file.close()
                    
                return text.strip()
                
            except ImportError:
                # Fallback: Mock PDF text extraction if check fails
                return """
                This is a sample PDF content for development purposes. (PyPDF2 not found)
                
                Key Points:
                • Sample bullet point 1
                • Sample bullet point 2
                
                Please install PyPDF2 to enable real PDF extraction.
                """
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

    @staticmethod
    def generate_summary(context: str, save_to_file: bool = False, generate_pdf: bool = False) -> str:
        """Generate a summary of the PDF content."""
        if not context or not context.strip():
            return "❌ No PDF content available to summarize. Please upload a PDF first."
        
        try:
            # Avoid circular import
            from app.services.mentor_service import MentorService
            
            # summary = LLMService.summarize_pdf_content(context)
            prompt = f"{MentorService.SYSTEM_PROMPT}\n\nTask: Provide a comprehensive SUMMARY of this document.\nHighlight key concepts and takeaways.\n\nDocument Content:\n{context[:20000]}"
            summary = GeminiService.generate_response(prompt)
            
            # Add metadata
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_summary = f"""
# 📄 PDF Summary
**Generated on**: {timestamp}

{summary}

---
**📊 Document Statistics:**
* Characters: {len(context):,}
* Words: {len(context.split()):,}
* Estimated pages: {max(1, len(context) // 2000)}
            """.strip()
            
            # Save to file if requested
            if save_to_file:
                filename = f"pdf_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(formatted_summary)
                    formatted_summary += f"\n\n✅ Summary saved to: {filename}"
                except Exception as e:
                    formatted_summary += f"\n\n⚠️ Could not save file: {str(e)}"
            
            # Generate PDF if requested
            if generate_pdf:
                pdf_result = PDFManager.generate_summary_pdf(formatted_summary)
                formatted_summary += f"\n\n{pdf_result}"
            
            return formatted_summary
            
        except Exception as e:
            return f"❌ Error generating summary: {str(e)}"

    @staticmethod
    def generate_notes(context: str, topic_focus: Optional[str] = None) -> str:
        """Generate study notes from PDF content."""
        if not context or not context.strip():
            return "❌ No PDF content available for note generation."
        
        try:
            # Avoid circular import
            from app.services.mentor_service import MentorService
            
            # notes = LLMService.generate_study_notes(context, topic_focus)
            focus_text = f"Focus specifically on: {topic_focus}" if topic_focus else "Cover all key topics."
            prompt = f"{MentorService.SYSTEM_PROMPT}\n\nTask: Create detailed STUDY NOTES from this document.\n{focus_text}\nUse bullet points, bold key terms, and explain complex concepts clearly.\n\nDocument Content:\n{context[:20000]}"
            notes = GeminiService.generate_response(prompt)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_notes = f"""
# 📚 Study Notes
**Generated on**: {timestamp}
{f"**Focus**: {topic_focus}" if topic_focus else ""}

{notes}

---
**📖 Source Document Info:**
* Total characters: {len(context):,}
* Total words: {len(context.split()):,}
* Estimated reading time: {max(1, len(context.split()) // 200)} minutes
            """.strip()
            
            return formatted_notes
            
        except Exception as e:
            return f"❌ Error generating notes: {str(e)}"

    @staticmethod
    def analyze_content(context: str, analysis_type: str = "general") -> str:
        """Analyze PDF content for specific information."""
        if not context or not context.strip():
            return "❌ No PDF content available for analysis."
        
        try:
            
            if analysis_type == "technical":
                result = LLMService.extract_key_information(context, "technical")
                title = "🔧 **Technical Analysis**"
            elif analysis_type == "academic":
                result = LLMService.extract_key_information(context, "general")
                title = "🎓 **Academic Analysis**"
            elif analysis_type == "dates":
                result = LLMService.extract_key_information(context, "dates")
                title = "📅 **Date & Timeline Analysis**"
            else:
                result = LLMService.extract_key_information(context, "general")
                title = "📋 **General Analysis**"
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return f"""
{title}
Generated on: {timestamp}

{result}

---
📊 **Document Overview:**
• Content length: {len(context):,} characters
• Word count: {len(context.split()):,}
• Analysis type: {analysis_type.title()}
            """.strip()
            
        except Exception as e:
            return f"❌ Error analyzing content: {str(e)}"

    @staticmethod
    def generate_summary_pdf(content: str) -> str:
        """Generate a PDF file from summary content."""
        try:
            # Try to import reportlab for PDF generation
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                
                filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                doc = SimpleDocTemplate(filename, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                # Convert content to PDF paragraphs
                for line in content.split('\n'):
                    if line.strip():
                        story.append(Paragraph(line, styles['Normal']))
                        story.append(Spacer(1, 12))
                
                doc.build(story)
                return f"📄 PDF generated: {filename}"
                
            except ImportError:
                # Fallback: Save as text file
                filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"📄 Text file generated: {filename} (Install reportlab for PDF generation)"
                
        except Exception as e:
            return f"⚠️ Could not generate PDF: {str(e)}"
