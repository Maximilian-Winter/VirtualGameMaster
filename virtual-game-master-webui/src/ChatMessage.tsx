import React, { useState, useRef, useEffect } from 'react';
import { Edit2, Check, Copy } from 'lucide-react';

interface ChatMessageProps {
  message: {
    id: number;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  };
  onEdit: (id: number, content: string) => void;
  isGenerating: boolean;
  isLastMessage: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onEdit, isGenerating, isLastMessage }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(message.content);
  const editTextareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isEditing && editTextareaRef.current) {
      editTextareaRef.current.style.height = 'auto';
      editTextareaRef.current.style.height = `${editTextareaRef.current.scrollHeight}px`;
    }
  }, [isEditing, editedContent]);

  const handleEditClick = () => {
    setIsEditing(true);
    setEditedContent(message.content);
  };

  const handleSaveEdit = () => {
    onEdit(message.id, editedContent);
    setIsEditing(false);
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
    } catch (err) {
      console.error('Failed to copy text to clipboard:', err);
    }
  };

  return (
    <div className={`flex gap-4 p-4 ${
      message.role === 'assistant' ? 'bg-[#2d333b]' : ''
    } rounded-lg mb-4`}>
      <img
        className="h-10 w-10 rounded-full flex-shrink-0"
        src={`https://dummyimage.com/256x256/354ea1/ffffff&text=${
          message.role === 'user' ? 'P' : 'GM'
        }`}
        alt={message.role === 'user' ? 'Player' : 'Game Master'}
      />
      <div className="flex flex-col flex-grow overflow-hidden">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-gray-200">
              {message.role === 'user' ? 'Player' : 'Game Master'}
            </span>
            <span className="text-xs text-gray-400">{message.timestamp}</span>
          </div>
          <div className="flex gap-2">
            <button
              className="text-gray-400 hover:text-blue-500"
              title="Copy"
              onClick={copyToClipboard}
            >
              <Copy size={16} />
            </button>
            <button
              className="text-gray-400 hover:text-blue-500"
              title="Edit"
              onClick={handleEditClick}
            >
              <Edit2 size={16} />
            </button>
          </div>
        </div>
        {isEditing ? (
          <div className="flex items-center">
            <textarea
              ref={editTextareaRef}
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className={`flex-grow p-2 rounded-lg text-gray-200 resize-none ${
                message.role === 'assistant'
                  ? 'bg-[#3a404b]'
                  : 'bg-[#2d333b]'
              }`}
              rows={3}
            />
            <button
              onClick={handleSaveEdit}
              className="ml-2 bg-green-500 hover:bg-green-600 text-white p-2 rounded-lg transition-colors"
            >
              <Check size={16}/>
            </button>
          </div>
        ) : (
          <div className="text-gray-200 whitespace-pre-wrap break-words overflow-auto">
            {message.content.trimStart()}
            {message.role === 'assistant' && isLastMessage && isGenerating && (
              <span className="animate-pulse">▋</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
