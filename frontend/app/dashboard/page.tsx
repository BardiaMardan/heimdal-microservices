export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
          Dashboard
        </h1>
        <p className="mt-2 text-zinc-600">
          Welcome to Heimdall. Your AI-powered home automation orchestrator.
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {/* Placeholder for Agent Chat */}
        <div className="col-span-full rounded-lg border border-zinc-200 bg-white p-6 shadow-sm min-h-[400px] flex items-center justify-center">
          <div className="text-center">
            <p className="text-lg font-medium text-zinc-900">Agent Chat</p>
            <p className="text-sm text-zinc-500">
              Todo : Agent chat interface will be implemented here.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
