import { useState, useEffect, useRef, useCallback } from 'react';

interface WebSocketHookOptions {
  url: string;
  onMessage: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

const useWebSocket = ({ url, onMessage, onConnect, onDisconnect }: WebSocketHookOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    wsRef.current = new WebSocket(url);

    wsRef.current.onopen = () => {
      console.log('WebSocket connection established');
      setIsConnected(true);
      if (onConnect) onConnect();
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket connection closed');
      setIsConnected(false);
      if (onDisconnect) onDisconnect();
      // Attempt to reconnect after a delay
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('Attempting to reconnect...');
        connect();
      }, 5000);
    };
  }, [url, onMessage, onConnect, onDisconnect]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ content: message }));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);

  return { isConnected, sendMessage };
};

export default useWebSocket;
