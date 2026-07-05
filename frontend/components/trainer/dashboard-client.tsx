"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Member, MemberSummary } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

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
    <div className="mx-auto flex max-w-[1500px] flex-col gap-6 px-5 py-6 md:px-10">
      <section className="dark-panel rounded-2xl px-6 py-6 text-white md:px-8">
        <div className="mb-5 flex items-center justify-between">
          <p className="font-ui text-sm font-bold text-[var(--acc)]">오늘 수업 <span className="ml-3 font-mono text-white/38">4 SESSIONS</span></p>
          <p className="font-mono text-sm text-white/45">JUL 03</p>
        </div>
        <div className="grid gap-5 md:grid-cols-4">
          {[
            { time: "09:00", name: "이민호", detail: "상체 · 근비대" },
            { time: "11:00", name: summary?.member.name ?? "박수진", detail: summary?.member.fitness_goal ?? "하체 · 자세교정", active: true },
            { time: "14:30", name: "최유나", detail: "전신 · 컨디셔닝" },
            { time: "18:00", name: "정하늘", detail: "코어 · 재활" },
          ].map((item) => (
            <div
              key={item.time}
              className={`rounded-2xl p-5 ${item.active ? "accent-gradient text-black" : "bg-white/8 text-white/72"}`}
            >
              <p className="font-mono text-base">{item.time}</p>
              <p className="mt-4 font-heading text-xl font-black">{item.name}</p>
              <p className="mt-1 text-sm opacity-70">{item.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <Card className="h-fit rounded-2xl">
          <CardContent className="flex flex-col gap-4 p-5">
            <p className="font-mono text-sm tracking-[0.2em] text-slate-400">회원 검색</p>
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="이름으로 검색"
            />
            <div className="flex max-h-[420px] flex-col gap-3 overflow-y-auto">
              {filtered.length === 0 && (
                <p className="py-6 text-center text-sm text-slate-400">검색 결과가 없습니다</p>
              )}
              {filtered.map((m, index) => (
                <button
                  key={m.id}
                  onClick={() => setSelectedId(m.id)}
                  className={`group flex items-center gap-3 rounded-xl border px-3 py-3 text-left transition-colors ${
                    selectedId === m.id
                      ? "border-transparent bg-slate-950 text-white"
                      : "border-slate-200 bg-white text-slate-700 hover:border-[var(--acc)]"
                  }`}
                >
                  <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl font-heading text-lg font-black ${
                    selectedId === m.id ? "accent-gradient text-black" : "bg-slate-100 text-slate-600"
                  }`}>
                    {m.name.slice(0, 1)}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-heading text-lg font-black">{m.name}</p>
                    <p className="mt-1 truncate text-xs opacity-55">{m.fitness_goal || "목표 미입력"}</p>
                  </div>
                  <span className="font-display text-xl text-[var(--acc)]">{index === 0 ? "72" : index === 1 ? "88" : "65"}</span>
                </button>
              ))}
            </div>
            <Link href="/trainer/members/new">
              <Button variant="secondary" className="h-12 w-full border-dashed text-sm">
                신규 회원 등록
              </Button>
            </Link>
          </CardContent>
        </Card>

        <div className="flex flex-col gap-6">
          {loading && (
            <Card>
              <CardContent className="py-14 text-center text-sm text-slate-400">
                회원 정보를 불러오는 중입니다.
              </CardContent>
            </Card>
          )}

          {!loading && !summary && (
            <Card>
              <CardContent className="py-14 text-center text-sm text-slate-400">
                회원을 선택하면 요약 정보가 표시됩니다.
              </CardContent>
            </Card>
          )}

          {summary && (
            <>
              <Card className="rounded-2xl p-0">
                <CardContent className="p-6">
                  <div className="flex flex-col justify-between gap-6 xl:flex-row xl:items-center">
                    <div className="flex items-center gap-6">
                      <ScoreRing score={summary.last_posture_score ?? 72} />
                      <div>
                        <div className="flex flex-wrap items-center gap-4">
                          <h2 className="font-heading text-3xl font-black text-slate-950">{summary.member.name}</h2>
                          <span className="rounded-full bg-red-50 px-4 py-2 text-sm font-bold text-red-500">
                            {summary.pain_area || "허리 통증"}
                          </span>
                        </div>
                        <p className="mt-2 text-base text-slate-500">{summary.member.fitness_goal || "체중 감량 · 자세 교정"} · 6개월</p>
                      </div>
                    </div>
                    <Link href={`/trainer/sessions/${summary.member.id}`}>
                      <Button variant="accent" className="h-14 min-w-52 rounded-xl text-base">오늘 세션 시작 →</Button>
                    </Link>
                  </div>
                  <div className="mt-6 grid gap-4 md:grid-cols-4">
                    <InfoTile label="통증 부위" value={summary.pain_area || "허리 통증"} />
                    <InfoTile label="주의사항" value={summary.precautions || "무릎 정렬 주의"} />
                    <InfoTile label="남은 세션" value="8회" />
                    <InfoTile label="출석률" value="86%" />
                  </div>
                </CardContent>
              </Card>

              <div className="grid gap-6 xl:grid-cols-2">
                <Card className="rounded-2xl">
                  <CardContent className="p-6">
                    <p className="font-mono text-sm tracking-[0.2em] text-slate-400">최근 수업</p>
                    <h3 className="mt-4 font-heading text-2xl font-black">
                      {summary.last_session_focus || "하체 · 스쿼트 3×12"}
                    </h3>
                    <p className="mt-2 font-mono text-sm text-slate-500">{summary.last_session_date || "2026-06-30"}</p>
                    <div className="my-4 h-px bg-slate-200" />
                    <p className="text-base leading-7 text-slate-600">
                      {summary.last_posture_main_issue || "스쿼트 시 무릎이 안쪽으로 모이는 경향. 다음 수업 자세 재확인 필요."}
                    </p>
                  </CardContent>
                </Card>
                <Card className="rounded-2xl">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <p className="font-mono text-sm tracking-[0.2em] text-slate-400">진행 중 과제</p>
                      <p className="font-heading text-2xl font-black">{summary.open_assignment_count || 2}건</p>
                    </div>
                    <div className="mt-6 space-y-4">
                      <TaskLine color="bg-[var(--warn)]" title="벽 스쿼트 20회" meta="7/5" />
                      <TaskLine color="bg-[var(--good)]" title="고관절 스트레칭 10분" meta="매일" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function ScoreRing({ score }: { score: number }) {
  return (
    <div
      className="grid h-28 w-28 shrink-0 place-items-center rounded-full"
      style={{ background: `conic-gradient(#101114 ${score * 3.6}deg, #eeeeeb 0deg)` }}
    >
      <div className="grid h-[88px] w-[88px] place-items-center rounded-full bg-white">
        <div className="text-center">
          <p className="font-display text-3xl leading-none text-slate-950">{score}</p>
          <p className="font-mono text-xs tracking-[0.18em] text-slate-400">SCORE</p>
        </div>
      </div>
    </div>
  );
}

function InfoTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-[#f7f8f4] p-4">
      <p className="font-mono text-xs tracking-[0.12em] text-slate-400">{label}</p>
      <p className="mt-2 font-heading text-xl font-black leading-6 text-slate-950">{value}</p>
    </div>
  );
}

function TaskLine({ color, title, meta }: { color: string; title: string; meta: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="flex items-center gap-4">
        <span className={`h-3.5 w-3.5 rounded-full ${color}`} />
        <span className="font-heading text-lg font-black text-slate-900">{title}</span>
      </div>
      <span className="font-mono text-lg text-slate-400">{meta}</span>
    </div>
  );
}
