import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function LogsPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Logs
        </h1>
        <p className="mt-2 text-sm sm:text-base text-white/80">
          System and device events.
        </p>
      </div>

      <Card className="min-h-[400px]">
        <CardHeader>
          <CardTitle>Event log</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-full min-h-[300px] items-center justify-center">
            <div className="text-center">
              <p className="text-lg font-medium text-white">No events yet</p>
              <p className="mt-2 max-w-sm text-sm text-white/60">
                Device lifecycle and system events will be recorded here.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
