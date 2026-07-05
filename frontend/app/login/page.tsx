"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Role = "trainer" | "member";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next");

  const [role, setRole] = useState<Role>("trainer");
  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [phoneLast4, setPhoneLast4] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (role === "trainer") {
        await api.post("/auth/trainer/login", { login_id: loginId, password });
        router.replace(nextPath && nextPath.startsWith("/trainer") ? nextPath : "/trainer/dashboard");
      } else {
        if (!/^\d{4}$/.test(phoneLast4)) {
          setError("전화번호 뒷자리 4자리 숫자를 입력해주세요");
          setLoading(false);
          return;
        }
        await api.post("/auth/member/login", { name, phone_last4: phoneLast4 });
        router.replace(nextPath && nextPath.startsWith("/member") ? nextPath : "/member");
      }
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("로그인 중 오류가 발생했습니다");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen w-full bg-background lg:grid-cols-[1.05fr_0.95fr]">
      <section className="relative hidden min-h-screen overflow-hidden bg-black p-16 text-white lg:flex lg:flex-col lg:justify-between">
        <div>
          <div className="flex items-center gap-5">
            <div className="flex h-12 w-12 items-center justify-center accent-gradient font-ui text-xl font-black text-black">
              F
            </div>
            <p className="font-heading text-3xl font-black uppercase">FITNOTE</p>
          </div>
        </div>
        <div>
          <p className="mb-8 flex items-center gap-4 font-mono text-xl font-bold uppercase tracking-[0.28em] text-[var(--acc)]">
            <span className="h-1 w-12 accent-gradient" />
            Trainer OS
          </p>
          <h1 className="max-w-3xl font-heading text-[72px] font-black leading-[1.05] tracking-tight">
            기억이 아닌
            <br />
            <span className="text-[var(--acc)]">기록</span>으로
          </h1>
          <p className="mt-8 max-w-2xl text-xl leading-8 text-white/62">
            수업 기록 · 자세 분석 · 피드백 · 과제를 한 흐름으로. 트레이너의 모든 순간을 데이터로.
          </p>
        </div>
        <div className="flex gap-12">
          {[
            ["124", "누적 세션"],
            ["18", "담당 회원"],
            ["92%", "완료율"],
          ].map(([value, label]) => (
            <div key={label}>
              <p className="font-display text-4xl leading-none">{value}</p>
              <p className="mt-3 text-sm text-white/45">{label}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="flex min-h-screen items-center justify-center px-6 py-8">
        <div className="w-full max-w-[520px]">
          <div className="mb-10">
            <p className="mono-label text-slate-400">Welcome Back</p>
            <h2 className="mt-2 font-heading text-4xl font-black leading-none text-slate-950">로그인</h2>
            <p className="mt-4 text-base text-slate-500">데모 계정으로 바로 둘러보세요.</p>
          </div>

          <div className="mb-7 grid rounded-2xl bg-slate-200/70 p-1.5">
            <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setRole("trainer")}
              className={`h-12 rounded-xl font-ui text-base font-black transition-colors ${
                role === "trainer"
                  ? "bg-white text-slate-950 shadow-sm"
                  : "text-slate-400 hover:text-slate-600"
              }`}
            >
              트레이너
            </button>
            <button
              type="button"
              onClick={() => setRole("member")}
              className={`h-12 rounded-xl font-ui text-base font-black transition-colors ${
                role === "member"
                  ? "bg-white text-slate-950 shadow-sm"
                  : "text-slate-400 hover:text-slate-600"
              }`}
            >
              회원
            </button>
            </div>
          </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
              {role === "trainer" ? (
                <>
                  <div className="flex flex-col gap-3">
                    <label className="text-sm font-semibold text-slate-400">아이디</label>
                    <Input
                      value={loginId}
                      onChange={(e) => setLoginId(e.target.value)}
                      placeholder="트레이너 아이디"
                      autoComplete="username"
                      required
                    />
                  </div>
                  <div className="flex flex-col gap-3">
                    <label className="text-sm font-semibold text-slate-400">비밀번호</label>
                    <Input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="비밀번호"
                      autoComplete="current-password"
                      required
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="flex flex-col gap-3">
                    <label className="text-sm font-semibold text-slate-400">이름</label>
                    <Input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="회원 이름"
                      required
                    />
                  </div>
                  <div className="flex flex-col gap-3">
                    <label className="text-sm font-semibold text-slate-400">전화번호 뒷자리 4자리</label>
                    <Input
                      value={phoneLast4}
                      onChange={(e) => setPhoneLast4(e.target.value.replace(/[^0-9]/g, "").slice(0, 4))}
                      placeholder="0000"
                      inputMode="numeric"
                      maxLength={4}
                      required
                    />
                  </div>
                </>
              )}

              {error && <p className="text-sm text-red-600">{error}</p>}

              <Button type="submit" variant="accent" size="lg" disabled={loading} className="mt-3 h-14 w-full rounded-xl text-base">
                {loading ? "로그인 중..." : "로그인 →"}
              </Button>
              <p className="text-center font-mono text-base text-slate-300">demo · trainer1 / pass1234</p>
            </form>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}
