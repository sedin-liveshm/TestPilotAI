"use client";
import { useRouter } from 'next/navigation';
import { Menu, UserCircle, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/auth-store';
import { Sidebar } from './Sidebar';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const router = useRouter();
  const { logout, user, status } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    router.replace('/login');
  };

  return (
    <div className="grid min-h-screen w-full md:grid-cols-[256px_1fr]">
      <Sidebar />
      <div className="flex flex-col">
        <header className="flex h-14 items-center gap-4 border-b bg-background px-4 lg:h-[60px] lg:px-6">
          <Button variant="outline" size="icon" className="shrink-0 ">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
          <div className="w-full flex-1" />
          {status === 'authenticated' && (
            <Button variant="ghost" size="icon" onClick={handleLogout} className="rounded-full" aria-label="Logout">
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
