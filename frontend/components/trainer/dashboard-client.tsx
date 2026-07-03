"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Member, MemberSummary } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { DailySchedule } from "@/components/trainer/daily-schedule";

export function DashboardClient({ members }: { members: Member[] }) {
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(members[0]?.id ?? null);
  const [summary, setSummary] = useState<MemberSummary | null>(null);
  const [loading, setLoading] = useState(false);

  const filtered = useMemo(
    () => members.filter((m) => m.name.includes(query.trim())),
    [members, query]
  );

  useEffect(() => {
    if (!selectedId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSummary(null);
      return;
    }
    setLoading(true);
    api
      .get<MemberSummary>(`/members/${selectedId}`)
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, [selectedId]);

  return (
    <div className="flex flex-col gap-4 p-4 md:p-6">
      <DailySchedule />

      <div className="grid gap-4 md:grid-cols-[280px_1fr]">
      {/* 회원 검색/선택 */}
      <Card className="h-fit">
        <CardHeader>
          <CardTitle>회원 검색</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="이름으로 검색"
          />
          <div className="flex max-h-80 flex-col gap-1 overflow-y-auto">
            {filtered.length === 0 && (
              <p className="py-4 text-center text-sm text-slate-400">검색 결과가 없습니다</p>
            )}
            {filtered.map((m) => (
              <button
                key={m.id}
                onClick={() => setSelectedId(m.id)}
                className={`rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                  selectedId === m.id
                    ? "bg-slate-900 text-white"
                    : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                {m.name}
                <span className="ml-2 text-xs opacity-60">{m.fitness_goal}</span>
              </button>
            ))}
          </div>
          <Link href="/trainer/members/new">
            <Button variant="secondary" className="w-full">
              + 신규 회원 등록
            </Button>
          </Link>
        </CardContent>
      </Card>

      {/* 요약 영역 */}
      <div className="flex flex-col gap-4">
        {loading && <p className="text-sm text-slate-400">불러오는 중...</p>}

        {!loading && !summary && (
          <Card>
            <CardContent className="py-12 text-center text-sm text-slate-400">
              회원을 선택하면 요약 정보가 표시됩니다
            </CardContent>
          </Card>
        )}

        {summary && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>{summary.member.name} 회원 요약</CardTitle>
                <Link href={`/trainer/sessions/${summary.member.id}`}>
                  <Button size="sm">오늘 세션 시작</Button>
                </Link>
              </CardHeader>
              <CardContent className="grid gap-3 sm:grid-cols-2">
                <InfoRow label="운동 목표" value={summary.member.fitness_goal || "-"} />
                <InfoRow label="운동 경험" value={summary.member.exercise_experience || "-"} />
                <InfoRow label="통증 부위" value={summary.pain_area || "없음"} />
                <InfoRow label="주의사항" value={summary.precautions || "없음"} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>최근 수업 / 자세 분석</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3 sm:grid-cols-2">
                <InfoRow
                  label="최근 수업"
                  value={
                    summary.last_session_date
                      ? `${summary.last_session_date} · ${summary.last_session_focus || ""}`
                      : "기록 없음"
                  }
                />
                <InfoRow
                  label="최근 자세 점수"
                  value={
                    summary.last_posture_score != null
                      ? `${summary.last_posture_score}점 · ${summary.last_posture_main_issue || ""}`
                      : "분석 기록 없음"
                  }
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>진행 중 과제</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">
                  진행 중인 과제 {summary.open_assignment_count}건
                </p>
              </CardContent>
            </Card>

            {/* 미니 달력 등 상세 정보는 데스크탑에서만 노출 */}
            <Card className="hidden md:block">
              <CardHeader>
                <CardTitle>이번 달 메모</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-500">
                  회원별 세부 일정/메모 캘린더는 추후 확장 영역입니다.
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>
      </div>
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
