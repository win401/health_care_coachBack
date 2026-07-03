import { serverGet } from "@/lib/server-api";
import type { Member } from "@/lib/types";
import { DashboardClient } from "@/components/trainer/dashboard-client";

export default async function TrainerDashboardPage() {
  const members = (await serverGet<Member[]>("/members")) || [];

  return <DashboardClient members={members} />;
}
