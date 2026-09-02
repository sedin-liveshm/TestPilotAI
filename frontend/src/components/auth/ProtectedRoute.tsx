"use client";
import { useRouter } from 'next/navigation';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';
import { useEffect } from 'react';
import { Spinner } from '@/components/ui/spinner';

/**
 * Protects routes based on authentication status.
 * - Skips protection for the /login page (public).
 * - Shows a spinner while the auth status is being resolved.
 * - Redirects unauthenticated users to /login.
 */
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { status, checkSession } = useAuthStore();

  // Initial session verification
  useEffect(() => {
    if (status === 'idle') {
      checkSession();
    }
  }, [status, checkSession]);

  // Redirect when unauthenticated and trying to access a protected page
  useEffect(() => {
    if (status === 'unauthenticated' && pathname !== '/login') {
      router.replace('/login');
    }
  }, [status, pathname, router]);

  // If we are on the login page, just render children (no auth check needed)
  if (pathname === '/login') {
    return <>{children}</>;
  }

  if (status === 'loading' || status === 'idle') {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Spinner />
      </div>
    );
  }

  // Authenticated and not on login page – render protected UI
  return <>{children}</>;
}
