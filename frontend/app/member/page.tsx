import { serverGet } from "@/lib/server-api";
import type { MemberSummary } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function MemberHomePage() {
  const summary = await serverGet<MemberSummary>("/my/profile");

  if (!summary) {
    return <div className="p-4 text-sm text-slate-500">회원 정보를 불러오지 못했습니다.</div>;
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <div>
        <h1 className="text-xl font-bold text-slate-900">안녕하세요, {summary.member.name}님</h1>
        <p className="text-sm text-slate-500">오늘도 좋은 운동 되세요.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>내 프로필</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3">
          <InfoRow label="운동 목표" value={summary.member.fitness_goal || "-"} />
          <InfoRow label="통증/주의사항" value={summary.precautions || summary.pain_area || "없음"} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>최근 수업</CardTitle>
        </CardHeader>
        <CardContent>
          {summary.last_session_date ? (
            <p className="text-sm text-slate-700">
              {summary.last_session_date} · {summary.last_session_focus}
            </p>
          ) : (
            <p className="text-sm text-slate-400">아직 수업 기록이 없습니다</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>최근 자세 분석</CardTitle>
        </CardHeader>
        <CardContent>
          {summary.last_posture_score != null ? (
            <p className="text-sm text-slate-700">
              자세 점수 {summary.last_posture_score}점 · {summary.last_posture_main_issue}
            </p>
          ) : (
            <p className="text-sm text-slate-400">아직 자세 분석 기록이 없습니다</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>진행 중 과제</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-700">{summary.open_assignment_count}건 진행 중</p>
        </CardContent>
      </Card>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-slate-400">{label}</p>
      <p className="text-sm font-medium text-slate-800">{value}</p>
    </div>
  );
}
