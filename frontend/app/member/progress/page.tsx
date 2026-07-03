import { serverGet } from "@/lib/server-api";
import type { PostureHistoryPoint } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function MemberProgressPage() {
  const history = (await serverGet<PostureHistoryPoint[]>("/my/posture-history")) || [];

  return (
    <div className="flex flex-col gap-4 p-4">
      <h1 className="text-xl font-bold text-slate-900">변화 기록</h1>

      <Card>
        <CardHeader>
          <CardTitle>자세 점수 변화</CardTitle>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <p className="text-sm text-slate-400">아직 자세 분석 기록이 없습니다</p>
          ) : (
            <div className="flex items-end gap-2 h-32">
              {history.map((h, i) => (
                <div key={i} className="flex flex-1 flex-col items-center gap-1">
                  <div
                    className="w-full rounded-t bg-slate-800"
                    style={{ height: `${Math.max(4, ((h.total_score || 0) / 100) * 100)}%` }}
                  />
                  <span className="text-[10px] text-slate-400">{h.total_score ?? "-"}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>전체 히스토리</CardTitle>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <p className="text-sm text-slate-400">기록 없음</p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-xs text-slate-400">
                  <th className="pb-2 font-medium">일시</th>
                  <th className="pb-2 font-medium">점수</th>
                  <th className="pb-2 font-medium">주요 문제</th>
                </tr>
              </thead>
              <tbody>
                {history
                  .slice()
                  .reverse()
                  .map((h, i) => (
                    <tr key={i} className="border-t border-slate-100">
                      <td className="py-1.5 text-xs text-slate-500">{h.analyzed_at}</td>
                      <td className="py-1.5 font-medium text-slate-800">{h.total_score ?? "-"}</td>
                      <td className="py-1.5 text-xs text-slate-500">{h.main_issue || "-"}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
