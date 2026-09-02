/**
 * Standalone layout for the login page.
 * This layout is intentionally minimal — no sidebar, no header, no AppShell.
 * It inherits global CSS (fonts, CSS vars) from the root layout but nothing else.
 */
export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
