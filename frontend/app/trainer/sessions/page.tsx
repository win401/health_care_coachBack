import Link from "next/link";
import { serverGet } from "@/lib/server-api";
import type { Member, Session } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type MemberWithLastSession = Member & { sessions: Session[] };

export default async function SessionsListPage() {
  const members = (await serverGet<Member[]>("/members")) || [];

  const withSessions: MemberWithLastSession[] = await Promise.all(
    members.map(async (m) => ({
      ...m,
      sessions: (await serverGet<Session[]>(`/members/${m.id}/sessions?limit=1`)) || [],
    }))
  );

  return (
    <div className="flex flex-col gap-4 p-4 md:p-6">
      <h1 className="text-xl font-bold text-slate-900">세션 기록</h1>
      <p className="text-sm text-slate-500">회원을 선택해 수업 기록 · 자세 분석 · 과제를 작성하세요.</p>

      {withSessions.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-slate-400">
            등록된 회원이 없습니다
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {withSessions.map((m) => (
            <Card key={m.id}>
              <CardContent className="flex flex-col gap-2 py-4">
                <p className="text-base font-semibold text-slate-900">{m.name}</p>
                <p className="text-xs text-slate-400">
                  {m.sessions[0]
                    ? `최근 수업: ${m.sessions[0].session_date} · ${m.sessions[0].focus_area || ""}`
                    : "수업 기록 없음"}
                </p>
                <Link href={`/trainer/sessions/${m.id}`}>
                  <Button size="sm" className="mt-2 w-full">
                    세션 기록 열기
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
