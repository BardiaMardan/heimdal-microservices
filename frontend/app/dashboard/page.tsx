import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Dashboard
        </h1>
        <p className="mt-2 text-white">
          Welcome to Heimdall. Your AI-powered home automation orchestrator.
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="col-span-full">
          <Card className="min-h-[400px]">
            <CardHeader>
              <CardTitle>Agent Chat</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center h-full min-h-[300px]">
                <div className="text-center">
                  <p className="text-lg font-medium text-white">Agent Chat</p>
                  <p className="text-sm text-white mt-2">
                    TODO: Agent chat interface will be implemented here.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
