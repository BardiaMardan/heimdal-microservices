"use client";

import { Header } from "./header";
import { Sidebar } from "./sidebar";
import { MainContent } from "./main-content";
import { RightPanel } from "./right-panel";
import { useState } from "react";

export function AppLayout({
  children,
  rightPanel,
}: {
  children: React.ReactNode;
  rightPanel?: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-black">
      <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex pt-16">
        <div className="hidden lg:block">
          <Sidebar isOpen={true} />
        </div>
        <div className="lg:hidden">
          <Sidebar
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
          />
        </div>
        <div className="flex-1 lg:ml-60">
          <MainContent>{children}</MainContent>
        </div>
        {rightPanel && (
          <div className="hidden xl:block w-[280px]">
            <RightPanel>{rightPanel}</RightPanel>
          </div>
        )}
      </div>
    </div>
  );
}
