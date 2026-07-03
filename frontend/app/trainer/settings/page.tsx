import { AccentPicker } from "@/components/trainer/accent-picker";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TrainerSettingsPage() {
  return (
    <div className="flex flex-col gap-4 p-4 md:p-6">
      <div>
        <p className="mono-label text-xs text-slate-500">Preference</p>
        <h1 className="mt-1 font-heading text-2xl font-extrabold text-slate-900">설정</h1>
        <p className="mt-1 text-sm text-slate-500">트레이너 화면의 포인트 컬러를 선택하세요.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>포인트 컬러</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <AccentPicker />
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="mono-label text-[11px] text-slate-500">Preview</p>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <span className="accent-gradient rounded-full px-4 py-2 font-ui text-sm font-bold text-white">
                세션 시작
              </span>
              <span className="rounded-full border border-mint px-4 py-2 font-ui text-sm font-bold text-mint">
                리포트 생성
              </span>
              <span className="h-3 w-32 rounded-full bg-slate-200">
                <span className="block h-3 w-20 rounded-full accent-gradient" />
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
