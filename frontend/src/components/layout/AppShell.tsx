import { Sidebar } from "./Sidebar";
import { Menu, UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="grid min-h-screen w-full md:grid-cols-[256px_1fr]">
      <Sidebar />
      <div className="flex flex-col">
        <header className="flex h-14 items-center gap-4 border-b bg-background px-4 lg:h-[60px] lg:px-6">
          <Button variant="outline" size="icon" className="shrink-0 md:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
          <div className="w-full flex-1">
            {/* Search or breadcrumbs could go here */}
          </div>
          <Button variant="ghost" size="icon" className="rounded-full">
            <UserCircle className="h-6 w-6 text-muted-foreground" />
            <span className="sr-only">Toggle user menu</span>
          </Button>
        </header>
        <main className="flex-1 p-4 lg:p-6 bg-muted/20">
          {children}
        </main>
      </div>
    </div>
  );
}
