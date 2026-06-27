import { AppLayout } from "@/components/layout/app-layout";
import { fetchApi } from "@/lib/api";
import { User } from "@/lib/definitions";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await fetchApi<User>("/auth/me");

  return <AppLayout userEmail={user.email}>{children}</AppLayout>;
}
