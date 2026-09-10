"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  FolderGit2, 
  TestTube2, 
  Wand2, 
  PlayCircle, 
  BarChart3, 
  ShieldCheck, 
  Settings 
} from "lucide-react";
import { cn } from "@/lib/utils";

export const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Projects", href: "/projects", icon: FolderGit2 },
  { name: "Tests", href: "/tests", icon: TestTube2 },
  { name: "Test Builder", href: "/builder", icon: Wand2 },
  { name: "Runs", href: "/runs", icon: PlayCircle },
  { name: "Reports", href: "/reports", icon: BarChart3 },
  { name: "Coverage", href: "/coverage", icon: ShieldCheck },
  { name: "Settings", href: "/settings", icon: Settings },
];

interface SidebarProps {
  className?: string;
  onNavigate?: () => void;
}

export function Sidebar({ className, onNavigate }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className={cn("w-64 flex-col border-r bg-card", className)}>
      <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
        <Link
          href="/"
          onClick={onNavigate}
          className="flex items-center gap-2 font-heading font-semibold text-xl"
        >
          <Wand2 className="h-6 w-6 text-primary" />
          <span className="text-primary">PilotAI</span>
        </Link>
      </div>
      <div className="flex-1 overflow-auto py-2">
        <nav className="grid items-start px-2 text-sm font-medium lg:px-4 gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onNavigate}
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
    </aside>
  );
}

