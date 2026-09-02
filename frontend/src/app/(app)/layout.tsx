"use client";

import { AppShell } from "@/components/layout/AppShell";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

/**
 * This layout wraps all authenticated app routes.
 * It applies the AppShell (sidebar + header) and ProtectedRoute (auth guard).
 * The /login page has its own layout and is NOT nested here.
 */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <AppShell>{children}</AppShell>
    </ProtectedRoute>
  );
}
