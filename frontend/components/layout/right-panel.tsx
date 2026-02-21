export function RightPanel({ children }: { children: React.ReactNode }) {
  return (
    <aside className="fixed right-0 top-16 bottom-0 z-40 w-[280px] border-l border-white/10 bg-black">
      <div className="p-6">
        {children}
      </div>
    </aside>
  );
}

