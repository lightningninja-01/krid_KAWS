import type { Session } from "../../types";
import { TypingIndicator } from "./TypingIndicator";

interface ChatListProps {
  sessions: Session[];
  selectedSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
}

const STATUS_LABEL: Record<Session["status"], string> = {
  WAITING_FOR_BOT: "Waiting",
  AGENT_RESPONDING: "Responding",
  RESOLVED: "Resolved",
  NEEDS_HUMAN: "Needs human",
};

function formatRelativeTime(iso: string | null): string {
  if (!iso) return "—";
  const diffMs = Date.now() - new Date(iso).getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  return `${diffHr}h ago`;
}

export function ChatList({ sessions, selectedSessionId, onSelectSession }: ChatListProps) {
  if (sessions.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center px-6 text-center">
        <p className="font-display text-lg text-ink-muted">No conversations yet</p>
        <p className="mt-1 text-sm text-ink-muted">
          Once a customer messages this tenant's WhatsApp number, it'll show up here.
        </p>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-border overflow-y-auto">
      {sessions.map((session) => {
        const isSelected = session.id === selectedSessionId;
        const isNeedsHuman = session.status === "NEEDS_HUMAN";
        return (
          <li key={session.id}>
            <button
              onClick={() => onSelectSession(session.id)}
              className={`flex w-full flex-col gap-1 px-4 py-3 text-left transition-colors ${
                isSelected ? "bg-white" : "hover:bg-white/60"
              } ${isNeedsHuman ? "border-l-2 border-danger bg-danger-soft/40" : "border-l-2 border-transparent"}`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate font-mono text-sm font-medium text-ink">{session.customer_phone}</span>
                <span className="shrink-0 text-xs text-ink-muted">{formatRelativeTime(session.last_message_at)}</span>
              </div>
              <div className="flex items-center gap-2">
                {session.status === "AGENT_RESPONDING" ? (
                  <TypingIndicator size="sm" />
                ) : (
                  <span
                    className={`text-xs ${isNeedsHuman ? "font-medium text-danger" : "text-ink-muted"}`}
                  >
                    {STATUS_LABEL[session.status]}
                  </span>
                )}
              </div>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
