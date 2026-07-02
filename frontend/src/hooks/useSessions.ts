// Polls the session list for the active tenant every 2s — this is the
// "Live Chat Monitor" mechanism. Polling was chosen over WebSockets/SSE
// deliberately: it satisfies "live" without the connection-management
// complexity that would add real risk to a 48-hour-scoped project.
import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { Session } from "../types";

const POLL_INTERVAL_MS = 2000;

export function useSessions(tenantId: string | null) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!tenantId) return;

    let cancelled = false;

    const fetchSessions = async () => {
      try {
        const result = await api.listSessions(tenantId);
        if (!cancelled) {
          setSessions(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load sessions");
      }
    };

    fetchSessions();
    intervalRef.current = setInterval(fetchSessions, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [tenantId]);

  return { sessions, error };
}
