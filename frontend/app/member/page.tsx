import { serverGet } from "@/lib/server-api";
import type { MemberSummary } from "@/lib/types";

export default async function MemberHomePage() {
  const summary = await serverGet<MemberSummary>("/my/profile");

  if (!summary) {
    return <div className="p-4 text-sm text-slate-500">회원 정보를 불러오지 못했습니다.</div>;
  }

  return (
    <div className="min-h-screen overflow-hidden rounded-3xl bg-black text-white md:mt-4">
      <section className="px-6 pb-8 pt-9">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center accent-gradient font-ui text-xl font-black text-black">
              F
            </div>
            <p className="font-heading text-2xl font-black">FITNOTE</p>
          </div>
          <p className="font-mono text-lg text-white/62">MY PT</p>
        </div>
        <p className="mt-9 font-mono text-sm font-bold uppercase tracking-[0.22em] text-[var(--acc)]">Welcome</p>
        <h1 className="mt-2 font-heading text-3xl font-black leading-tight">{summary.member.name} 회원님</h1>
        <div className="mt-7 grid grid-cols-3 gap-3">
          <MemberMetric label="남은 세션" value="8" suffix="회" />
          <MemberMetric label="자세 점수" value={`${summary.last_posture_score ?? 72}`} />
          <MemberMetric label="출석률" value="86" suffix="%" />
        </div>
      </section>

      <section className="flex flex-col gap-5 bg-background px-6 py-7 text-slate-950">
        <div className="rounded-2xl bg-white p-5">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="font-heading text-2xl font-black">오늘의 과제</h2>
            <p className="text-sm font-bold text-[var(--good)]">1 / 3 완료</p>
          </div>
          <div className="space-y-5">
            <AssignmentRow title="벽 스쿼트" meta="20회 × 3세트 · 마감 7/5" />
            <AssignmentRow title="고관절 스트레칭" meta="10분 · 마감 매일" done />
            <AssignmentRow title="데드버그" meta="12회 × 2세트 · 마감 7/4" />
          </div>
        </div>

        <div className="rounded-2xl bg-white p-5">
          <h2 className="font-heading text-2xl font-black">자세 점수 변화</h2>
          <p className="mt-2 text-sm text-slate-400">최근 4회 · +14점 개선</p>
          <div className="mt-7 grid grid-cols-4 items-end gap-4">
            {[58, 65, 68, summary.last_posture_score ?? 72].map((score, index) => (
              <div key={index} className="text-center">
                <p className="font-heading text-xl font-black">{score}</p>
                <div className="mt-8 rounded-t-xl accent-gradient" style={{ height: `${score * 1.5}px` }} />
                <p className="mt-5 font-mono text-sm text-slate-400">{["5/20", "6/03", "6/17", "7/01"][index]}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl bg-white p-5">
          <h2 className="font-heading text-2xl font-black">다음 PT 예약</h2>
          <p className="mt-3 text-base text-slate-600">
            {summary.last_session_date ? `${summary.last_session_date} 이후 다음 예약 확인` : "예약된 수업을 확인해보세요."}
          </p>
        </div>
      </section>
    </div>
  );
}

function MemberMetric({ label, value, suffix = "" }: { label: string; value: string; suffix?: string }) {
  return (
    <div className="rounded-2xl bg-white/9 p-4">
      <p className="text-xs text-white/62">{label}</p>
      <p className="mt-2 font-display text-3xl leading-none text-white">
        {value}<span className="font-sans text-lg text-white/62">{suffix}</span>
      </p>
    </div>
  );
}

function AssignmentRow({ title, meta, done = false }: { title: string; meta: string; done?: boolean }) {
  return (
    <div className="flex items-center gap-5">
      <span className={`flex h-10 w-10 items-center justify-center rounded-lg border-[3px] ${
        done ? "border-[var(--good)] bg-[var(--good)] text-white" : "border-slate-300 text-transparent"
      }`}>
        ✓
      </span>
      <div>
        <p className={`font-heading text-xl font-black ${done ? "text-slate-400 line-through" : "text-slate-950"}`}>{title}</p>
        <p className="mt-1 text-sm text-slate-400">{meta}</p>
      </div>
    </div>
  );
}
