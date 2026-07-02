// Active-tenant selection, shared across the whole dashboard via Context.
// Deliberately not pulling in a state library for one piece of shared
// state — Context is the right-sized tool here.
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api } from "../api/client";
import type { Tenant } from "../types";

interface TenantStoreValue {
  tenants: Tenant[];
  activeTenant: Tenant | null;
  setActiveTenantId: (id: string) => void;
  isLoading: boolean;
  error: string | null;
}

const TenantContext = createContext<TenantStoreValue | undefined>(undefined);

export function TenantProvider({ children }: { children: ReactNode }) {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [activeTenantId, setActiveTenantId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listTenants()
      .then((fetched) => {
        setTenants(fetched);
        if (fetched.length > 0) setActiveTenantId(fetched[0].id);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load tenants"))
      .finally(() => setIsLoading(false));
  }, []);

  const activeTenant = useMemo(
    () => tenants.find((t) => t.id === activeTenantId) ?? null,
    [tenants, activeTenantId]
  );

  // Drive the CSS custom property that the whole UI reads for its accent
  // color — this is the mechanism behind the tenant-branded theming.
  useEffect(() => {
    const accent = activeTenant?.branding.primary_color ?? "#2563EB";
    document.documentElement.style.setProperty("--tenant-accent", accent);
  }, [activeTenant]);

  const value: TenantStoreValue = {
    tenants,
    activeTenant,
    setActiveTenantId,
    isLoading,
    error,
  };

  return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>;
}

export function useTenantStore(): TenantStoreValue {
  const ctx = useContext(TenantContext);
  if (!ctx) throw new Error("useTenantStore must be used within a TenantProvider");
  return ctx;
}
