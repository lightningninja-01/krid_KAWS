import { useState } from "react";
import { Sidebar } from "../components/layout/Sidebar";
import { ChatList } from "../components/chat/ChatList";
import { ConversationWindow } from "../components/chat/ConversationWindow";
import { BroadcastDrawer } from "../components/broadcast/BroadcastDrawer";
import { useTenantStore } from "../store/tenantStore";
import { useSessions } from "../hooks/useSessions";

export function Dashboard() {
  const { activeTenant, isLoading, error } = useTenantStore();
  const { sessions } = useSessions(activeTenant?.id ?? null);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [isBroadcastOpen, setIsBroadcastOpen] = useState(false);

  const selectedSession = sessions.find((s) => s.id === selectedSessionId) ?? null;

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-canvas">
        <p className="text-sm text-danger">Couldn't reach the API: {error}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-canvas">
        <p className="font-display text-lg text-ink-muted">Loading dashboard…</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-canvas">
      <Sidebar onOpenBroadcast={() => setIsBroadcastOpen(true)} />

      <div className="flex min-w-0 flex-1">
        <section className="w-80 shrink-0 border-r border-border bg-canvas">
          <div className="border-b border-border px-4 py-3.5">
            <h1 className="font-display text-lg">{activeTenant?.company_name ?? "Conversations"}</h1>
            <p className="text-xs text-ink-muted">{sessions.length} active conversation{sessions.length === 1 ? "" : "s"}</p>
          </div>
          <ChatList
            sessions={sessions}
            selectedSessionId={selectedSessionId}
            onSelectSession={setSelectedSessionId}
          />
        </section>

        <section className="min-w-0 flex-1 bg-canvas">
          <ConversationWindow tenantId={activeTenant?.id ?? null} session={selectedSession} />
        </section>
      </div>

      <BroadcastDrawer isOpen={isBroadcastOpen} onClose={() => setIsBroadcastOpen(false)} />
    </div>
  );
}
