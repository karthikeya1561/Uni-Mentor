// Formal, Glassmorphic EduBot Chatbot JS

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('center-form');
  const input = document.querySelector('.center-input');
  const uploadBtn = document.querySelector('.input-icon-btn[title="upload file"]');
  let chatMessages = document.getElementById('chat-messages');

  // If chat-messages doesn't exist, create and insert it above the input form
  if (!chatMessages) {
    // Create the chat container first
    const chatContainer = document.createElement('div');
    chatContainer.className = 'chat-container';

    // Create the chat messages div inside the container
    chatMessages = document.createElement('div');
    chatMessages.id = 'chat-messages';
    chatMessages.className = 'chat-messages';

    // Add the chat container to the main element
    const main = document.querySelector('.center-main');
    main.appendChild(chatContainer);

    // Add the chat messages to the container
    chatContainer.appendChild(chatMessages);
  }

  // Add CSS for chat messages if not already in the CSS file
  if (!document.querySelector('style#chat-styles')) {
    const style = document.createElement('style');
    style.id = 'chat-styles';
    style.textContent = `
      .chat-container {
        width: 100%;
        max-width: 700px;
        height: calc(100% - 200px);
        overflow-y: auto;
        overflow-x: hidden;
        padding: 20px 30px 20px 10px; /* Increased right padding to move scrollbar away from content */
        margin-top: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        scrollbar-width: thin;
        scrollbar-color: #23283a #101114;
      }

      .chat-container::-webkit-scrollbar {
        width: 8px;
      }

      .chat-container::-webkit-scrollbar-track {
        background: #101114;
      }

      .chat-container::-webkit-scrollbar-thumb {
        background-color: #23283a;
        border-radius: 10px;
        border: 2px solid #101114;
      }

      .chat-messages {
        display: flex;
        flex-direction: column;
        gap: 12px;
        width: 100%;
        max-width: 700px;
        margin: 0 auto;
        padding: 10px 25px 10px 10px; /* Increased right padding to move content away from scrollbar */
      }

      /* Style for chat messages when greeting is hidden */
      .greeting-hidden .chat-container {
        height: calc(100% - 40px);
        margin-top: 20px;
      }
      .chat-bubble {
        padding: 12px 16px;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
        line-height: 1.5;
        white-space: pre-line; /* Preserves line breaks */
        margin-bottom: 12px; /* Add more space between chat bubbles */
        box-shadow: 0 2px 8px rgba(0,0,0,0.15); /* Add subtle shadow */
        transition: all 0.3s ease; /* Add transition for animations */
        animation: fadeIn 0.3s ease-out; /* Add fade-in animation */
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .chat-bubble p {
        margin: 0 0 10px 0;
      }
      .chat-bubble p:last-child {
        margin-bottom: 0;
      }
      .chat-bubble ul, .chat-bubble ol {
        margin-top: 5px;
        margin-bottom: 5px;
        padding-left: 20px;
      }
      .chat-bubble li {
        margin-bottom: 5px;
      }
      .bubble-user {
        align-self: flex-end;
        background: linear-gradient(135deg, #7b7bff, #6e6eff);
        color: white;
        border-bottom-right-radius: 4px;
        transform-origin: bottom right;
        animation: fadeInRight 0.3s ease-out;
        box-shadow: 0 2px 10px rgba(123, 123, 255, 0.3);
      }

      @keyframes fadeInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
      }

      .bubble-bot {
        align-self: flex-start;
        background: linear-gradient(135deg, #23283a, #2c3248);
        color: #f3f6fa;
        border-bottom-left-radius: 4px;
        transform-origin: bottom left;
        animation: fadeInLeft 0.3s ease-out;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        margin-right: 15px; /* Add right margin to keep bot messages away from scrollbar */
      }

      @keyframes fadeInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
      }

      /* Add hover effect to chat bubbles */
      .chat-bubble:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      }
      .shimmer {
        background: linear-gradient(90deg, #23283a, #3a3f52, #23283a);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        display: inline-block;
      }
      @keyframes shimmer {
        0% { background-position: 100% 0; }
        100% { background-position: -100% 0; }
      }
      .file-input {
        display: none;
      }
      .progress-container {
        width: 90%; /* Reduced width to create space */
        background-color: #181c24; /* Matches the input box background color */
        border-radius: 10px;
        margin-top: 30px; /* Increased space between text and progress bar */
        margin-left: 5%; /* Add left margin to center it */
        padding-right: 5%; /* Add right padding */
        overflow: hidden;
        height: 12px; /* Slightly thicker progress bar */
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        animation: fadeIn 0.5s ease-out;
      }
      .progress-bar {
        width: 0%;
        height: 100%;
        background-color: #7b7bff; /* Matches the primary accent color in your UI */
        background: linear-gradient(90deg, #6e6eff, #9f9fff);
        background-size: 200% 100%;
        border-radius: 10px;
        transition: width 0.2s ease-out;
        box-shadow: 0 0 12px rgba(123, 123, 255, 0.6); /* Enhanced glow effect */
        animation: gradientShift 2s linear infinite;
      }

      @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
    `;
    document.head.appendChild(style);
  }

  // Create a hidden file input for uploads
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = '.pdf';
  fileInput.className = 'file-input';
  fileInput.id = 'file-input';
  document.body.appendChild(fileInput);

  // Function to hide the greeting and subtitle
  function hideGreeting() {
    const greeting = document.querySelector('.main-greeting');
    const subtitles = document.querySelectorAll('.main-subtitle');
    const featureGap = document.querySelector('.feature-gap');
    const main = document.querySelector('.center-main');

    if (greeting) {
      greeting.style.display = 'none';
    }

    subtitles.forEach(subtitle => {
      subtitle.style.display = 'none';
    });

    if (featureGap) {
      featureGap.style.display = 'none';
    }

    // Add a class to the main container to adjust styling
    if (main && !main.classList.contains('greeting-hidden')) {
      main.classList.add('greeting-hidden');
    }
  }

  function appendBubble(text, sender = 'user', isInitialGreeting = false) {
    // Only hide the greeting when it's a user message or not the initial greeting
    if (sender === 'user' || !isInitialGreeting) {
      hideGreeting();
    }

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble ' + (sender === 'user' ? 'bubble-user' : 'bubble-bot');

    // Format text with proper paragraphs and lists
    if (sender === 'bot') {
      // Convert markdown-style lists to HTML lists
      text = text.replace(/\n- /g, '\n• '); // Convert "- " to bullet points

      // Convert double line breaks to paragraph breaks
      const paragraphs = text.split('\n\n');
      if (paragraphs.length > 1) {
        const formattedText = paragraphs
          .filter(p => p.trim() !== '')
          .map(p => `<p>${p.trim()}</p>`)
          .join('');
        bubble.innerHTML = formattedText;
      } else {
        bubble.innerHTML = text;
      }
    } else {
      bubble.innerHTML = text;
    }

    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Handle file upload button click
  uploadBtn.addEventListener('click', function() {
    fileInput.click();
  });

  // Handle file selection
  fileInput.addEventListener('change', async function() {
    if (fileInput.files.length === 0) return;

    const file = fileInput.files[0];
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      appendBubble('Please upload a PDF file.', 'bot');
      return;
    }

    // Show upload message
    appendBubble(`Uploading ${file.name}...`, 'user');

    // Show bot is thinking with progress bar
    const thinkingBubble = document.createElement('div');
    thinkingBubble.className = 'chat-bubble bubble-bot';
    thinkingBubble.innerHTML = `
      <div><strong>Processing PDF file...</strong></div>
      <div style="font-size: 0.9rem; margin-top: 5px; color: #b0b3bb;">Please wait while I extract the content</div>
      <div style="padding-left: 20px; padding-right: 20px;">
        <div class="progress-container">
          <div class="progress-bar"></div>
        </div>
      </div>
    `;
    chatMessages.appendChild(thinkingBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Animate progress bar
    const progressBar = thinkingBubble.querySelector('.progress-bar');
    let width = 0;
    const progressInterval = setInterval(() => {
      if (width >= 100) {
        clearInterval(progressInterval);
      } else {
        width += 1;
        progressBar.style.width = width + '%';
      }
    }, 50);

    // Create form data and send file
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      clearInterval(progressInterval); // Clear the progress interval
      thinkingBubble.remove();
      appendBubble(data.reply, 'bot');
    } catch (err) {
      clearInterval(progressInterval); // Clear the progress interval
      thinkingBubble.remove();
      appendBubble('Sorry, there was an error uploading the file.', 'bot');
    }

    // Reset file input
    fileInput.value = '';
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const userMessage = input.value.trim();
    if (!userMessage) return;
    appendBubble(userMessage, 'user');
    input.value = '';

    // Check if it's a summarize pdf command
    const isSummarizeCommand = userMessage.toLowerCase().includes('summarize pdf');

    // Show bot is thinking
    const thinkingBubble = document.createElement('div');
    thinkingBubble.className = 'chat-bubble bubble-bot';

    let progressInterval;

    if (isSummarizeCommand) {
      thinkingBubble.innerHTML = `
        <div><strong>Generating PDF summary...</strong></div>
        <div style="font-size: 0.9rem; margin-top: 5px; color: #b0b3bb;">Please wait while I analyze the document</div>
        <div style="padding-left: 20px; padding-right: 20px;">
          <div class="progress-container">
            <div class="progress-bar"></div>
          </div>
        </div>
      `;
    } else if (userMessage.toLowerCase().includes('generate notes')) {
      thinkingBubble.innerHTML = `
        <div><strong>Creating detailed notes...</strong></div>
        <div style="font-size: 0.9rem; margin-top: 5px; color: #b0b3bb;">Please wait while I extract key information</div>
        <div style="padding-left: 20px; padding-right: 20px;">
          <div class="progress-container">
            <div class="progress-bar"></div>
          </div>
        </div>
      `;
    } else {
      thinkingBubble.innerHTML = '<span class="shimmer">Uni Mentor is thinking...</span>';
    }

    chatMessages.appendChild(thinkingBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add progress bar animation for summarize command or generate notes
    if (isSummarizeCommand || userMessage.toLowerCase().includes('generate notes')) {
      const progressBar = thinkingBubble.querySelector('.progress-bar');
      let width = 0;

      // Make the progress bar fill faster (5 seconds to reach ~90%)
      // This gives a better user experience since we've optimized the backend
      progressInterval = setInterval(() => {
        if (width >= 90) {
          // Slow down at 90% to wait for actual completion
          width += 0.1;
        } else {
          width += 1.5; // Faster initial progress
        }

        if (width >= 100) {
          clearInterval(progressInterval);
        }

        progressBar.style.width = width + '%';
      }, 50);
    }

    // Send to backend
    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });
      const data = await response.json();
      if (progressInterval) clearInterval(progressInterval);
      thinkingBubble.remove();
      appendBubble(data.reply, 'bot');
    } catch (err) {
      if (progressInterval) clearInterval(progressInterval);
      thinkingBubble.remove();
      appendBubble('Sorry, there was an error connecting to the server.', 'bot');
    }
  });

  // Add an initial greeting
  setTimeout(() => {
    appendBubble('<p>👋 Hello! I\'m Uni Mentor, your academic assistant. How can I help you today?</p>', 'bot', true);
  }, 500);
});