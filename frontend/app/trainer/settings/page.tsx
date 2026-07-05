import { AccentPicker } from "@/components/trainer/accent-picker";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TrainerSettingsPage() {
  return (
    <div className="mx-auto flex max-w-[980px] flex-col gap-6 px-5 py-8 md:px-10">
      <Card>
        <CardHeader>
          <CardTitle>포인트 컬러</CardTitle>
          <p className="mt-2 text-base text-slate-500">
            선택한 컬러가 버튼·탭·아이콘 등 앱 전체에 즉시 반영됩니다.
          </p>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <AccentPicker />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <p className="mb-6 text-sm font-semibold text-slate-400">미리보기</p>
          <div className="flex flex-wrap items-center gap-5">
            <span className="accent-gradient rounded-xl px-7 py-4 font-heading text-lg font-black text-black">
              오늘 세션 시작 →
            </span>
            <span className="flex items-center gap-4 font-ui text-xl font-black text-slate-700">
              <span className="h-3 w-3 rounded-full bg-[var(--acc)]" />
              진행 중
            </span>
            <span className="font-display text-4xl leading-none text-[var(--acc)]">72</span>
            <span className="font-mono text-slate-400">SCORE</span>
            <span className="rounded-xl bg-slate-100 p-1.5">
              <span className="accent-gradient inline-block rounded-lg px-5 py-2 font-ui font-black text-black">대시보드</span>
              <span className="inline-block px-5 py-2 font-ui font-black text-slate-400">리포트</span>
            </span>
          </div>
        </CardContent>
      </Card>

      <div className="rounded-2xl bg-white/55 p-5 text-sm leading-6 text-slate-500">
        실제 서비스에서는 선택값을 사용자 설정(user.theme.accent)에 저장하고, 루트의 --acc 토큰 하나로 전체 UI에
        적용됩니다. 그라데이션 선은 이 색에서 자동 파생됩니다.
      </div>
    </div>
  );
}
