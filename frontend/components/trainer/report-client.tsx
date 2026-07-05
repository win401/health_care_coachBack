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
    <div className="mx-auto flex max-w-[1500px] flex-col gap-6 px-5 py-6 md:px-10">
      <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <p className="mb-2 text-sm font-semibold text-slate-400">회원</p>
            <div className="flex h-14 min-w-44 items-center rounded-xl border border-slate-200 bg-white px-5 font-heading text-xl font-black">
              {member.name}
            </div>
          </div>
          <div>
            <p className="mb-2 text-sm font-semibold text-slate-400">세션</p>
            <div className="flex h-14 min-w-56 items-center rounded-xl border border-slate-200 bg-white px-5 font-heading text-xl font-black">
              2026-07-03 · 하체
            </div>
          </div>
        </div>
        <Button variant="accent" onClick={handleGenerate} disabled={generating} className="h-14 rounded-xl px-7 text-base">
          {generating ? "생성 중..." : "리포트 생성"}
        </Button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}

      {list.length === 0 ? (
        <Card className="border-dashed border-slate-300 bg-transparent shadow-none">
          <CardContent className="flex min-h-[260px] flex-col items-center justify-center py-14 text-center">
            <p className="font-heading text-2xl font-black text-slate-950">리포트를 생성하세요</p>
            <p className="mt-4 text-base text-slate-400">
              세션 기록·자세 분석·피드백·과제를 모아 회원용 리포트를 만듭니다.
            </p>
          </CardContent>
        </Card>
      ) : (
        list.map((r) => (
          <Card key={r.id} className="overflow-hidden">
            <CardHeader className="border-b border-slate-200 bg-[#f7f8f4]">
              <p className="mono-label text-slate-400">{r.created_at}</p>
              <CardTitle className="mt-2 text-2xl">{r.report_title}</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 text-sm text-slate-700 md:grid-cols-2">
              <ReportRow label="오늘의 운동 요약" value={r.workout_summary} />
              <ReportRow label="자세 분석 결과" value={r.posture_summary} />
              <ReportRow label="잘한 점" value={r.good_points} />
              <ReportRow label="주의할 점" value={r.caution_points} />
              <ReportRow label="다음 과제" value={r.next_assignment} />
              <p className="rounded-2xl border border-slate-200 bg-white p-4 text-xs leading-5 text-slate-400 md:col-span-2">
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
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <p className="mono-label text-slate-400">{label}</p>
      <p className="mt-2 leading-6 text-slate-800">{value || "-"}</p>
    </div>
  );
}
