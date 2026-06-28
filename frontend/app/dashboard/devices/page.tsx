import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { Device } from "@/lib/definitions";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function StatusPill({ status }: { status: Device["status"] }) {
  const label = status.toUpperCase();
  return (
    <span
      className={cn(
        "inline-flex items-center border px-2 py-0.5 text-xs font-medium uppercase tracking-wide",
        status === "active"
          ? "border-white/30 text-white"
          : "border-white/10 text-white/50",
      )}
    >
      {label}
    </span>
  );
}

function formatRelative(iso: string | null): string {
  if (!iso) return "Never";
  const then = new Date(iso).getTime();
  const diff = Date.now() - then;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default async function DevicesPage() {
  const devices = await fetchApi<Device[]>("/devices");

  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Devices
          </h1>
          <p className="mt-2 text-sm sm:text-base text-white/80">
            Industrial devices you have claimed.
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/devices/connect">Connect a device</Link>
        </Button>
      </div>

      {devices.length === 0 ? (
        <div className="flex min-h-[320px] flex-col items-center justify-center border border-white/10 bg-black p-8 text-center">
          <p className="text-lg font-medium text-white">No devices yet</p>
          <p className="mt-2 max-w-sm text-sm text-white/60">
            Power on a device and enter the 6-digit code it displays to claim it
            to your account.
          </p>
          <Button asChild className="mt-6">
            <Link href="/dashboard/devices/connect">Connect a device</Link>
          </Button>
        </div>
      ) : (
        <div className="border border-white/10 bg-black">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-white/50">
                <th className="px-4 py-3 font-medium uppercase tracking-wide">
                  Name
                </th>
                <th className="hidden px-4 py-3 font-medium uppercase tracking-wide sm:table-cell">
                  Type
                </th>
                <th className="hidden px-4 py-3 font-medium uppercase tracking-wide md:table-cell">
                  Location
                </th>
                <th className="px-4 py-3 font-medium uppercase tracking-wide">
                  Status
                </th>
                <th className="hidden px-4 py-3 font-medium uppercase tracking-wide lg:table-cell">
                  Last seen
                </th>
              </tr>
            </thead>
            <tbody>
              {devices.map((device) => (
                <tr
                  key={device.id}
                  className="border-b border-white/10 last:border-b-0 transition-colors hover:bg-white/5"
                >
                  <td className="px-4 py-3 font-medium text-white">
                    {device.name}
                    {device.hardware_id && (
                      <span className="mt-0.5 block font-mono text-xs text-white/40">
                        {device.hardware_id}
                      </span>
                    )}
                  </td>
                  <td className="hidden px-4 py-3 capitalize text-white/80 sm:table-cell">
                    {device.type}
                  </td>
                  <td className="hidden px-4 py-3 text-white/80 md:table-cell">
                    {device.location ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <StatusPill status={device.status} />
                  </td>
                  <td className="hidden px-4 py-3 text-white/60 lg:table-cell">
                    {formatRelative(device.last_seen_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
