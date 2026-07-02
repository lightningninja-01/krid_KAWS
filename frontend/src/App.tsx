import { TenantProvider } from "./store/tenantStore";
import { Dashboard } from "./pages/Dashboard";

export default function App() {
  return (
    <TenantProvider>
      <Dashboard />
    </TenantProvider>
  );
}
