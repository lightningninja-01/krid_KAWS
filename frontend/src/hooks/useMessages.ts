// Polls the message history for the selected session. Same rationale as
// useSessions — short-interval polling for a "live" feel without WebSockets.
import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { Message } from "../types";

const POLL_INTERVAL_MS = 2000;

export function useMessages(tenantId: string | null, sessionId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!tenantId || !sessionId) {
      setMessages([]);
      return;
    }

    let cancelled = false;

    const fetchMessages = async () => {
      try {
        const result = await api.listMessages(tenantId, sessionId);
        if (!cancelled) {
          setMessages(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load messages");
      }
    };

    fetchMessages();
    intervalRef.current = setInterval(fetchMessages, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [tenantId, sessionId]);

  return { messages, error };
}
