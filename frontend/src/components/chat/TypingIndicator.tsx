// The signature element: an animated three-dot pulse rendered in the
// active tenant's accent color, used both inline in the chat list and
// inside the conversation window. This is the visible representation of
// AGENT_RESPONDING, which the backend sets the instant the Acknowledge
// node fires — so what the business owner sees here genuinely reflects
// the agent "thinking" in real time (within the polling interval).
interface TypingIndicatorProps {
  size?: "sm" | "md";
}

export function TypingIndicator({ size = "md" }: TypingIndicatorProps) {
  const dotSize = size === "sm" ? "h-1.5 w-1.5" : "h-2 w-2";
  return (
    <span className="inline-flex items-center gap-1" role="status" aria-label="Agent is typing">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className={`${dotSize} animate-pulse-dot rounded-full`}
          style={{ backgroundColor: "var(--tenant-accent, #2563EB)", animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </span>
  );
}
