import { serverGet } from "@/lib/server-api";
import type { Session } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function MemberSchedulePage() {
  const sessions = (await serverGet<Session[]>("/my/sessions?limit=10")) || [];
  const latest = sessions[0];

  return (
    <div className="flex flex-col gap-4 p-4">
      <h1 className="text-xl font-bold text-slate-900">내 일정</h1>

      <Card>
        <CardHeader>
          <CardTitle>다음 수업 확인사항</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-700">
            {latest?.next_memo || "트레이너가 등록한 다음 수업 안내가 아직 없습니다"}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>지난 수업 기록</CardTitle>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <p className="text-sm text-slate-400">수업 기록이 없습니다</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {sessions.map((s) => (
                <li key={s.id} className="border-b border-slate-100 pb-2 last:border-0">
                  <p className="text-sm font-medium text-slate-800">
                    {s.session_date} · {s.focus_area}
                  </p>
                  {s.exercises.length > 0 && (
                    <p className="text-xs text-slate-500">
                      {s.exercises.map((e) => e.exercise_name).join(", ")}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
