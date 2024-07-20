import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Save, ChevronLeft, ChevronRight, Edit2, Check, Copy } from 'lucide-react';

interface GameInfo {
  [key: string]: string;
}

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const BACKEND_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

const RPGGameUI: React.FC = () => {
  const [gameInfo, setGameInfo] = useState<GameInfo>({});
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState<string>('');
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [editingMessageId, setEditingMessageId] = useState<number | null>(null);
  const [editedContent, setEditedContent] = useState<string>('');
  const [editingGameInfoField, setEditingGameInfoField] = useState<string | null>(null);
  const [editedGameInfoContent, setEditedGameInfoContent] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [wsConnected, setWsConnected] = useState<boolean>(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const editTextareaRef = useRef<HTMLTextAreaElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const initWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    wsRef.current = new WebSocket(WS_URL);

    wsRef.current.onopen = () => {
      console.log('WebSocket connection established');
      setWsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
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
                id: prevHistory.length,
                role: 'assistant',
                content: data.content,
                timestamp: new Date().toLocaleString(),
              }
            ];
          }
        });
      } else if (data.type === 'end') {
        setIsGenerating(false);
        if (data.should_exit) {
          // Handle game exit if needed
        }
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsConnected(false);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket connection closed');
      setWsConnected(false);
      // Attempt to reconnect after a delay
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('Attempting to reconnect...');
        initWebSocket();
      }, 5000);
    };
  }, []);

  useEffect(() => {
    fetchGameInfo();
    fetchChatHistory();
    initWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [initWebSocket]);

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

  useEffect(() => {
    if (editTextareaRef.current && editingMessageId !== null) {
      const message = chatHistory.find(msg => msg.id === editingMessageId);
      if (message) {
        editTextareaRef.current.style.height = 'auto';
        editTextareaRef.current.style.height = `${editTextareaRef.current.scrollHeight}px`;
      }
    }
  }, [editingMessageId, chatHistory]);

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
      setChatHistory(data.history);
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  const handleSendMessage = () => {
    if (!userInput.trim() || isGenerating || !wsConnected) return;

    const newUserMessage: ChatMessage = {
      id: chatHistory.length,
      role: 'user',
      content: userInput,
      timestamp: new Date().toLocaleString(),
    };
    setChatHistory(prevHistory => [...prevHistory, newUserMessage]);
    setUserInput('');
    setIsGenerating(true);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ content: userInput }));
    } else {
      console.error('WebSocket is not connected');
      setIsGenerating(false);
      initWebSocket();
    }
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleEditMessage = (id: number) => {
    const messageToEdit = chatHistory.find(msg => msg.id === id);
    if (messageToEdit) {
      setEditingMessageId(id);
      setEditedContent(messageToEdit.content);
    }
  };

  const handleSaveEditedMessage = async (id: number) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/edit_message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, content: editedContent }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        setChatHistory(chatHistory.map(msg => msg.id === id ? { ...msg, content: editedContent } : msg));
        setEditingMessageId(null);
        setEditedContent('');
      }
    } catch (error) {
      console.error('Failed to save edited message:', error);
    }
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

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy text to clipboard:', err);
    }
  };

  return (
      <div className="bg-[#0d1117] min-h-screen text-gray-300 flex flex-col">
        <header className="bg-[#161b22] p-4 shadow-md z-30 relative">
          <h1 className="text-2xl font-bold text-gray-100">Virtual-Game-Master</h1>
        </header>

        <main className="flex-grow flex overflow-hidden relative">
          {/* Sidebar */}
          <aside
              className={`bg-[#161b22] transition-all duration-300 ease-in-out ${
                  isSidebarOpen ? 'w-80 lg:w-96 xl:w-[480px] 2xl:w-[640px]' : 'w-0'
              } overflow-hidden flex flex-col absolute left-0 top-0 bottom-0 z-20 h-full`}
          >
            <div className="p-4 border-b border-gray-700 flex justify-between items-center">
              <h2 className="text-xl pr-8 font-semibold text-gray-100">Game Information</h2>
            </div>
            <div className="flex-grow overflow-y-auto p-4 space-y-4">
              {Object.entries(gameInfo).map(([key, value]) => (
                  <div key={key} className="bg-[#1c2128] p-4 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="font-semibold text-gray-200">{key}</h3>
                      {editingGameInfoField !== key && (
                          <button
                              onClick={() => handleEditGameInfoField(key)}
                              className="text-gray-400 hover:text-gray-200 transition-colors"
                          >
                            <Edit2 size={16} />
                          </button>
                      )}
                    </div>
                    {editingGameInfoField === key ? (
                        <div className="flex items-center mt-2">
                  <textarea
                      value={editedGameInfoContent}
                      onChange={(e) => setEditedGameInfoContent(e.target.value)}
                      className="flex-grow bg-[#0d1117] p-2 rounded-lg text-gray-200 resize-none"
                      rows={5}
                  />
                          <button
                              onClick={() => handleSaveEditedGameInfoField(key)}
                              className="ml-2 bg-green-500 hover:bg-green-600 text-white p-2 rounded-lg transition-colors"
                          >
                            <Check size={16} />
                          </button>
                        </div>
                    ) : (
                        <pre className="text-gray-400 whitespace-pre-wrap break-words">
                  {value}
                </pre>
                    )}
                  </div>
              ))}
            </div>
            <div className="p-4 border-t border-gray-700">
              <button
                  onClick={handleSaveGame}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors flex items-center justify-center"
              >
                <Save size={18} className="mr-2" />
                Save Game
              </button>
            </div>
          </aside>

          {/* Chat Section */}
          <section className="flex-grow flex flex-col bg-[#0d1117] overflow-hidden relative w-full h-full">
            {/* Sidebar Toggle Button */}
            <div className="absolute top-4 left-4 z-30">
              <button
                  onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                  className="bg-[#1c2128] hover:bg-[#2d333b] text-gray-300 p-2 rounded-full transition-colors"
              >
                {isSidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
              </button>
            </div>

            {/* Chat History Window */}
            <div className="flex-grow overflow-hidden p-4 mt-16 mb-24">
              <div
                  ref={chatContainerRef}
                  className="h-full overflow-y-auto bg-[#1c2128] rounded-lg border border-gray-700 p-4"
              >
                {chatHistory.map((message) => (
                    <div
                        key={message.id}
                        className={`flex gap-4 p-4 ${
                            message.role === 'assistant' ? 'bg-[#2d333b]' : ''
                        } rounded-lg mb-4`}
                    >
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
                                onClick={() => copyToClipboard(message.content)}
                            >
                              <Copy size={16} />
                            </button>
                            <button
                                className="text-gray-400 hover:text-blue-500"
                                title="Edit"
                                onClick={() => handleEditMessage(message.id)}
                            >
                              <Edit2 size={16} />
                            </button>
                          </div>
                        </div>
                        {editingMessageId === message.id ? (
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
                                  onClick={() => handleSaveEditedMessage(message.id)}
                                  className="ml-2 bg-green-500 hover:bg-green-600 text-white p-2 rounded-lg transition-colors"
                              >
                                <Check size={16}/>
                              </button>
                            </div>
                        ) : (
                            <div className="text-gray-200 whitespace-pre-wrap break-words overflow-auto">
                              {message.content.trimStart()}
                              {message.role === 'assistant' && message.id === chatHistory.length - 1 && isGenerating && (
                                  <span className="animate-pulse">▋</span>
                              )}
                            </div>
                        )}
                      </div>
                    </div>
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

            {/* Fixed Input Area */}
            <div className="fixed bottom-0 left-0 right-0 p-4 bg-[#0d1117] border-t border-gray-700">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-start gap-4 bg-[#1c2128] rounded-lg overflow-hidden p-2">
              <textarea
                  ref={textareaRef}
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="flex-grow bg-transparent p-3 focus:outline-none text-gray-200 resize-none min-h-[50px] max-h-[75px] overflow-y-auto"
                  placeholder="Enter your message... (Shift+Enter for new line)"
                  rows={1}
                  disabled={isGenerating || !wsConnected}
              />
                  <button
                      onClick={handleSendMessage}
                      className={`text-gray-400 hover:text-blue-500 p-3 mt-1 ${
                          isGenerating || !wsConnected ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                      title="Send"
                      disabled={isGenerating || !wsConnected}
                  >
                    <Send size={24} />
                  </button>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
  );
};

export default RPGGameUI;