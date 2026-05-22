import { useState, useEffect, useRef, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  data: unknown;
  timestamp: string;
}

interface UseWebSocketReturn {
  messages: WebSocketMessage[];
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
}

export function useWebSocket(scanId: string | null): UseWebSocketReturn {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 10;
  const scanIdRef = useRef(scanId);

  scanIdRef.current = scanId;

  const connect = useCallback(() => {
    if (!scanIdRef.current) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/scans/${scanIdRef.current}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttemptsRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setMessages((prev) => [...prev, message]);
        setLastMessage(message);
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;

      if (
        scanIdRef.current &&
        reconnectAttemptsRef.current < maxReconnectAttempts
      ) {
        const delay = Math.min(1000 * 2 ** reconnectAttemptsRef.current, 30000);
        reconnectAttemptsRef.current += 1;
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    if (!scanId) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setMessages([]);
      setLastMessage(null);
      setIsConnected(false);
      return;
    }

    reconnectAttemptsRef.current = 0;
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [scanId, connect]);

  return { messages, isConnected, lastMessage };
}
