
'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/lib/store';
import { useMutation } from '@tanstack/react-query';
import { chatApi } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, Bot, User, GraduationCap, Menu } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import Sidebar from './Sidebar';
import { Textarea } from '@/components/ui/textarea';

export default function ChatInterface() {
    const { messages, addMessage, isLoading, setLoading } = useChatStore();
    const [input, setInput] = useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    const chatMutation = useMutation({
        mutationFn: chatApi,
        onMutate: () => {
            setLoading(true);
        },
        onSuccess: (data) => {
            addMessage({
                id: Date.now().toString(),
                role: 'bot',
                content: data.reply,
                timestamp: Date.now(),
            });
            setLoading(false);
        },
        onError: () => {
            addMessage({
                id: Date.now().toString(),
                role: 'bot',
                content: "❌ Sorry, I encountered an error.",
                timestamp: Date.now(),
            });
            setLoading(false);
        }
    });

    const handleSend = () => {
        if (!input.trim()) return;

        const userMsg = input.trim();
        addMessage({
            id: Date.now().toString(),
            role: 'user',
            content: userMsg,
            timestamp: Date.now(),
        });

        setInput('');
        chatMutation.mutate(userMsg);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    return (
        <div className="flex flex-col h-full">
            {/* Mobile Header */}
            <header className="md:hidden flex items-center p-4 border-b border-border bg-background/95 backdrop-blur z-10 sticky top-0">
                <Sheet>
                    <SheetTrigger asChild>
                        <Button variant="ghost" size="icon" className="mr-2">
                            <Menu size={20} />
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="p-0 w-[260px]">
                        <Sidebar />
                    </SheetContent>
                </Sheet>
                <h1 className="font-semibold text-lg flex items-center gap-2">
                    <GraduationCap className="text-primary" />
                    Uni Mentor
                </h1>
            </header>

            {/* Messages Area */}
            <div className="flex-1 overflow-hidden relative" >
                <div className="h-full overflow-y-auto px-4 py-8" ref={scrollRef}>
                    <div className="max-w-3xl mx-auto space-y-8">
                        {messages.length === 0 && (
                            <div className="text-center py-20 space-y-4">
                                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                                    <GraduationCap size={32} className="text-primary" />
                                </div>
                                <h2 className="text-2xl font-bold">Hello! I'm Uni Mentor.</h2>
                                <p className="text-muted-foreground max-w-md mx-auto">
                                    I can help you analyze resumes, plan your career, and generate study schedules from your PDFs.
                                </p>
                            </div>
                        )}

                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                {msg.role === 'bot' && (
                                    <Avatar className="h-8 w-8 border border-border">
                                        <AvatarFallback className="bg-primary text-primary-foreground">AI</AvatarFallback>
                                    </Avatar>
                                )}

                                <div className={`relative px-4 py-3 rounded-2xl max-w-[85%] ${msg.role === 'user'
                                        ? 'bg-primary text-primary-foreground'
                                        : 'bg-muted/50 text-foreground border border-border'
                                    }`}>
                                    <div className="prose prose-invert text-sm leading-relaxed whitespace-pre-wrap">
                                        {msg.role === 'bot'
                                            ? <div dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br />').replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') }} />
                                            : msg.content
                                        }
                                    </div>
                                </div>

                                {msg.role === 'user' && (
                                    <Avatar className="h-8 w-8 border border-border">
                                        <AvatarFallback className="bg-secondary">U</AvatarFallback>
                                    </Avatar>
                                )}
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex gap-4">
                                <Avatar className="h-8 w-8">
                                    <AvatarFallback>AI</AvatarFallback>
                                </Avatar>
                                <div className="bg-muted/50 px-4 py-3 rounded-2xl border border-border">
                                    <div className="flex gap-1 items-center h-6">
                                        <span className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <span className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <span className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Input Area */}
            <div className="p-4 bg-background/95 backdrop-blur border-t border-border">
                <div className="max-w-3xl mx-auto relative">
                    <div className="relative flex items-end gap-2 p-2 rounded-xl border border-input bg-background shadow-sm focus-within:ring-1 focus-within:ring-ring">
                        <Textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask me anything..."
                            className="min-h-[44px] max-h-[200px] border-none focus-visible:ring-0 resize-none py-3 shadow-none overflow-hidden"
                            style={{ height: '44px' }}
                        />
                        <Button
                            onClick={handleSend}
                            disabled={!input.trim() || isLoading}
                            size="icon"
                            className={input.trim() ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}
                        >
                            <Send size={18} />
                        </Button>
                    </div>
                    <div className="text-center text-xs text-muted-foreground mt-2">
                        Uni Mentor can make mistakes. Please verify important information.
                    </div>
                </div>
            </div>
        </div>
    );
}
