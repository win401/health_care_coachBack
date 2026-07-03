import { serverGet } from "@/lib/server-api";
import type { Member } from "@/lib/types";
import { MembersListClient } from "@/components/trainer/members-list-client";

export default async function MembersPage() {
  const members = (await serverGet<Member[]>("/members")) || [];
  return <MembersListClient members={members} />;
}
