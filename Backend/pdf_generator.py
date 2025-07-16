import os
import markdown
from datetime import datetime

def markdown_to_html_file(markdown_text, output_path=None):
    """
    Convert markdown text to an HTML file

    Args:
        markdown_text (str): The markdown text to convert
        output_path (str, optional): The path to save the HTML file. If None, a default path is used.

    Returns:
        str: The path to the generated HTML file
    """
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])

    # Add CSS styling for better formatting
    css_content = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 2cm;
        font-size: 12pt;
        background-color: #fff;
        color: #333;
    }
    h1 {
        color: #2c3e50;
        font-size: 24pt;
        margin-bottom: 20px;
        text-align: center;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
    h2 {
        color: #3498db;
        font-size: 18pt;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    h3 {
        color: #2980b9;
        font-size: 14pt;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    p {
        margin-bottom: 15px;
    }
    ul, ol {
        margin-bottom: 15px;
        padding-left: 20px;
    }
    li {
        margin-bottom: 5px;
    }
    strong {
        color: #2c3e50;
    }
    hr {
        border: none;
        border-top: 1px solid #eee;
        margin: 20px 0;
    }
    code {
        background-color: #f8f8f8;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: monospace;
    }
    pre {
        background-color: #f8f8f8;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
        font-family: monospace;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 15px;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
    }
    @media print {
        body {
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3 {
            page-break-after: avoid;
        }
        ul, ol, p {
            page-break-inside: avoid;
        }
    }
    """

    # Create a complete HTML document
    complete_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>PDF Summary</title>
        <style>
            {css_content}
        </style>
    </head>
    <body>
        {html_content}
        <!-- No auto-print script, just a nicely formatted document -->
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>To save as PDF: Use your browser's Print function (Ctrl+P or Cmd+P) and select "Save as PDF"</p>
        </div>
    </body>
    </html>
    """

    # Create output directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')

    # Generate a unique filename if none provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"static/summary_{timestamp}.html"

    # Write HTML to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(complete_html)

    return output_path

def generate_pdf_from_summary(summary_text):
    """
    Generate an HTML file from the summary text that can be printed as PDF

    Args:
        summary_text (str): The summary text in markdown format

    Returns:
        str: The path to the generated HTML file
    """
    return markdown_to_html_file(summary_text)
