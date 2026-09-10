"use client";

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { Menu, UserCircle, LogOut, X, Wand2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/auth-store';
import { useUIStore } from '@/store/ui-store';
import { Sidebar, navItems } from './Sidebar';
import { cn } from '@/lib/utils';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { logout, status } = useAuthStore();
  const {
    isSidebarOpen,
    isMobileSidebarOpen,
    toggleSidebar,
    toggleMobileSidebar,
    setMobileSidebarOpen,
  } = useUIStore();

  // Close mobile drawer whenever route changes
  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [pathname, setMobileSidebarOpen]);

  const handleToggle = () => {
    if (typeof window !== 'undefined' && window.innerWidth < 768) {
      toggleMobileSidebar();
    } else {
      toggleSidebar();
    }
  };

  const handleLogout = async () => {
    await logout();
    router.replace('/login');
  };

  return (
    <div
      className={cn(
        "min-h-screen w-full bg-background",
        isSidebarOpen ? "md:grid md:grid-cols-[256px_1fr]" : "flex flex-col"
      )}
    >
      {/* Mobile Navigation Drawer */}
      {isMobileSidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileSidebarOpen(false)}
            aria-hidden="true"
          />
          <div className="relative z-10 flex h-full w-72 max-w-[85vw] flex-col bg-card shadow-2xl">
            <div className="flex h-14 items-center justify-between border-b px-4 lg:h-[60px] lg:px-6">
              <Link
                href="/"
                onClick={() => setMobileSidebarOpen(false)}
                className="flex items-center gap-2 font-heading font-semibold text-xl"
              >
                <Wand2 className="h-6 w-6 text-primary" />
                <span className="text-primary">PilotAI</span>
              </Link>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setMobileSidebarOpen(false)}
                aria-label="Close navigation menu"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            <div className="flex-1 overflow-auto py-2">
              <nav className="grid items-start px-2 text-sm font-medium lg:px-4 gap-1">
                {navItems.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileSidebarOpen(false)}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2 transition-all",
                        isActive
                          ? "bg-muted text-primary font-medium"
                          : "text-muted-foreground hover:text-primary hover:bg-muted"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            </div>
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      {isSidebarOpen && <Sidebar className="hidden md:flex" />}

      <div className="flex flex-col min-w-0 flex-1">
        <header className="flex h-14 items-center gap-4 border-b bg-background px-4 lg:h-[60px] lg:px-6">
          <Button
            variant="outline"
            size="icon"
            onClick={handleToggle}
            className="shrink-0"
            title={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
            aria-label="Toggle navigation menu"
            aria-expanded={isSidebarOpen}
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
          <div className="w-full flex-1" />
          {status === 'authenticated' && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="rounded-full"
              aria-label="Logout"
            >
              <LogOut className="h-5 w-5 text-muted-foreground" />
            </Button>
          )}
          <Button variant="ghost" size="icon" className="rounded-full" aria-label="User menu">
            <UserCircle className="h-6 w-6 text-muted-foreground" />
          </Button>
        </header>
        <main className="flex-1 p-4 lg:p-6 bg-muted/20">{children}</main>
      </div>
    </div>
  );
}

