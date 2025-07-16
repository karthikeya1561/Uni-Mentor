import fitz  # PyMuPDF is imported as fitz
import re
import os
import datetime
from tqdm import tqdm
import numpy as np
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from pdf_generator import generate_pdf_from_summary

# Global cache
cached_pages = {}
cached_text = ""

# Add caching for summarization results
summary_cache = {}

# ========== TEXT EXTRACTION ==========

def extract_text_from_pdf(file_bytes):
    global cached_pages, cached_text
    cached_pages.clear()
    cached_text = ""

    file_stream = BytesIO(file_bytes)
    doc = fitz.open(stream=file_stream, filetype="pdf")
    for i, page in enumerate(tqdm(doc, desc="📄 Extracting text")):
        page_text = page.get_text()
        cached_pages[i + 1] = page_text.strip()
        cached_text += page_text + "\n"

    return cached_text

# ========== SUMMARIZATION HELPERS ==========

def split_text_by_tokens(paragraphs, max_tokens=1024):
    """Split text into chunks, optimized for speed"""
    # Use a smaller max_tokens for faster processing
    max_tokens = min(max_tokens, 512)  # Limit to 512 tokens for speed

    chunks = []
    current_chunk = ""
    current_token_count = 0

    # Estimate token count without calling tokenizer for every paragraph
    # Rough estimate: 1 token ≈ 4 characters for English text
    chars_per_token = 4

    for para in paragraphs:
        # Quick estimate of token count
        para_token_estimate = len(para) // chars_per_token

        if current_token_count + para_token_estimate <= max_tokens:
            # If our estimate says it fits, add it
            if current_chunk:
                current_chunk += " " + para
            else:
                current_chunk = para
            current_token_count += para_token_estimate
        else:
            # If it doesn't fit, start a new chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
            current_token_count = para_token_estimate

    # Add the last chunk if there is one
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def extract_heading(text):
    lines = text.strip().split('\n')
    first_line = lines[0]
    return re.sub(r'[^a-zA-Z0-9\s]', '', first_line).strip().title()

# ========== MAIN SUMMARIZATION ==========

def cached_summarize(text, max_length=250, min_length=30, use_groq=False, groq_client=None):
    """Cached summarization to avoid redundant processing"""
    # Create a cache key based on the text and parameters
    cache_key = f"{hash(text)}-{max_length}-{min_length}-{use_groq}"

    # Check if we have a cached result
    if cache_key in summary_cache:
        return summary_cache[cache_key]

    # Try to use Groq API for better summarization if available
    if use_groq and groq_client:
        try:
            prompt = f"""
            Please summarize the following text in a clear, concise manner.
            Focus on extracting the key points and main ideas.
            Text to summarize: {text}
            """

            completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-8b-8192",
                max_tokens=max_length,
                temperature=0.3,
            )

            result = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error using Groq API: {e}")
            # Fallback to simple summarization
            sentences = re.split(r'(?<=[.!?]) +', text)
            result = " ".join(sentences[:3])  # Just use first 3 sentences as fallback
    else:
        # Use simple summarization as fallback
        sentences = re.split(r'(?<=[.!?]) +', text)
        result = " ".join(sentences[:3])  # Just use first 3 sentences as fallback

    # Store in cache for future use
    summary_cache[cache_key] = result

    return result

def summarize_text(paragraphs):
    # Limit the number of chunks to process for speed
    MAX_CHUNKS = 10

    # Get smaller chunks for faster processing
    chunks = split_text_by_tokens(paragraphs)

    # If we have too many chunks, sample them strategically
    if len(chunks) > MAX_CHUNKS:
        # Always include first and last chunks
        sampled_chunks = [chunks[0], chunks[-1]]

        # Sample evenly from the middle
        step = (len(chunks) - 2) // (MAX_CHUNKS - 2)
        for i in range(1, len(chunks) - 1, step):
            if len(sampled_chunks) < MAX_CHUNKS:
                sampled_chunks.append(chunks[i])

        chunks = sampled_chunks

    # Get current date for the summary
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Extract a potential document title from the first paragraph
    doc_title = "Document Summary"
    if paragraphs and len(paragraphs) > 0:
        first_para = paragraphs[0].strip()
        if len(first_para) < 100:  # Reasonable length for a title
            doc_title = first_para

    # Try to use Groq API for better summarization if available
    groq_client = None
    use_groq = False
    try:
        from groq import Groq
        groq_client = Groq(api_key="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")
        use_groq = True
        print("✅ Using Groq API for enhanced summarization")
    except Exception as e:
        print(f"❌ Groq API not available: {e}")
        use_groq = False

    # Start building the summary with the new format
    final_output = "# 📚 " + doc_title.upper() + "\n\n\n"

    # Process chunks to get topic titles first (for table of contents)
    # We'll store the processed chunks and their summaries for later use
    chunk_summaries = []
    topic_titles = []

    # Use tqdm to show progress
    for i, chunk in enumerate(tqdm(chunks, desc="🧠 Summarizing")):
        # Use cached summarization
        summary = cached_summarize(chunk, max_length=200, min_length=30, use_groq=use_groq, groq_client=groq_client)
        summary_sentences = re.split(r'(?<=[.!?]) +', summary)
        topic_title = extract_heading(chunk) or f"Topic {i+1}"

        # Try to generate a better heading with Groq if available
        if use_groq and groq_client:
            try:
                # Create a prompt for better heading
                prompt = f"""
                Create a concise, accurate heading (3-6 words) for this section of text.
                The heading should clearly represent the main topic discussed.

                Text: {chunk[:1000]}

                Important instructions:
                1. Return ONLY the heading text, nothing else
                2. Make it specific and descriptive
                3. Do not use generic headings like "Introduction" or "Topic"
                4. No explanatory text or meta-language
                """

                completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    max_tokens=20,
                    temperature=0.3,
                )

                better_heading = completion.choices[0].message.content.strip()

                # Use the better heading if it's not empty and not too long
                if better_heading and len(better_heading) < 50:
                    topic_title = better_heading
            except Exception as e:
                print(f"Error generating better heading: {e}")
                # Keep the original topic_title

        # Store for later use
        chunk_summaries.append((i, topic_title, summary_sentences))
        topic_titles.append(topic_title)

    # Add Table of Contents with topic names
    final_output += "## Table of Contents\n\n"
    final_output += "1. [Introduction](#introduction)\n"
    final_output += "2. [Topic-Wise Summarization](#topic-wise-summarization)\n"

    # Add subtopics to the table of contents
    for i, title in enumerate(topic_titles):
        # Create a link-friendly anchor from the title
        anchor = title.lower().replace(' ', '-').replace('/', '').replace('(', '').replace(')', '')
        anchor = re.sub(r'[^a-z0-9-]', '', anchor)  # Remove any other special characters
        final_output += f"   - [2.{i+1}. {title}](#{anchor})\n"

    final_output += "3. [Important Terms and Abbreviations](#important-terms-and-abbreviations)\n"
    final_output += "4. [Conclusion / Final Summary](#conclusion--final-summary)\n\n\n"

    # Add Introduction section
    final_output += "## Introduction\n\n"

    # Extract the main idea from the first chunk's summary for the introduction
    if chunks:
        main_idea_chunk = chunks[0]

        # Use Groq with specific instructions for the introduction
        if use_groq and groq_client:
            try:
                prompt = f"""
                Provide a concise introduction (3-4 sentences) for this document about {doc_title}.
                Focus on the main purpose and key concepts.

                Text to summarize: {main_idea_chunk[:2000]}

                Important instructions:
                1. Start directly with the content - NO phrases like "This document..." or "Here is..."
                2. Be direct, technical, and informative
                3. Do not use meta-language about the summary itself
                4. Focus only on the document's content
                """

                completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    max_tokens=150,
                    temperature=0.3,
                )

                intro_text = completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error generating introduction: {e}")
                # Fallback to regular summarization
                main_idea_summary = cached_summarize(main_idea_chunk, max_length=100, min_length=30, use_groq=use_groq, groq_client=groq_client)

                # Format the introduction with proper line breaks for readability
                sentences = re.split(r'(?<=[.!?]) +', main_idea_summary)
                intro_text = ""

                for sentence in sentences[:3]:  # Limit to 3-5 sentences for introduction
                    if sentence.strip():
                        intro_text += f"{sentence.strip()}. "
        else:
            # Fallback to regular summarization
            main_idea_summary = cached_summarize(main_idea_chunk, max_length=100, min_length=30, use_groq=use_groq, groq_client=groq_client)

            # Format the introduction with proper line breaks for readability
            sentences = re.split(r'(?<=[.!?]) +', main_idea_summary)
            intro_text = ""

            for sentence in sentences[:3]:  # Limit to 3-5 sentences for introduction
                if sentence.strip():
                    intro_text += f"{sentence.strip()}. "

        final_output += intro_text + "\n\n"
        final_output += f"Date Summarized: {current_date}\n\n\n"

    # Add Topic-Wise Summarization section
    final_output += "## Topic-Wise Summarization\n\n"

    # Now build the output from the pre-generated summaries for Topic-Wise Summarization
    for i, topic_title, summary_sentences in chunk_summaries:
        # Create a link-friendly anchor from the title for linking from table of contents
        anchor = topic_title.lower().replace(' ', '-').replace('/', '').replace('(', '').replace(')', '')
        anchor = re.sub(r'[^a-z0-9-]', '', anchor)  # Remove any other special characters

        # Add topic name as a clear heading with section numbering and anchor
        final_output += f"### 2.{i+1}. {topic_title} <a name=\"{anchor}\"></a>\n\n"

        # Add brief explanation (short paragraph)
        if summary_sentences and len(summary_sentences) > 0:
            main_point = summary_sentences[0].strip()
            final_output += f"{main_point}\n\n"

            # Add key points as bullets
            final_output += "*Key Points:*\n"
            for sentence in summary_sentences[1:4]:  # Limit to 3 supporting details
                if sentence.strip():
                    final_output += f"- {sentence.strip()}\n"

            final_output += "\n"

            # Add placeholder for formulas/equations (if present)
            if "equation" in chunks[i].lower() or "formula" in chunks[i].lower():
                final_output += "*Important Formulas/Equations:*\n"
                final_output += "- [Formula placeholder - extracted from document]\n\n"

        final_output += "\n\n"

    # Add Important Terms and Abbreviations section
    final_output += "## Important Terms and Abbreviations\n\n"

    # Extract important terms using TF-IDF - faster with fewer features
    vectorizer = TfidfVectorizer(stop_words='english', max_features=10)

    # Only proceed if we have enough text
    if len(paragraphs) > 0:
        try:
            # Use only a sample of paragraphs for faster processing
            sample_size = min(len(paragraphs), 20)
            sample_paragraphs = paragraphs[:sample_size]

            # Fit the vectorizer on the sample
            vectorizer.fit_transform(sample_paragraphs)
            feature_names = vectorizer.get_feature_names_out()

            # Try to use Groq for better term explanations
            if use_groq and groq_client:
                try:
                    # Create a prompt for term explanations
                    terms_str = ", ".join([term.capitalize() for term in feature_names[:10]])
                    context_str = " ".join(paragraphs[:5])  # Use first few paragraphs for context

                    prompt = f"""
                    Based on the following context about {doc_title}, provide brief explanations (1-2 sentences each)
                    for these key terms: {terms_str}.

                    Context: {context_str[:2000]}

                    Format each term as:
                    - *Term*: Brief explanation that shows understanding of the concept in this specific context.

                    Important instructions:
                    1. Make each explanation specific and informative, not generic
                    2. Do NOT include any introductory text like "Here is..." or "Below are..."
                    3. Start directly with the first term definition
                    4. Keep explanations concise and technical
                    """

                    completion = groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama3-8b-8192",
                        max_tokens=800,
                        temperature=0.3,
                    )

                    term_explanations = completion.choices[0].message.content.strip()
                    final_output += term_explanations + "\n"
                except Exception as e:
                    print(f"Error getting term explanations: {e}")
                    # Fallback to simple list
                    for term in feature_names[:10]:  # Get top 10 terms
                        final_output += f"- *{term.capitalize()}:* Important concept related to {doc_title}\n"
            else:
                # Fallback to simple list
                for term in feature_names[:10]:  # Get top 10 terms
                    final_output += f"- *{term.capitalize()}:* Important concept related to {doc_title}\n"
        except Exception as e:
            print(f"TF-IDF extraction error: {e}")
            # Fallback if TF-IDF fails
            final_output += "- No key terminology could be extracted automatically\n"

    final_output += "\n\n\n"

    # Add Conclusion / Final Summary section
    final_output += "## Conclusion / Final Summary\n\n"

    # Extract conclusion from the last chunk
    if len(chunks) > 0:
        conclusion_chunk = chunks[-1]  # Use the last chunk for conclusions

        # Try to generate a better conclusion with Groq
        if use_groq and groq_client:
            try:
                # Create a prompt for a concise conclusion
                prompt = f"""
                Write a concise conclusion (3-4 sentences) that summarizes the key points from this document about {doc_title}.
                End with a single-sentence key takeaway that captures the most important insight.

                Text: {conclusion_chunk[:2000]}

                Important instructions:
                1. Start directly with the conclusion - NO phrases like "In conclusion..." or "To summarize..."
                2. Be direct, technical, and informative
                3. Do not use meta-language about the summary itself
                4. Format the key takeaway as "Key Takeaway: [single sentence]" on a new line
                """

                completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    max_tokens=200,
                    temperature=0.3,
                )

                conclusion_text = completion.choices[0].message.content.strip()
                final_output += conclusion_text
            except Exception as e:
                print(f"Error generating conclusion: {e}")
                # Fallback to regular conclusion generation
                # Reuse the summary if we already have it
                conclusion_summary = None
                for i, topic_title, summary_sentences in chunk_summaries:
                    if i == len(chunks) - 1:
                        conclusion_summary = " ".join([s.strip() for s in summary_sentences])
                        break

                # If we don't have it, generate it
                if not conclusion_summary:
                    conclusion_summary = cached_summarize(conclusion_chunk, max_length=150, min_length=30, use_groq=use_groq, groq_client=groq_client)

                conclusion_sentences = re.split(r'(?<=[.!?]) +', conclusion_summary)

                # Very short wrap-up of the main ideas (3-5 sentences)
                for sentence in conclusion_sentences[:3]:  # Limit to 3 sentences for conclusion
                    if sentence.strip():
                        final_output += f"{sentence.strip()}. "

                # Add one-sentence takeaway for revision
                if conclusion_sentences and len(conclusion_sentences) > 0:
                    final_output += f"\n\n*Key Takeaway:* {conclusion_sentences[0].strip()}."
        else:
            # Fallback to regular conclusion generation
            # Reuse the summary if we already have it
            conclusion_summary = None
            for i, topic_title, summary_sentences in chunk_summaries:
                if i == len(chunks) - 1:
                    conclusion_summary = " ".join([s.strip() for s in summary_sentences])
                    break

            # If we don't have it, generate it
            if not conclusion_summary:
                conclusion_summary = cached_summarize(conclusion_chunk, max_length=150, min_length=30, use_groq=use_groq, groq_client=groq_client)

            conclusion_sentences = re.split(r'(?<=[.!?]) +', conclusion_summary)

            # Very short wrap-up of the main ideas (3-5 sentences)
            for sentence in conclusion_sentences[:3]:  # Limit to 3 sentences for conclusion
                if sentence.strip():
                    final_output += f"{sentence.strip()}. "

            # Add one-sentence takeaway for revision
            if conclusion_sentences and len(conclusion_sentences) > 0:
                final_output += f"\n\n*Key Takeaway:* {conclusion_sentences[0].strip()}."

    final_output += "\n\n\n"

    # Add a footer with date and page count
    final_output += "---\n\n"
    final_output += f"Summary generated on {current_date}\n"

    # If we have information about the number of pages
    if hasattr(chunks, '_len_'):
        final_output += f"Document contains approximately {len(chunks)} sections\n\n"

    final_output += "\n✅ End of Summary"

    return final_output

def summarize_pdf(save_to_file=False, generate_pdf=False):
    """Generate a summary of the loaded PDF"""
    if not cached_text:
        return "❌ PDF not uploaded or empty."

    # Split text into paragraphs and filter out short ones
    paragraphs = [p.strip() for p in cached_text.split('\n\n') if len(p.strip()) > 40]

    if not paragraphs:
        return "❌ Could not extract meaningful content from the PDF."

    # Generate the summary
    summary = summarize_text(paragraphs)

    # Generate PDF if requested
    pdf_link = ""
    if generate_pdf:
        try:
            # Generate HTML file that can be printed as PDF
            html_path = generate_pdf_from_summary(summary)
            pdf_link = f"<a href='{html_path}' target='_blank' style='color: #7b7bff; text-decoration: underline;'>View as PDF</a>"
        except Exception as e:
            pdf_link = f"⚠️ Could not generate PDF: {str(e)}"

    # Save to file if requested
    if save_to_file:
        try:
            # Create notes directory if it doesn't exist
            if not os.path.exists("notes"):
                os.makedirs("notes")

            # Generate a filename based on the current date and time
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"notes/summary_{timestamp}.txt"

            # Save the summary to the file
            with open(filename, "w", encoding="utf-8") as file:
                file.write("# DOCUMENT SUMMARY\n\n")
                file.write(summary)

            download_link = f"<a href='{filename}' download style='color: #7b7bff; text-decoration: underline;'>Download Summary as Text File</a>"

            return (
                "📄 Document Summary:\n"
                "===================\n"
                f"{summary}\n\n"
                f"💾 {download_link}\n\n"
                + (f"📊 {pdf_link}\n\n" if pdf_link else "")
                + "💡 Tip: Type 'generate notes' to get detailed study notes from this document."
            )
        except Exception as e:
            # If saving fails, still return the summary but with an error message
            return (
                "📄 Document Summary:\n"
                "===================\n"
                f"{summary}\n\n"
                f"⚠️ Could not save summary to file: {str(e)}\n\n"
                + (f"📊 {pdf_link}\n\n" if pdf_link else "")
                + "💡 Tip: Type 'generate notes' to get detailed study notes from this document."
            )
    else:
        return (
            "📄 Document Summary:\n"
            "===================\n"
            f"{summary}\n\n"
            + (f"📊 {pdf_link}\n\n" if pdf_link else "")
            + "💡 Tip: Type 'generate notes' to get detailed study notes from this document."
        )

# ========== NOTES GENERATION ==========

def generate_notes_from_pdf(input_data):
    if isinstance(input_data, bytes):  # Case: file bytes from uploader
        doc = fitz.open(stream=BytesIO(input_data), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
    elif isinstance(input_data, str):  # Case: cached_text
        text = input_data
    else:
        return "❌ Invalid input format for notes generation."

    # Extract document title if possible
    title = "Document"
    lines = text.split('\n')
    if lines and len(lines[0].strip()) > 0 and len(lines[0].strip()) < 100:
        title = lines[0].strip()

    paragraphs = text.split('\n\n')
    clean_paragraphs = [p.strip().replace('\n', ' ') for p in paragraphs if len(p.strip()) > 40]

    if not clean_paragraphs:
        return "❌ Couldn't extract meaningful content for notes."

    # Try to use Groq API for better notes generation
    groq_client = None
    use_groq = False
    try:
        from groq import Groq
        groq_client = Groq(api_key="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")
        use_groq = True
        print("✅ Using Groq API for enhanced notes generation")
    except Exception as e:
        print(f"❌ Groq API not available for notes: {e}")
        use_groq = False

    # Get current date for the notes
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")

    # If we have Groq API available, use it to generate comprehensive notes
    if use_groq and groq_client:
        try:
            # Create a context from the document
            context = " ".join(clean_paragraphs[:10])  # Use first 10 paragraphs for context

            # Create a prompt for generating the introduction
            intro_prompt = f"""
            Create a concise introduction paragraph (3-5 sentences) for notes on "{title}".
            Explain what the topic is about and why it's important.

            Context from document: {context[:2000]}

            Important instructions:
            1. Be direct and informative - no phrases like "This document..."
            2. Focus on setting the context for students
            3. Explain why this topic matters
            4. Use student-friendly language
            """

            intro_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": intro_prompt}],
                model="llama3-70b-8192",  # Using Llama 3 70B model
                max_tokens=400,  # Doubled token limit for more detailed introduction
                temperature=0.3,
            )

            introduction = intro_completion.choices[0].message.content.strip()

            # Extract ALL topics from the document - more comprehensive approach
            topic_extraction_prompt = f"""
            Based on this document about "{title}", identify ALL main topics and subtopics that should be covered in COMPREHENSIVE study notes. Do not omit any significant topics from the document.

            Context from document: {" ".join(clean_paragraphs[:40])[:4000]}

            For each topic:
            1. Provide a clear, specific topic name
            2. List ALL relevant subtopics that should be covered

            Format your response as:
            1. [Topic Name]
               - [Subtopic 1]
               - [Subtopic 2]
               - [Subtopic 3]

            2. [Topic Name]
               - [Subtopic 1]
               - [Subtopic 2]
               ...

            Important instructions:
            1. Be COMPREHENSIVE - include ALL topics from the document
            2. Do not limit to just 3-5 topics - cover everything important
            3. Be specific and detailed in naming topics and subtopics
            4. Ensure complete coverage of the document's content
            """

            topics_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": topic_extraction_prompt}],
                model="llama3-70b-8192",  # Using Llama 3 70B model
                max_tokens=2000,  # Increased token limit for more comprehensive topic extraction
                temperature=0.3,
            )

            topics_outline = topics_completion.choices[0].message.content.strip()

            # Generate practical student notes with comprehensive coverage
            detailed_notes_prompt = f"""
            Create PRACTICAL STUDENT NOTES on "{title}" following this EXACT format. These notes should COMPREHENSIVELY cover ALL important content from the document:

            # Practical Student Notes: {title}

            Introduction:
            {introduction}

            For each major topic in the document, create a separate section with this structure:

            ## [Topic Name]

            ### Quick Overview (1-2 lines)
            Write a super short explanation about the topic in 1-2 simple sentences.
            Natural style, like how you would quickly explain to a friend.

            Example: "Neural networks are models designed to mimic how the human brain processes information through layers of interconnected nodes."

            ### Core Concepts / Key Points
            - List important ideas or steps in bullet points
            - Keep each point short and clear (max 1-2 lines)
            - Add small examples inside points if needed
            - Cover ALL important concepts from this section of the document
            - Make sure to include every significant point

            ### Important Formulas (if applicable)

            [Formula goes here]

            Where:
            - [Variable 1] = [Meaning]
            - [Variable 2] = [Meaning]
            - [Variable 3] = [Meaning]

            ### Diagrams or Visuals (if needed)
            [Describe any important diagrams or visuals that would help understand the concept]

            ### Tips, Tricks, and Common Mistakes
            - 3-5 bullet points focusing on what students easily forget or common mistakes
            - Include practical advice for understanding this topic
            - Highlight tricky aspects that need special attention

            ### Mini Summary
            3-4 lines summarizing the whole topic. Try to "connect the dots" between concepts.

            IMPORTANT: Create a section for EVERY significant topic in the document. Do not skip any important content.

            Topics to cover (create a section for each, but also add ANY other important topics you identify):
            {topics_outline}

            After covering all topics, add these final sections:

            ## Important Definitions

            SPECIAL INSTRUCTIONS FOR DEFINITIONS:
            1. Format each definition as a bullet point: "- *Term*: Short, clear definition."
            2. Arrange all terms alphabetically in a single list
            3. No big paragraphs — just quick, clear lines
            4. Include ALL important technical terms from the document
            5. Be comprehensive - don't miss any significant terms
            6. Make sure each term stands on its own line with proper bullet formatting

            ## Abbreviations

            SPECIAL INSTRUCTIONS FOR ABBREVIATIONS:
            1. Format each abbreviation as a bullet point: "- *Abbreviation*: Full Form"
            2. Only include abbreviations that actually appear in the document
            3. List ALL abbreviations found in the document
            4. Arrange alphabetically for easy reference
            5. If no abbreviations exist, state "No important abbreviations in this topic."

            OVERALL STYLE GUIDELINES:
            1. Write in a casual, student-friendly tone
            2. Use simple language - imagine explaining to a friend
            3. Be concise but COMPREHENSIVE - cover ALL important content
            4. Include practical examples where possible
            5. Focus on what students need to know for understanding and exams
            6. Make the notes visually scannable with clear sections
            7. Use bullet points liberally
            8. Avoid overly technical language unless necessary

            CRITICAL: These notes should cover EVERY important concept, formula, and definition from the document. Do not skip any significant content.

            Context from document: {" ".join(clean_paragraphs[:50])[:5000]}

            ABSOLUTELY CRITICAL INSTRUCTIONS:
            1. FOLLOW THE EXACT FORMAT specified above - this is a specific note-taking style
            2. Use a CASUAL, STUDENT-FRIENDLY tone throughout - write like you're explaining to a friend
            3. Be COMPREHENSIVE - cover EVERY important concept from the document
            4. For each topic, include ALL the specified sections in order
            5. Make the "Quick Overview" line truly simple and casual
            6. Use BULLET POINTS for all lists - don't write paragraphs
            7. Include PRACTICAL EXAMPLES wherever possible
            8. For formulas, explain variables clearly and simply
            9. Make the "Tips, Tricks, and Common Mistakes" section genuinely helpful for exam preparation
            10. Keep definitions SHORT and SIMPLE - no complex technical language
            11. Format abbreviations exactly as specified: "*Abbreviation*: Full Form"
            12. Focus on making these notes both COMPREHENSIVE and PRACTICAL
            13. Use simple language throughout - avoid jargon unless necessary
            14. Make sure each topic section follows the same consistent structure
            15. Do not skip ANY important content from the document - cover everything
            """

            notes_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": detailed_notes_prompt}],
                model="llama3-70b-8192",  # Using Llama 3 70B model
                max_tokens=8000,  # Reasonable token limit for quality notes
                temperature=0.3,
            )

            notes_content = notes_completion.choices[0].message.content.strip()

            # Format the final notes with proper markdown
            notes_output = f"# 📝 Study Notes: {title}\n\n"
            notes_output += f"Generated on: {current_date}\n\n"
            notes_output += notes_content

            # Generate PDF version
            pdf_link = ""
            try:
                # Generate HTML file that can be printed as PDF
                html_path = generate_pdf_from_summary(notes_output)
                pdf_link = f"<a href='{html_path}' target='_blank' style='color: #7b7bff; text-decoration: underline;'>View as PDF</a>"
            except Exception as e:
                pdf_link = f"⚠️ Could not generate PDF: {str(e)}"

            # Save the notes to a file
            try:
                # Create notes directory if it doesn't exist
                if not os.path.exists("notes"):
                    os.makedirs("notes")

                # Generate a filename based on the current date and time
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"notes/study_notes_{timestamp}.txt"

                # Save the notes to the file
                with open(filename, "w", encoding="utf-8") as file:
                    file.write("# DETAILED STUDY NOTES\n\n")
                    file.write(notes_output)

                download_link = f"<a href='{filename}' download style='color: #7b7bff; text-decoration: underline;'>Download Notes as Text File</a>"

                return (
                    "📚 Detailed Study Notes:\n"
                    "=====================\n"
                    f"{notes_output}\n\n"
                    f"💾 {download_link}\n\n"
                    + (f"📊 {pdf_link}\n\n" if pdf_link else "")
                    + "💡 Tip: Type 'summarize pdf' to get a quick overview of the document."
                )
            except Exception as e:
                # If saving fails, still return the notes but with an error message
                return (
                    "📚 Detailed Study Notes:\n"
                    "=====================\n"
                    f"{notes_output}\n\n"
                    f"⚠️ Could not save notes to file: {str(e)}\n\n"
                    + (f"📊 {pdf_link}\n\n" if pdf_link else "")
                    + "💡 Tip: Type 'summarize pdf' to get a quick overview of the document."
                )

        except Exception as e:
            print(f"Error generating comprehensive notes with Groq: {e}")
            # Fall back to simpler notes generation if Groq fails
            return generate_simple_notes(title, clean_paragraphs, current_date)
    else:
        # If Groq is not available, use simpler notes generation
        return generate_simple_notes(title, clean_paragraphs, current_date)

def generate_simple_notes(title, clean_paragraphs, current_date):
    """Generate practical student notes when Groq API is not available"""
    # Extract key concepts using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(clean_paragraphs)
    scores = np.asarray(X.sum(axis=1)).ravel()

    # Get paragraphs for topic coverage
    top_indices = scores.argsort()[-15:][::-1]

    # Start building the practical student notes
    notes_output = f"# Practical Student Notes: {title}\n\n"
    notes_output += f"Generated on: {current_date}\n\n"

    # Introduction
    if len(clean_paragraphs) > 0:
        intro_para = clean_paragraphs[0][:200]  # Just use the first bit of text
        notes_output += f"{intro_para}...\n\n"

    # Group paragraphs into topics
    topic_groups = {}

    for i, idx in enumerate(top_indices):
        paragraph = clean_paragraphs[idx]

        # Simple topic grouping - every 3 paragraphs form a topic
        topic_num = i // 3
        if topic_num not in topic_groups:
            topic_groups[topic_num] = []

        topic_groups[topic_num].append(paragraph)

    # Process each topic group in the new format
    for topic_num, paragraphs in topic_groups.items():
        # Create a meaningful topic title
        first_para = paragraphs[0]
        words = first_para.split()[:5]  # First 5 words for a shorter title
        topic_title = " ".join(words) + "..."

        notes_output += f"## {topic_title}\n\n"

        # Quick Overview
        notes_output += "### Quick Overview\n\n"
        notes_output += f"{topic_title.replace('...', '')} is {first_para[:100]}...\n\n"

        # Core Concepts / Key Points
        notes_output += "### Core Concepts / Key Points\n\n"

        # Extract key sentences from the paragraphs
        topic_text = " ".join(paragraphs)
        sentences = re.split(r'(?<=[.!?]) +', topic_text)
        key_sentences = sentences[:min(10, len(sentences))]

        for sentence in key_sentences:
            # Keep only shorter sentences for bullet points
            if 20 < len(sentence) < 150:
                notes_output += f"- {sentence}\n"

        notes_output += "\n"

        # Important Formulas (if applicable)
        # Look for potential formulas in the text (simple heuristic)
        has_formula = any(["=" in para or "+" in para or "-" in para or "*" in para or "/" in para for para in paragraphs])
        if has_formula:
            notes_output += "### Important Formulas\n\n"
            notes_output += "\n"
            # Just a placeholder since we can't reliably extract formulas
            notes_output += "Formula would appear here if detected\n"
            notes_output += "\n\n"
            notes_output += "Where:\n"
            notes_output += "- Variable 1 = Meaning would be explained here\n"
            notes_output += "- Variable 2 = Meaning would be explained here\n"
            notes_output += "- Variable 3 = Meaning would be explained here\n\n"

        # Diagrams or Visuals (if needed)
        notes_output += "### Diagrams or Visuals\n\n"
        notes_output += "[A simple diagram showing the key components and relationships in this topic would help visualize the concepts.]\n\n"

        # Tips, Tricks, and Common Mistakes
        notes_output += "### Tips, Tricks, and Common Mistakes\n\n"

        # Create some generic but useful tips
        notes_output += "- Remember to understand the core concepts before moving to advanced topics\n"
        notes_output += "- Pay attention to the relationships between different elements\n"
        notes_output += "- Practice applying these concepts to real-world examples\n"
        notes_output += "- Common mistake: Overlooking the importance of fundamentals\n"
        notes_output += "- This topic connects with other areas of the subject\n\n"

        # Mini Summary
        notes_output += "### Mini Summary\n\n"
        if len(key_sentences) > 0:
            summary = key_sentences[0]
            if len(key_sentences) > 1:
                summary += " " + key_sentences[1]
            notes_output += f"{summary} This is important for understanding the overall subject and applying the concepts in practical situations. The concepts here connect with other topics and provide a foundation for more advanced learning.\n\n"

    # Important Definitions section with alphabetical index
    notes_output += "## Important Definitions\n\n"

    # Extract important terms using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english', max_features=20)

    # Only proceed if we have enough text
    if len(clean_paragraphs) > 0:
        try:
            # Use a sample of paragraphs for processing
            sample_size = min(len(clean_paragraphs), 30)
            sample_paragraphs = clean_paragraphs[:sample_size]

            # Fit the vectorizer on the sample
            vectorizer.fit_transform(sample_paragraphs)
            feature_names = vectorizer.get_feature_names_out()

            # Sort terms alphabetically
            feature_names = sorted(feature_names)

            # Create a list of terms and definitions
            terms_and_definitions = []

            for term in feature_names:
                if len(term) < 3 or not term.isalpha():
                    continue  # Skip very short terms or non-alphabetic terms

                # Find the best context for this term
                best_context = ""
                for para in clean_paragraphs:
                    if term.lower() in para.lower():
                        # If we find a paragraph with the term, use it as context
                        best_context = para
                        # If the paragraph contains "is defined as" or similar, prioritize it
                        if any(phrase in para.lower() for phrase in [f"{term} is", "defined as", "refers to", "means"]):
                            break

                if best_context:
                    # Extract a definition-like sentence
                    sentences = re.split(r'(?<=[.!?]) +', best_context)
                    definition = ""

                    # Look for sentences that define the term
                    for sentence in sentences:
                        if term.lower() in sentence.lower() and any(phrase in sentence.lower() for phrase in ["is", "are", "refers", "means", "defined"]):
                            definition = sentence
                            break

                    # If no definition-like sentence found, use the first sentence with the term
                    if not definition:
                        for sentence in sentences:
                            if term.lower() in sentence.lower():
                                definition = sentence
                                break

                    # Simplify the definition for student-friendly format
                    if definition:
                        # Shorten the definition if it's too long
                        if len(definition) > 100:
                            definition = definition[:100] + "..."
                        # Add the term and definition to our list
                        terms_and_definitions.append((term.capitalize(), definition))
                    else:
                        # Create a simple placeholder
                        terms_and_definitions.append((term.capitalize(), f"Important concept in {title} related to {topic_title.replace('...', '')}."))

            # Sort terms alphabetically
            terms_and_definitions.sort(key=lambda x: x[0])

            # Add the definitions as bullet points
            if terms_and_definitions:
                for term, definition in terms_and_definitions:
                    notes_output += f"- *{term}*: {definition}\n\n"
            else:
                notes_output += "No key terminology could be extracted automatically.\n\n"

        except Exception as e:
            print(f"Error extracting definitions: {e}")
            notes_output += "No key terminology could be extracted automatically.\n\n"

    # Abbreviations section
    notes_output += "## Abbreviations\n\n"

    # Try to identify actual abbreviations (uppercase words)
    potential_abbrs = set()
    abbr_contexts = {}

    for para in clean_paragraphs:
        words = para.split()
        for i, word in enumerate(words):
            # Look for uppercase words that might be abbreviations
            if word.isupper() and 2 <= len(word) <= 5 and word.isalpha():
                potential_abbrs.add(word)

                # Store the context (surrounding words) for this abbreviation
                start_idx = max(0, i - 10)
                end_idx = min(len(words), i + 10)
                context = " ".join(words[start_idx:end_idx])

                if word in abbr_contexts:
                    abbr_contexts[word].append(context)
                else:
                    abbr_contexts[word] = [context]

    if potential_abbrs:
        # Sort abbreviations alphabetically
        sorted_abbrs = sorted(list(potential_abbrs))

        for abbr in sorted_abbrs:
            # Try to find the full form in the context
            full_form = ""
            contexts = abbr_contexts.get(abbr, [])

            for context in contexts:
                # Look for patterns like "XXX (Something Something Something)" or "Something Something Something (XXX)"
                match = re.search(rf'{abbr} \(([^)]+)\)', context)
                if match:
                    full_form = match.group(1)
                    break

                match = re.search(rf'\(([^)]+)\) {abbr}', context)
                if match:
                    full_form = match.group(1)
                    break

                # Look for patterns like "XXX - Something Something Something"
                match = re.search(rf'{abbr} - ([^.!?]+)', context)
                if match:
                    full_form = match.group(1)
                    break

            # Format according to the new style with bullet points
            if full_form:
                notes_output += f"- *{abbr}*: {full_form}\n\n"
            else:
                notes_output += f"- *{abbr}*: Abbreviation used in this topic\n\n"
    else:
        notes_output += "No important abbreviations in this topic.\n\n"

    # Generate PDF version
    pdf_link = ""
    try:
        # Generate HTML file that can be printed as PDF
        html_path = generate_pdf_from_summary(notes_output)
        pdf_link = f"<a href='{html_path}' target='_blank' style='color: #7b7bff; text-decoration: underline;'>View as PDF</a>"
    except Exception as e:
        pdf_link = f"⚠️ Could not generate PDF: {str(e)}"

    # Save the notes to a file
    try:
        # Create notes directory if it doesn't exist
        if not os.path.exists("notes"):
            os.makedirs("notes")

        # Generate a filename based on the current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"notes/study_notes_{timestamp}.txt"

        # Save the notes to the file
        with open(filename, "w", encoding="utf-8") as file:
            file.write("# DETAILED STUDY NOTES\n\n")
            file.write(notes_output)

        download_link = f"<a href='{filename}' download style='color: #7b7bff; text-decoration: underline;'>Download Notes as Text File</a>"

        return (
            "📚 Detailed Study Notes:\n"
            "=====================\n"
            f"{notes_output}\n\n"
            f"💾 {download_link}\n\n"
            + (f"📊 {pdf_link}\n\n" if pdf_link else "")
            + "💡 Tip: Type 'summarize pdf' to get a quick overview of the document."
        )
    except Exception as e:
        # If saving fails, still return the notes but with an error message
        return (
            "📚 Detailed Study Notes:\n"
            "=====================\n"
            f"{notes_output}\n\n"
            f"⚠️ Could not save notes to file: {str(e)}\n\n"
            + (f"📊 {pdf_link}\n\n" if pdf_link else "")
            + "💡 Tip: Type 'summarize pdf' to get a quick overview of the document."
        )

# ========== PAGE-WISE VIEW ==========

def get_pdf_page_text(page_num):
    if not cached_pages:
        return "❌ No PDF loaded."
    return cached_pages.get(page_num, f"❌ Page {page_num} not found.")