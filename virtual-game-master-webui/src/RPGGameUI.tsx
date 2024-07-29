import React, { useState, useEffect, useCallback } from 'react';
import useWebSocket from './useWebSocket';
import ChatTab from './ChatTab';
import GameStateTab from './GameStateTab';
import { ChatMessageType, GameInfo } from "./types";

const BACKEND_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

const RPGGameUI: React.FC = () => {
  const [gameInfo, setGameInfo] = useState<GameInfo>({});
  const [chatHistory, setChatHistory] = useState<ChatMessageType[]>([]);
  const [userInput, setUserInput] = useState<string>('');
  const [editingGameInfoField, setEditingGameInfoField] = useState<string | null>(null);
  const [editedGameInfoContent, setEditedGameInfoContent] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'gameState'>('chat');
  const [nextMessageId, setNextMessageId] = useState<number>(0);

  const handleWebSocketMessage = useCallback((data: any) => {
    if (data.type === 'chunk') {
      setChatHistory(prevHistory => {
        const updatedHistory = [...prevHistory];
        const lastMessage = updatedHistory[updatedHistory.length - 1];

        if (lastMessage && lastMessage.role === 'assistant') {
          return updatedHistory.map((msg, index) =>
              index === updatedHistory.length - 1
                  ? { ...msg, content: msg.content + data.content }
                  : msg
          );
        } else {
          return [
            ...updatedHistory,
            {
              id: nextMessageId + 1,
              role: 'assistant',
              content: data.content,
              timestamp: new Date().toLocaleString(),
            }
          ];
        }
      });
    } else if (data.type === 'end') {
      setIsGenerating(false);
      setNextMessageId(data.next_message_id)
      if (data.should_exit) {
        // Handle game exit if needed
      }
    }
  }, [nextMessageId]);

  const { isConnected, sendMessage } = useWebSocket({
    url: WS_URL,
    onMessage: handleWebSocketMessage,
  });

  useEffect(() => {
    fetchGameInfo();
    fetchChatHistory();
  }, []);

  const fetchGameInfo = async (): Promise<void> => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/get_template_fields`);
      const data = await response.json();
      setGameInfo(data.fields);
    } catch (error) {
      console.error('Failed to fetch game info:', error);
    }
  };

  const fetchChatHistory = async (): Promise<void> => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/get_chat_history`);
      const data = await response.json();
      setNextMessageId(data.next_message_id)
      setChatHistory(data.history);
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  const handleSendMessage = () => {
    if (!userInput.trim() || isGenerating || !isConnected) return;

    const newUserMessage: ChatMessageType = {
      id: nextMessageId,
      role: 'user',
      content: userInput,
      timestamp: new Date().toLocaleString(),
    };
    setChatHistory(prevHistory => [...prevHistory, newUserMessage]);
    setUserInput('');
    setIsGenerating(true);

    sendMessage(userInput);
  };

  const handleSaveGame = async (): Promise<void> => {
    try {
      await fetch(`${BACKEND_URL}/api/save_game`, { method: 'POST' });
      alert('Game saved successfully!');
    } catch (error) {
      console.error('Failed to save game:', error);
      alert('Failed to save game. Please try again.');
    }
  };

  const handleEditMessage = async (id: number, content: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/edit_message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, content }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        setChatHistory(chatHistory.map(msg => msg.id === id ? { ...msg, content } : msg));
      }
    } catch (error) {
      console.error('Failed to save edited message:', error);
    }
  };

  const handleDeleteMessage = async (id: number) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/delete_message/${id}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (data.status === 'success') {
        setNextMessageId(data.next_message_id)
        await fetchChatHistory()
      }
    } catch (error) {
      console.error('Failed to delete message:', error);
    }
  };

  const handleRegenerateLastMessage = async () => {
    if (chatHistory.length < 2) return;

    const lastAssistantMessage = chatHistory[chatHistory.length - 1];
    const lastUserMessage = chatHistory[chatHistory.length - 2];

    await handleDeleteMessage(lastAssistantMessage.id)
    await handleDeleteMessage(lastUserMessage.id).then(() => {

      const newUserMessage: ChatMessageType = {
        id: nextMessageId,
        role: 'user',
        content: lastUserMessage.content,
        timestamp: new Date().toLocaleString(),
      };
      setChatHistory(prevHistory => [...prevHistory, newUserMessage]);
      setUserInput('');

      setIsGenerating(true);

      // Resend the last user message
      sendMessage(lastUserMessage.content);

    })


  };

  const handleEditGameInfoField = (field: string) => {
    setEditingGameInfoField(field);
    setEditedGameInfoContent(gameInfo[field]);
  };

  const handleSaveEditedGameInfoField = async (field: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/update_template_fields`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fields: { [field]: editedGameInfoContent } }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        setGameInfo({ ...gameInfo, [field]: editedGameInfoContent });
        setEditingGameInfoField(null);
        setEditedGameInfoContent('');
      }
    } catch (error) {
      console.error('Failed to save edited game info field:', error);
    }
  };

  return (
      <div className="bg-[#0d1117] min-h-screen text-gray-300 flex flex-col">
        <header className="bg-[#161b22] p-4 shadow-md z-30 relative flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-100">Virtual-Game-Master</h1>
          <div className="flex space-x-4">
            <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'chat' ? 'bg-[#2d333b] text-white' : 'text-gray-400 hover:text-white'
                }`}
            >
              Chat
            </button>
            <button
                onClick={() => setActiveTab('gameState')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'gameState' ? 'bg-[#2d333b] text-white' : 'text-gray-400 hover:text-white'
                }`}
            >
              Game State
            </button>
          </div>
        </header>

        <main className="flex-grow flex overflow-hidden relative">
          {activeTab === 'chat' && (
              <ChatTab
                  chatHistory={chatHistory}
                  userInput={userInput}
                  isGenerating={isGenerating}
                  isConnected={isConnected}
                  setUserInput={setUserInput}
                  handleSendMessage={handleSendMessage}
                  handleEditMessage={handleEditMessage}
                  handleDeleteMessage={handleDeleteMessage}
                  handleRegenerateLastMessage={handleRegenerateLastMessage}
              />
          )}

          {activeTab === 'gameState' && (
              <GameStateTab
                  gameInfo={gameInfo}
                  editingGameInfoField={editingGameInfoField}
                  editedGameInfoContent={editedGameInfoContent}
                  handleEditGameInfoField={handleEditGameInfoField}
                  handleSaveEditedGameInfoField={handleSaveEditedGameInfoField}
                  setEditedGameInfoContent={setEditedGameInfoContent}
                  handleSaveGame={handleSaveGame}
              />
          )}
        </main>
      </div>
  );
};

export default RPGGameUI;