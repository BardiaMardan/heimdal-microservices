import { logout } from "@/actions/auth";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="sticky top-0 z-50 w-full border-b border-zinc-200 bg-white shadow-sm">
        <div className="container flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="text-xl font-bold tracking-tight text-zinc-900"
            >
              Heimdall
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <form action={logout}>
              <button
                type="submit"
                className="text-sm font-medium text-zinc-600 hover:text-zinc-900 transition-colors"
              >
                Sign out
              </button>
            </form>
          </div>
        </div>
      </header>
      <main className="container py-8 px-4 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
