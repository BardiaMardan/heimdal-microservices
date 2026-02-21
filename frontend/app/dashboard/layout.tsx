import { logout } from "@/actions/auth";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-black">
      <header className="sticky top-0 z-50 w-full border-b border-white bg-black">
        <div className="container flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="text-xl font-bold tracking-tight text-white"
            >
              HEIMDALL
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-white">
              user@example.com
            </span>
            <form action={logout}>
              <Button type="submit" variant="outline" size="sm">
                Logout
              </Button>
            </form>
          </div>
        </div>
      </header>
      <main className="container py-8 px-4 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
