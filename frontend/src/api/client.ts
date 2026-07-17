// Thin fetch wrapper — single place that knows the API base URL and how
// errors are shaped, so components never construct URLs or handle raw
// fetch() Response objects directly.
import type { BroadcastRequest, BroadcastResult, Message, Session, Tenant } from "../types";

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const isLocalHost =
  typeof window !== "undefined" &&
  ["localhost", "127.0.0.1"].includes(window.location.hostname);

const API_BASE_URL = configuredApiBaseUrl || (isLocalHost ? "http://localhost:8000" : "");

if (!API_BASE_URL) {
  throw new Error("Missing VITE_API_BASE_URL. Set it to your backend Render URL.");
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(response.status, body || response.statusText);
  }
  return response.json();
}

export const api = {
  listTenants: () => request<Tenant[]>("/api/tenants"),
  listSessions: (tenantId: string) => request<Session[]>(`/api/sessions/${tenantId}`),
  listMessages: (tenantId: string, sessionId: string) =>
    request<Message[]>(`/api/messages/${tenantId}/${sessionId}`),
  sendBroadcast: (payload: BroadcastRequest) =>
    request<BroadcastResult>("/api/broadcast", { method: "POST", body: JSON.stringify(payload) }),
};

export { ApiError };
