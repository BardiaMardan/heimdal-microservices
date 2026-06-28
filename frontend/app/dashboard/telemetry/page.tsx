import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TelemetryPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Telemetry
        </h1>
        <p className="mt-2 text-sm sm:text-base text-white/80">
          Live device readings, once MQTT ingestion is wired up.
        </p>
      </div>

      <Card className="min-h-[400px]">
        <CardHeader>
          <CardTitle>Streams</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-full min-h-[300px] items-center justify-center">
            <div className="text-center">
              <p className="text-lg font-medium text-white">No telemetry yet</p>
              <p className="mt-2 max-w-sm text-sm text-white/60">
                Claimed devices will stream readings here once the MQTT data
                plane lands.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
