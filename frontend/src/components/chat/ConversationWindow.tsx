import { useEffect, useRef } from "react";
import type { Session } from "../../types";
import { useMessages } from "../../hooks/useMessages";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

interface ConversationWindowProps {
  tenantId: string | null;
  session: Session | null;
}

export function ConversationWindow({ tenantId, session }: ConversationWindowProps) {
  const { messages } = useMessages(tenantId, session?.id ?? null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  if (!session) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-center">
        <p className="font-display text-xl text-ink-muted">Select a conversation</p>
        <p className="mt-1 text-sm text-ink-muted">Choose a customer from the list to audit the agent's replies.</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <header className="flex items-center justify-between border-b border-border bg-white px-5 py-3.5">
        <div>
          <p className="font-mono text-sm font-medium text-ink">{session.customer_phone}</p>
          <p className="text-xs text-ink-muted">
            Session started {new Date(session.created_at).toLocaleDateString()}
          </p>
        </div>
        {session.status === "NEEDS_HUMAN" && (
          <span className="rounded-full bg-danger-soft px-2.5 py-1 text-xs font-medium text-danger">
            Needs human
          </span>
        )}
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto px-5 py-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {session.status === "AGENT_RESPONDING" && (
          <div className="flex justify-end">
            <div className="rounded-2xl rounded-br-sm bg-white px-4 py-3">
              <TypingIndicator />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
