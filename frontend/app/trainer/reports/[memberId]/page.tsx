import { serverGet } from "@/lib/server-api";
import type { MemberSummary, Report } from "@/lib/types";
import { ReportClient } from "@/components/trainer/report-client";

export default async function MemberReportPage({
  params,
}: {
  params: Promise<{ memberId: string }>;
}) {
  const { memberId } = await params;
  const summary = await serverGet<MemberSummary>(`/members/${memberId}`);
  if (!summary) {
    return <div className="p-8 text-sm text-slate-500">회원을 찾을 수 없습니다.</div>;
  }
  const reports = (await serverGet<Report[]>(`/members/${memberId}/reports`)) || [];

  return <ReportClient member={summary.member} reports={reports} />;
}
