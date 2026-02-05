
'use client';

import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Plus, Upload, MessageSquare, User, History } from 'lucide-react';
import { useChatStore } from '@/lib/store';
import { uploadApi } from '@/lib/api';
import { useMutation } from '@tanstack/react-query';
import { useRef } from 'react';

export default function Sidebar() {
    const clearMessages = useChatStore((state) => state.clearMessages);
    const addMessage = useChatStore((state) => state.addMessage);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const uploadMutation = useMutation({
        mutationFn: uploadApi,
        onSuccess: (data) => {
            addMessage({
                id: Date.now().toString(),
                role: 'bot',
                content: data.reply,
                timestamp: Date.now(),
            });
        },
        onError: () => {
            addMessage({
                id: Date.now().toString(),
                role: 'bot',
                content: "❌ Failed to upload file.",
                timestamp: Date.now(),
            });
        }
    });

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            addMessage({
                id: Date.now().toString(),
                role: 'user',
                content: `📂 Uploading ${file.name}...`,
                timestamp: Date.now(),
            });
            uploadMutation.mutate(file);
        }
    };

    return (
        <div className="flex flex-col h-full p-4 gap-4">
            <Button
                variant="outline"
                className="justify-start gap-2 w-full border-dashed border-white/20 hover:bg-accent"
                onClick={clearMessages}
            >
                <Plus size={16} />
                New Conversation
            </Button>

            <ScrollArea className="flex-1 -mx-4 px-4">
                <div className="space-y-4 py-4">
                    <div className="px-3 py-2">
                        <h2 className="mb-2 px-4 text-xs font-semibold tracking-tight text-muted-foreground">
                            Tools
                        </h2>
                        <div className="space-y-1">
                            <Button variant="ghost" className="w-full justify-start gap-2" onClick={() => fileInputRef.current?.click()}>
                                <Upload size={16} />
                                Upload PDF
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    className="hidden"
                                    accept=".pdf"
                                    onChange={handleFileChange}
                                />
                            </Button>
                        </div>
                    </div>

                    <div className="px-3 py-2">
                        <h2 className="mb-2 px-4 text-xs font-semibold tracking-tight text-muted-foreground">
                            History
                        </h2>
                        <div className="space-y-1">
                            <Button variant="ghost" className="w-full justify-start gap-2 font-normal text-muted-foreground">
                                <History size={16} />
                                Previous Chat ...
                            </Button>
                        </div>
                    </div>
                </div>
            </ScrollArea>

            <div className="mt-auto pt-4 border-t border-border">
                <Button variant="ghost" className="w-full justify-start gap-2">
                    <div className="h-6 w-6 rounded bg-primary/20 flex items-center justify-center">
                        <User size={14} />
                    </div>
                    <div className="flex flex-col items-start text-xs">
                        <span className="font-medium">User Account</span>
                        <span className="text-muted-foreground">Student</span>
                    </div>
                </Button>
            </div>
        </div>
    );
}
