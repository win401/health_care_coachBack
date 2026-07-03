import { serverGet } from "@/lib/server-api";
import type { MemberSummary } from "@/lib/types";
import { SessionWorkspaceClient } from "@/components/trainer/session-workspace-client";

export default async function SessionWorkspacePage({
  params,
}: {
  params: Promise<{ memberId: string }>;
}) {
  const { memberId } = await params;
  const summary = await serverGet<MemberSummary>(`/members/${memberId}`);

  if (!summary) {
    return <div className="p-8 text-sm text-slate-500">회원을 찾을 수 없습니다.</div>;
  }

  return <SessionWorkspaceClient member={summary.member} />;
}
