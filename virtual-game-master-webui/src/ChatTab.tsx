import React, { useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { ChatMessageType } from "./types";
import ChatMessage from "./ChatMessage";

interface ChatTabProps {
    chatHistory: ChatMessageType[];
    userInput: string;
    isGenerating: boolean;
    isConnected: boolean;
    setUserInput: (input: string) => void;
    handleSendMessage: () => void;
    handleEditMessage: (id: number, content: string) => void;
    handleDeleteMessage: (id: number) => void;
    handleRegenerateLastMessage: () => void;
}

const ChatTab: React.FC<ChatTabProps> = ({
                                             chatHistory,
                                             userInput,
                                             isGenerating,
                                             isConnected,
                                             setUserInput,
                                             handleSendMessage,
                                             handleEditMessage,
                                             handleDeleteMessage,
                                             handleRegenerateLastMessage,
                                         }) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const chatContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 5 * 24)}px`;
        }
    }, [userInput]);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [chatHistory]);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <section className="flex-grow flex flex-col bg-[#0d1117] overflow-hidden relative w-full h-full">
            <div className="flex-grow overflow-hidden p-4 pb-24">
                <div
                    ref={chatContainerRef}
                    className="h-full overflow-y-auto bg-[#1c2128] rounded-lg border border-gray-700 p-4"
                >
                    {chatHistory.map((message, index) => (
                        <ChatMessage
                            key={message.id}
                            message={message}
                            onEdit={handleEditMessage}
                            onDelete={handleDeleteMessage}
                            onRegenerate={handleRegenerateLastMessage}
                            isGenerating={isGenerating}
                            isLastMessage={index === chatHistory.length - 1}
                        />
                    ))}
                    {isGenerating && (!chatHistory.length || chatHistory[chatHistory.length - 1].role !== 'assistant') && (
                        <div className="flex gap-4 p-4 bg-[#2d333b] rounded-lg mb-4">
                            <img
                                className="h-10 w-10 rounded-full flex-shrink-0"
                                src="https://dummyimage.com/256x256/354ea1/ffffff&text=GM"
                                alt="Game Master"
                            />
                            <div className="flex flex-col flex-grow overflow-hidden">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="font-bold text-gray-200">Game Master</span>
                                    <span className="text-xs text-gray-400">{new Date().toLocaleString()}</span>
                                </div>
                                <div className="text-gray-200 whitespace-pre-wrap break-words overflow-auto">
                                    <span className="animate-pulse">▋</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="fixed bottom-0 left-0 right-0 p-4 bg-[#0d1117] border-t border-gray-700">
                <div className="max-w-4xl mx-auto">
                    <div className="flex items-start gap-4 bg-[#1c2128] rounded-lg overflow-hidden p-2">
                        <textarea
                            ref={textareaRef}
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            className="flex-grow bg-transparent p-3 focus:outline-none text-gray-200 resize-none min-h-[50px] max-h-[150px] overflow-y-auto"
                            placeholder="Enter your message... (Shift+Enter for new line)"
                            rows={1}
                            disabled={isGenerating || !isConnected}
                        />
                        <button
                            onClick={handleSendMessage}
                            className={`text-gray-400 hover:text-blue-500 p-3 mt-1 ${
                                isGenerating || !isConnected ? 'opacity-50 cursor-not-allowed' : ''
                            }`}
                            title="Send"
                            disabled={isGenerating || !isConnected}
                        >
                            <Send size={24} />
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default ChatTab;