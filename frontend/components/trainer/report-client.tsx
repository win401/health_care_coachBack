"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Member, Report } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function ReportClient({ member, reports }: { member: Member; reports: Report[] }) {
  const [list, setList] = useState(reports);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setError(null);
    setGenerating(true);
    try {
      const created = await api.post<Report>("/reports", { member_id: member.id });
      setList((prev) => [created, ...prev]);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "리포트 생성 중 오류가 발생했습니다");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-4 md:p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900">{member.name} 회원 리포트</h1>
        <Button onClick={handleGenerate} disabled={generating}>
          {generating ? "생성 중..." : "리포트 생성"}
        </Button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}

      {list.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-slate-400">
            아직 생성된 리포트가 없습니다. 최근 세션/자세분석/과제 데이터를 기반으로 생성해보세요.
          </CardContent>
        </Card>
      ) : (
        list.map((r) => (
          <Card key={r.id}>
            <CardHeader>
              <CardTitle>{r.report_title}</CardTitle>
              <p className="text-xs text-slate-400">{r.created_at}</p>
            </CardHeader>
            <CardContent className="flex flex-col gap-2 text-sm text-slate-700">
              <ReportRow label="오늘의 운동 요약" value={r.workout_summary} />
              <ReportRow label="자세 분석 결과" value={r.posture_summary} />
              <ReportRow label="잘한 점" value={r.good_points} />
              <ReportRow label="주의할 점" value={r.caution_points} />
              <ReportRow label="다음 과제" value={r.next_assignment} />
              <p className="mt-2 text-xs text-slate-400">
                이 리포트는 의료 진단이 아니라 운동 자세 참고 자료입니다. 최종 피드백은 트레이너 판단을
                기반으로 합니다.
              </p>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}

function ReportRow({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <p className="text-xs font-medium text-slate-400">{label}</p>
      <p>{value || "-"}</p>
    </div>
  );
}
