"use client";

import React, { useState, useRef, useEffect } from "react";
import { chatApi, uploadApi } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// ... (Rest of file)

// ... Inside rendering loop ...



type Message = {
  id: string;
  role: "user" | "ai";
  content: string | React.ReactNode;
  timestamp: Date;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init-1",
      role: "ai",
      content: "Hello. I'm UniMentor, your personal assistant for university career success. I'm ready to help you optimize your resume for your next big opportunity.\n\nHow can we improve your professional profile today?",
      timestamp: new Date(),
    }
  ]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text?: string) => {
    const messageContent = text || inputValue;

    // Validate: Needs either text OR file
    if ((!messageContent.trim() && !selectedFile) || isLoading) return;

    // 1. Construct User Message
    const userDisplayContent = (
      <div className="flex flex-col gap-2">
        {selectedFile && (
          <div className="flex items-center gap-2 text-sm text-white/60 bg-white/5 p-2 rounded-lg w-fit">
            <span className="material-symbols-outlined text-[18px]">description</span>
            <span>{selectedFile.name}</span>
          </div>
        )}
        {messageContent && <span>{messageContent}</span>}
      </div>
    );

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: userDisplayContent, // We store ReactNode for display
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);

    // Clear inputs immediately
    if (!text) setInputValue("");
    const fileToSend = selectedFile; // Capture ref
    setSelectedFile(null); // Clear state
    if (fileInputRef.current) fileInputRef.current.value = "";

    setIsLoading(true);

    try {
      let uploadResponse = null;

      // 2. Upload File First (if exists)
      if (fileToSend) {
        uploadResponse = await uploadApi(fileToSend);
        // We ignore the generic upload response message for the chat flow,
        // unless there is NO text message, in which case we show it.
      }

      // 3. Send Text Message (if exists)
      if (messageContent.trim()) {
        const data = await chatApi(messageContent);
        const botMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "ai",
          content: data.reply,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMsg]);
      } else if (uploadResponse) {
        // File only - show upload response
        const botMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "ai",
          content: uploadResponse.reply,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMsg]);
      }

    } catch (error) {
      console.error("Interaction error:", error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: "Sorry, I encountered an error providing your request.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleQuickAction = (action: string) => {
    if (action === "analyze") {
      triggerFileUpload();
    } else if (action === "start_fresh") {
      setInputValue("I want to start a fresh resume");
      const textarea = document.querySelector('textarea');
      if (textarea) textarea.focus();
    }
  };

  return (
    <div className="bg-deep-charcoal text-white overflow-hidden h-screen flex flex-col font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-10 py-8 bg-transparent z-20">
        <div className="flex items-center gap-4">
          <h1 className="unimentor-title text-2xl font-semibold">UniMentor</h1>
          <div className="h-4 w-px bg-white/10 mx-1"></div>
          <span className="text-[11px] uppercase tracking-[0.2em] text-white/40 font-medium">Assistant</span>
        </div>
        <div className="flex items-center gap-4">
          {/* Profile removed as requested */}
        </div>
      </header>

      <main className="flex-1 flex flex-col overflow-hidden relative">
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="chat-container px-8 py-12 flex flex-col gap-12">

            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-6 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`size-9 rounded-xl flex items-center justify-center shrink-0 border ${msg.role === 'user' ? 'rounded-full bg-white/10 border-white/20' : 'bg-white/5 border-white/10'}`}>
                  <span className="material-symbols-outlined text-white/60 text-xl">
                    {msg.role === 'user' ? 'person' : 'auto_awesome'}
                  </span>
                </div>
                <div className={`flex flex-col gap-2 max-w-[80%] ${msg.role === 'user' ? 'items-end' : ''}`}>
                  <div className={`${msg.role === 'user' ? 'chat-bubble-user rounded-tr-none text-white/95' : 'chat-bubble-ai rounded-tl-none text-white/90'} p-6 rounded-2xl`}>
                    {msg.role === 'ai' && typeof msg.content === 'string' ? (
                      <div className="markdown-content text-[15px] leading-relaxed font-light">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            a: ({ node, ...props }) => <a {...props} className="text-primary-blue hover:underline" target="_blank" rel="noopener noreferrer" />
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="text-[15px] leading-relaxed font-light whitespace-pre-wrap">
                        {msg.content}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-6">
                <div className="size-9 rounded-xl bg-white/5 flex items-center justify-center shrink-0 border border-white/10">
                  <span className="material-symbols-outlined text-white/60 text-xl">auto_awesome</span>
                </div>
                <div className="flex flex-col gap-2 max-w-[80%]">
                  <div className="chat-bubble-ai p-6 rounded-2xl rounded-tl-none">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce [animation-delay:-.3s]"></div>
                      <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce [animation-delay:-.5s]"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />



          </div>
        </div>

        {/* Input Area */}
        <div className="w-full bg-transparent pb-12 pt-6">
          <div className="chat-container px-8">
            <div className="relative group">

              {/* File Preview */}
              {selectedFile && (
                <div className="absolute -top-12 left-0 bg-white/10 backdrop-blur-md border border-white/10 text-white px-4 py-2 rounded-xl flex items-center gap-3 shadow-lg z-10 animate-in fade-in slide-in-from-bottom-2">
                  <span className="material-symbols-outlined text-white/60 text-sm">description</span>
                  <span className="text-sm font-medium pr-2 max-w-[200px] truncate">{selectedFile.name}</span>
                  <button onClick={handleRemoveFile} className="hover:bg-white/20 rounded-full p-1 transition-colors">
                    <span className="material-symbols-outlined text-sm">close</span>
                  </button>
                </div>
              )}

              <textarea
                className="w-full bg-white/[0.04] border border-white/10 rounded-[28px] py-6 pl-8 pr-32 text-[15px] focus:ring-1 focus:ring-white/20 focus:border-white/30 focus:bg-white/[0.06] resize-none text-white placeholder-white/25 transition-all outline-none min-h-[70px] custom-scrollbar"
                placeholder="Ask UniMentor anything about your resume..."
                rows={1}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
              ></textarea>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-3">
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept=".pdf"
                  onChange={handleFileSelect}
                />
                <button
                  onClick={triggerFileUpload}
                  className={`size-11 rounded-full flex items-center justify-center transition-all ${selectedFile ? 'text-white bg-white/10' : 'text-white/40 hover:text-white hover:bg-white/10'}`}
                  title="Upload File"
                >
                  <span className="material-symbols-outlined">attach_file</span>
                </button>
                <button
                  onClick={() => handleSend()}
                  disabled={isLoading || (!inputValue.trim() && !selectedFile)}
                  className="size-11 bg-white text-black rounded-full flex items-center justify-center hover:scale-105 transition-all shadow-2xl shadow-white/5 active:scale-95 disabled:opacity-50 disabled:active:scale-100"
                >
                  <span className="material-symbols-outlined font-semibold text-xl">north</span>
                </button>
              </div>
            </div>
            <div className="flex items-center justify-center gap-4 mt-8 opacity-40">
              <p className="text-[10px] tracking-widest uppercase font-medium">Focused Session • Minimal Mode</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
