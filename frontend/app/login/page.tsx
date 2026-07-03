"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

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
    <div className="grid min-h-screen w-full bg-background lg:grid-cols-[1.1fr_0.9fr]">
      <section className="dark-panel relative hidden min-h-screen overflow-hidden p-10 text-white lg:flex lg:flex-col lg:justify-between">
        <div>
          <p className="mono-label text-xs text-white/45">PT Coaching OS</p>
          <h1 className="mt-5 max-w-xl font-heading text-5xl font-extrabold leading-tight">
            회원 기록과 자세 분석을 한 화면에서.
          </h1>
        </div>
        <div className="grid gap-3">
          <div className="h-44 rounded-2xl border border-white/10 bg-white/8 p-5">
            <p className="mono-label text-xs text-white/45">Today</p>
            <p className="mt-4 font-display text-6xl text-white">12</p>
            <p className="mt-1 text-sm text-white/60">scheduled sessions</p>
          </div>
          <div className="accent-gradient h-2 w-44 rounded-full" />
        </div>
      </section>

      <div className="flex min-h-screen items-center justify-center px-4 py-10">
        <div className="w-full max-w-sm">
          <div className="mb-8">
            <p className="mono-label text-xs text-slate-500">FitNote Trainer</p>
            <h2 className="mt-2 font-heading text-3xl font-extrabold text-slate-900">로그인</h2>
            <p className="mt-1 text-sm text-slate-500">회원 관리 · 자세 분석 · 리포트</p>
          </div>
        <Card>
          <div className="flex border-b border-slate-200">
            <button
              type="button"
              onClick={() => setRole("trainer")}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                role === "trainer"
                  ? "border-b-2 border-mint text-slate-900"
                  : "text-slate-400 hover:text-slate-600"
              }`}
            >
              트레이너 로그인
            </button>
            <button
              type="button"
              onClick={() => setRole("member")}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                role === "member"
                  ? "border-b-2 border-mint text-slate-900"
                  : "text-slate-400 hover:text-slate-600"
              }`}
            >
              회원 로그인
            </button>
          </div>

          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 pt-2">
              {role === "trainer" ? (
                <>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-slate-700">아이디</label>
                    <Input
                      value={loginId}
                      onChange={(e) => setLoginId(e.target.value)}
                      placeholder="트레이너 아이디"
                      autoComplete="username"
                      required
                    />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-slate-700">비밀번호</label>
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
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-slate-700">이름</label>
                    <Input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="회원 이름"
                      required
                    />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-slate-700">전화번호 뒷자리 4자리</label>
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

              <Button type="submit" variant="accent" size="lg" disabled={loading} className="mt-2 w-full">
                {loading ? "로그인 중..." : "로그인"}
              </Button>
            </form>
          </CardContent>
        </Card>
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
