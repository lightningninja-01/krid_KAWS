import type { Message } from "../../types";
import { MediaPreview } from "./MediaPreview";

interface MessageBubbleProps {
  message: Message;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isCustomer = message.sender === "customer";
  const sentimentScore = message.metadata?.sentiment_score as number | undefined;

  return (
    <div className={`flex ${isCustomer ? "justify-start" : "justify-end"}`}>
      <div className={`max-w-[70%] ${isCustomer ? "items-start" : "items-end"} flex flex-col`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm ${
            isCustomer
              ? "rounded-bl-sm bg-white text-ink"
              : "rounded-br-sm text-white"
          }`}
          style={!isCustomer ? { backgroundColor: "var(--tenant-accent, #2563EB)" } : undefined}
        >
          {message.text && <p className="whitespace-pre-wrap">{message.text}</p>}
          {message.media && <MediaPreview media={message.media} />}
          {message.status === "FAILED" && (
            <p className="mt-1 text-xs text-danger-soft">Delivery failed</p>
          )}
        </div>
        <div className="mt-1 flex items-center gap-2 px-1">
          <span className="font-mono text-[11px] text-ink-muted">{formatTime(message.created_at)}</span>
          {typeof sentimentScore === "number" && sentimentScore >= 0.75 && (
            <span className="text-[11px] font-medium text-danger">frustrated</span>
          )}
        </div>
      </div>
    </div>
  );
}
