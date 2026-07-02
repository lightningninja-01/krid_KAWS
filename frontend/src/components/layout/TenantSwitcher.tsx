import { useTenantStore } from "../../store/tenantStore";

export function TenantSwitcher() {
  const { tenants, activeTenant, setActiveTenantId, isLoading } = useTenantStore();

  if (isLoading) {
    return <div className="h-16 animate-pulse rounded-lg bg-white/5" />;
  }

  if (tenants.length === 0) {
    return <p className="text-xs text-sidebar-ink/50">No tenants configured yet.</p>;
  }

  return (
    <div className="space-y-1.5">
      {tenants.map((tenant) => {
        const isActive = tenant.id === activeTenant?.id;
        return (
          <button
            key={tenant.id}
            onClick={() => setActiveTenantId(tenant.id)}
            className={`flex w-full items-center gap-2.5 rounded-lg border px-3 py-2.5 text-left transition-colors ${
              isActive ? "border-white/15 bg-white/10" : "border-transparent hover:bg-white/5"
            }`}
          >
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: tenant.branding.primary_color }}
              aria-hidden="true"
            />
            <span className="min-w-0">
              <span className="block truncate text-sm font-medium">{tenant.company_name}</span>
              <span className="block truncate font-mono text-[11px] text-sidebar-ink/45">
                {tenant.phone_number_id}
              </span>
            </span>
          </button>
        );
      })}
    </div>
  );
}
