import { create } from 'zustand';

/**
 * Global UI State Store
 * 
 * Convention:
 * - Use Zustand ONLY for global UI state (e.g. active project, sidebar toggle, global modals).
 * - Do NOT use Zustand for server state (use API clients / React Query).
 * - Do NOT use Zustand for local ephemeral state (use React `useState`).
 */

interface UIState {
  activeProjectId: string | null;
  isSidebarOpen: boolean;
  
  // Actions
  setActiveProject: (id: string | null) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  activeProjectId: null,
  isSidebarOpen: false,

  setActiveProject: (id) => set({ activeProjectId: id }),
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),
}));
