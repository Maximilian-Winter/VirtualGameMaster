// types.ts

export interface ChatMessageType {
    id: number;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

export interface GameInfo {
    [key: string]: string;
}