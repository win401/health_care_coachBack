"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { Member } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function NewMemberPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [fitnessGoal, setFitnessGoal] = useState("");
  const [exerciseExperience, setExerciseExperience] = useState("");
  const [painArea, setPainArea] = useState("");
  const [injuryHistory, setInjuryHistory] = useState("");
  const [precautions, setPrecautions] = useState("");
  const [shoulderAsym, setShoulderAsym] = useState(false);
  const [pelvisAsym, setPelvisAsym] = useState(false);
  const [otherAsym, setOtherAsym] = useState("");
  const [consentAgreed, setConsentAgreed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("회원 이름은 필수입니다");
      return;
    }
    if (!fitnessGoal.trim()) {
      setError("운동 목표는 필수입니다");
      return;
    }

    const asymmetryParts = [
      shoulderAsym ? "어깨" : null,
      pelvisAsym ? "골반" : null,
      otherAsym ? `기타: ${otherAsym}` : null,
    ].filter(Boolean);

    setLoading(true);
    try {
      const created = await api.post<Member>("/members", {
        name,
        phone: phone || null,
        age: age ? Number(age) : null,
        gender: gender || null,
        fitness_goal: fitnessGoal,
        exercise_experience: exerciseExperience || null,
        health_note: {
          pain_area: painArea || "없음",
          injury_history: injuryHistory || null,
          precautions: precautions || "없음",
          asymmetry_note: asymmetryParts.length ? asymmetryParts.join(", ") : "특이 비대칭 없음",
        },
        consent_agreed: consentAgreed,
      });
      router.push(`/trainer/sessions/${created.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "회원 등록 중 오류가 발생했습니다");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-4 md:p-6">
      <h1 className="mb-4 text-xl font-bold text-slate-900">신규 회원 등록</h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Card>
          <CardHeader>
            <CardTitle>기본 정보</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            <Field label="이름 *">
              <Input value={name} onChange={(e) => setName(e.target.value)} required />
            </Field>
            <Field label="연락처">
              <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="010-0000-0000" />
            </Field>
            <Field label="나이">
              <Input type="number" value={age} onChange={(e) => setAge(e.target.value)} />
            </Field>
            <Field label="성별">
              <div className="flex gap-2 pt-1">
                {["F", "M", "기타"].map((g) => (
                  <button
                    type="button"
                    key={g}
                    onClick={() => setGender(g)}
                    className={`rounded-lg border px-3 py-1.5 text-sm ${
                      gender === g
                        ? "border-slate-900 bg-slate-900 text-white"
                        : "border-slate-300 text-slate-600"
                    }`}
                  >
                    {g === "F" ? "여성" : g === "M" ? "남성" : "기타"}
                  </button>
                ))}
              </div>
            </Field>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>운동 정보</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Field label="운동 목표 *">
              <Input
                value={fitnessGoal}
                onChange={(e) => setFitnessGoal(e.target.value)}
                placeholder="예: 체중 감량, 자세 교정"
                required
              />
            </Field>
            <Field label="운동 경험">
              <Input
                value={exerciseExperience}
                onChange={(e) => setExerciseExperience(e.target.value)}
                placeholder="예: 1년, 헬스 초보"
              />
            </Field>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>건강 주의사항</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Field label="통증 부위">
              <Input value={painArea} onChange={(e) => setPainArea(e.target.value)} placeholder="없으면 비워두세요" />
            </Field>
            <Field label="부상 이력">
              <Textarea rows={2} value={injuryHistory} onChange={(e) => setInjuryHistory(e.target.value)} />
            </Field>
            <Field label="수업 주의사항">
              <Textarea rows={2} value={precautions} onChange={(e) => setPrecautions(e.target.value)} />
            </Field>
            <Field label="비대칭 체크">
              <div className="flex flex-wrap items-center gap-4 pt-1">
                <label className="flex items-center gap-2 text-sm text-slate-700">
                  <input type="checkbox" checked={shoulderAsym} onChange={(e) => setShoulderAsym(e.target.checked)} />
                  어깨 비대칭
                </label>
                <label className="flex items-center gap-2 text-sm text-slate-700">
                  <input type="checkbox" checked={pelvisAsym} onChange={(e) => setPelvisAsym(e.target.checked)} />
                  골반 비대칭
                </label>
                <Input
                  value={otherAsym}
                  onChange={(e) => setOtherAsym(e.target.value)}
                  placeholder="기타 비대칭"
                  className="max-w-[180px]"
                />
              </div>
            </Field>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-start gap-3 pt-5">
            <input
              type="checkbox"
              checked={consentAgreed}
              onChange={(e) => setConsentAgreed(e.target.checked)}
              className="mt-1"
            />
            <p className="text-sm text-slate-600">
              신체·건강 정보는 자세 분석 참고용으로만 사용되며, 의료 진단이 아닙니다. 회원에게 안내 후
              동의를 받았습니다.
            </p>
          </CardContent>
        </Card>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="flex gap-2">
          <Button type="submit" size="lg" disabled={loading} className="flex-1">
            {loading ? "저장 중..." : "회원 저장"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            size="lg"
            onClick={() => router.back()}
          >
            취소
          </Button>
        </div>
      </form>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-slate-700">{label}</label>
      {children}
    </div>
  );
}
