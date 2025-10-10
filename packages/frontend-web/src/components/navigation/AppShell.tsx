/**
 * AppShell - Moderne ERP-Navigation
 * Kein Ribbon - Hybrid-Ansatz mit:
 * - Sidebar (Domänen)
 * - Top-Header (Suche, User)
 * - Kontextuelle Page-Toolbar
 * - Command Palette (Ctrl+K)
 * 
 * MCP-Ready: Alle Actions mit Metadaten für Phase 3
 */

import { ReactNode, useState } from 'react';
import { CommandPalette } from './CommandPalette';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata';

interface AppShellProps {
  children: ReactNode;
}

// MCP-Metadaten für AppShell (Phase 3 Vorbereitung)
export const appShellMCP = createMCPMetadata('AppShell', 'navigation', {
  accessibility: {
    role: 'application',
    ariaLabel: 'VALEO NeuroERP Main Application',
    focusable: false,
    keyboardShortcuts: ['Ctrl+K', 'Ctrl+B', '/'],
  },
  intent: {
    purpose: 'Main application navigation and layout',
    userActions: ['navigate', 'search', 'command'],
    businessDomain: 'core',
  },
  mcpHints: {
    autoFillable: false,
    explainable: true,
    testable: true,
    contextAware: true,
  },
});

export function AppShell({ children }: AppShellProps) {
  const [commandOpen, setCommandOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Command Palette mit Ctrl/Cmd+K
  useState(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCommandOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  });

  return (
    <div 
      className="flex h-screen overflow-hidden bg-background"
      data-mcp-component="app-shell"
      data-mcp-version="1.0.0"
    >
      {/* Sidebar - Domänen-Navigation */}
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top-Bar - Suche, Ask VALEO, User */}
        <TopBar onCommandOpen={() => setCommandOpen(true)} />

        {/* Page Content (mit PageHeader + Toolbar) */}
        <main 
          className="flex-1 overflow-y-auto overflow-x-hidden"
          role="main"
          aria-label="Main content"
        >
          {children}
        </main>
      </div>

      {/* Command Palette - Ctrl/Cmd+K */}
      <CommandPalette 
        open={commandOpen}
        onOpenChange={setCommandOpen}
      />
    </div>
  );
}

