import { TenantSwitcher } from "./TenantSwitcher";

interface SidebarProps {
  onOpenBroadcast: () => void;
}

export function Sidebar({ onOpenBroadcast }: SidebarProps) {
  return (
    <aside className="flex h-full w-64 shrink-0 flex-col bg-sidebar text-sidebar-ink">
      <div className="px-5 py-6">
        <p className="font-display text-lg tracking-tight">Agent Console</p>
        <p className="mt-1 text-xs text-sidebar-ink/50">Multi-tenant WhatsApp ops</p>
      </div>

      <div className="px-5">
        <TenantSwitcher />
      </div>

      <nav className="mt-8 flex-1 px-3">
        <p className="px-2 text-xs font-medium uppercase tracking-wider text-sidebar-ink/40">Monitor</p>
        <a
          href="#"
          className="mt-2 flex items-center rounded-lg px-3 py-2 text-sm font-medium bg-white/5 text-sidebar-ink"
        >
          Live conversations
        </a>
      </nav>

      <div className="p-4">
        <button
          onClick={onOpenBroadcast}
          className="w-full rounded-lg py-2.5 text-sm font-semibold text-white transition-opacity hover:opacity-90"
          style={{ backgroundColor: "var(--tenant-accent, #2563EB)" }}
        >
          New broadcast
        </button>
      </div>
    </aside>
  );
}
