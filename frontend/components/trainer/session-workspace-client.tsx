"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { Member, PostureImage, Session, SessionExercise, VoiceRecordingSummary } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CameraIcon, MicIcon, StopIcon } from "@/components/ui/icons";
import { cn } from "@/lib/utils";

type VoiceSummary = {
  exercise_summary: string;
  caution_note: string;
  assignment_candidate: string;
};

const today = () => new Date().toISOString().slice(0, 10);

export function SessionWorkspaceClient({ member }: { member: Member }) {
  const router = useRouter();

  // ---- 1. 회원 및 수업 정보 + 2. 세션 기록 ----
  const [sessionDate, setSessionDate] = useState(today());
  const [focusArea, setFocusArea] = useState("하체");
  const [memo, setMemo] = useState("");
  const [nextMemo, setNextMemo] = useState("");
  const [exercises, setExercises] = useState<SessionExercise[]>([
    { exercise_name: "", sets: null, reps: null, weight_kg: null, note: null },
  ]);
  const [session, setSession] = useState<Session | null>(null);
  const [savingSession, setSavingSession] = useState(false);
  const [sessionError, setSessionError] = useState<string | null>(null);

  // ---- 3. 음성 메모 요약 (녹음 / 직접 입력) ----
  const [voiceMode, setVoiceMode] = useState<"record" | "manual">("record");
  const [voiceText, setVoiceText] = useState("");
  const [voiceSummary, setVoiceSummary] = useState<VoiceSummary | null>(null);
  const [summarizing, setSummarizing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedUrl, setRecordedUrl] = useState<string | null>(null);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [transcribing, setTranscribing] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordedBlobRef = useRef<Blob | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ---- 4. 자세 분석 ----
  const [movementName, setMovementName] = useState("스쿼트");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [postureImage, setPostureImage] = useState<PostureImage | null>(null);
  const [selectedPreviewUrl, setSelectedPreviewUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [postureError, setPostureError] = useState<string | null>(null);

  // ---- 5. 트레이너 피드백 ----
  const [trainerComment, setTrainerComment] = useState("");
  const [cautionNote, setCautionNote] = useState("");
  const [nextCheckPoint, setNextCheckPoint] = useState("");
  const [feedbackSaved, setFeedbackSaved] = useState(false);
  const [savingFeedback, setSavingFeedback] = useState(false);

  // ---- 6. 과제 등록 ----
  const [assignmentTitle, setAssignmentTitle] = useState("");
  const [assignmentTarget, setAssignmentTarget] = useState("");
  const [assignmentDue, setAssignmentDue] = useState("");
  const [assignmentSaved, setAssignmentSaved] = useState(false);
  const [savingAssignment, setSavingAssignment] = useState(false);

  function updateExercise(index: number, patch: Partial<SessionExercise>) {
    setExercises((prev) => prev.map((ex, i) => (i === index ? { ...ex, ...patch } : ex)));
  }

  function addExerciseRow() {
    setExercises((prev) => [...prev, { exercise_name: "", sets: null, reps: null, weight_kg: null, note: null }]);
  }

  async function handleSaveSession() {
    setSessionError(null);
    setSavingSession(true);
    try {
      const composedSummary = voiceSummary
        ? `${focusArea || "운동"} 세션. ${voiceSummary.exercise_summary}`
        : undefined;
      const created = await api.post<Session>("/sessions", {
        member_id: member.id,
        session_date: sessionDate,
        focus_area: focusArea,
        memo,
        next_memo: nextMemo,
        raw_voice_text: voiceText || undefined,
        summary: composedSummary,
        exercises: exercises.filter((ex) => ex.exercise_name.trim()),
      });
      setSession(created);
    } catch (err) {
      setSessionError(err instanceof ApiError ? err.detail : "세션 저장 중 오류가 발생했습니다");
    } finally {
      setSavingSession(false);
    }
  }

  async function handleSummarizeVoice() {
    setSummarizing(true);
    try {
      const result = await api.post<VoiceSummary>("/sessions/voice-summary", { raw_text: voiceText });
      setVoiceSummary(result);
    } catch {
      setVoiceSummary(null);
    } finally {
      setSummarizing(false);
    }
  }

  // 컴포넌트가 사라질 때 마이크 스트림/미리듣기 URL 정리
  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      if (timerRef.current) clearInterval(timerRef.current);
      if (recordedUrl) URL.revokeObjectURL(recordedUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function resetRecording() {
    setRecordedUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });
    recordedBlobRef.current = null;
    setRecordingSeconds(0);
  }

  async function startRecording() {
    setVoiceError(null);
    resetRecording();
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      audioChunksRef.current = [];
      const mimeType = typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "";
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: recorder.mimeType || "audio/webm" });
        recordedBlobRef.current = blob;
        setRecordedUrl(URL.createObjectURL(blob));
        streamRef.current?.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
      setRecordingSeconds(0);
      timerRef.current = setInterval(() => setRecordingSeconds((s) => s + 1), 1000);
    } catch {
      setVoiceError("마이크 접근 권한이 필요합니다. 브라우저 권한 설정을 확인해주세요.");
    }
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }

  async function handleUploadRecording() {
    const blob = recordedBlobRef.current;
    if (!blob) return;
    setVoiceError(null);
    setTranscribing(true);
    try {
      const formData = new FormData();
      const ext = blob.type.includes("webm") ? "webm" : "mp4";
      formData.append("file", blob, `recording.${ext}`);
      const result = await api.postForm<VoiceRecordingSummary>("/sessions/voice-recording", formData);
      if (!result.transcribed) {
        setVoiceError(result.message || "자동 변환에 실패했습니다. 텍스트로 직접 입력해주세요.");
        setVoiceMode("manual");
        return;
      }
      setVoiceText(result.raw_voice_text || "");
      setVoiceSummary({
        exercise_summary: result.exercise_summary || "",
        caution_note: result.caution_note || "",
        assignment_candidate: result.assignment_candidate || "",
      });
      resetRecording();
    } catch (err) {
      setVoiceError(err instanceof ApiError ? err.detail : "녹음 업로드 중 오류가 발생했습니다");
    } finally {
      setTranscribing(false);
    }
  }

  function formatSeconds(total: number) {
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  function handleSelectFile() {
    const file = fileInputRef.current?.files?.[0];
    setSelectedPreviewUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return file ? URL.createObjectURL(file) : null;
    });
  }

  async function handleUploadImage() {
    const file = fileInputRef.current?.files?.[0];
    if (!file) return;
    setPostureError(null);
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("member_id", String(member.id));
      if (session) formData.append("session_id", String(session.id));
      formData.append("movement_name", movementName);
      formData.append("file", file);
      const uploaded = await api.postForm<PostureImage>("/posture/images", formData);
      setPostureImage(uploaded);
      setSelectedPreviewUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return null;
      });
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setPostureError(err instanceof ApiError ? err.detail : "이미지 업로드 중 오류가 발생했습니다");
    } finally {
      setUploading(false);
    }
  }

  async function handleAnalyze() {
    if (!postureImage) return;
    setAnalyzing(true);
    setPostureError(null);
    try {
      const analyzed = await api.post<PostureImage>(`/posture/images/${postureImage.id}/analyze`);
      setPostureImage(analyzed);
    } catch (err) {
      setPostureError(err instanceof ApiError ? err.detail : "분석 중 오류가 발생했습니다");
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleSaveFeedback() {
    if (!trainerComment.trim()) return;
    setSavingFeedback(true);
    try {
      await api.post("/feedbacks", {
        member_id: member.id,
        session_id: session?.id,
        analysis_id: postureImage?.analysis?.id,
        trainer_comment: trainerComment,
        caution_note: cautionNote || undefined,
        next_check_point: nextCheckPoint || undefined,
      });
      setFeedbackSaved(true);
    } finally {
      setSavingFeedback(false);
    }
  }

  async function handleSaveAssignment() {
    if (!assignmentTitle.trim()) return;
    setSavingAssignment(true);
    try {
      await api.post("/assignments", {
        member_id: member.id,
        session_id: session?.id,
        title: assignmentTitle,
        target_amount: assignmentTarget || undefined,
        due_date: assignmentDue || undefined,
      });
      setAssignmentSaved(true);
    } finally {
      setSavingAssignment(false);
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-4 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{member.name} 회원 수업 기록</h1>
          <p className="text-sm text-slate-500">{member.fitness_goal}</p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => router.push(`/trainer/reports/${member.id}`)}
        >
          리포트로 이동
        </Button>
      </div>

      {/* 1~2. 회원/수업 정보 + 세션 기록 */}
      <Card>
        <CardHeader>
          <CardTitle>① 수업 정보 & 세션 기록</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="수업일">
              <Input type="date" value={sessionDate} onChange={(e) => setSessionDate(e.target.value)} />
            </Field>
            <Field label="운동 부위">
              <Input value={focusArea} onChange={(e) => setFocusArea(e.target.value)} placeholder="예: 하체" />
            </Field>
          </div>
          <Field label="수업 메모">
            <Textarea rows={2} value={memo} onChange={(e) => setMemo(e.target.value)} />
          </Field>

          <div className="flex flex-col gap-2">
            <p className="text-sm font-medium text-slate-700">운동 기록</p>
            {exercises.map((ex, i) => (
              <div key={i} className="grid grid-cols-4 gap-2">
                <Input
                  className="col-span-2"
                  placeholder="운동명"
                  value={ex.exercise_name}
                  onChange={(e) => updateExercise(i, { exercise_name: e.target.value })}
                />
                <Input
                  placeholder="세트"
                  type="number"
                  value={ex.sets ?? ""}
                  onChange={(e) => updateExercise(i, { sets: e.target.value ? Number(e.target.value) : null })}
                />
                <Input
                  placeholder="반복"
                  type="number"
                  value={ex.reps ?? ""}
                  onChange={(e) => updateExercise(i, { reps: e.target.value ? Number(e.target.value) : null })}
                />
              </div>
            ))}
            <Button type="button" variant="ghost" size="sm" onClick={addExerciseRow} className="self-start">
              + 운동 추가
            </Button>
          </div>

          <Field label="다음 수업 메모">
            <Input value={nextMemo} onChange={(e) => setNextMemo(e.target.value)} />
          </Field>

          {sessionError && <p className="text-sm text-red-600">{sessionError}</p>}
          <Button onClick={handleSaveSession} disabled={savingSession}>
            {session ? "세션 정보 다시 저장" : savingSession ? "저장 중..." : "세션 저장"}
          </Button>
          {session && <p className="text-xs text-emerald-600">세션 #{session.id} 저장됨</p>}
        </CardContent>
      </Card>

      {/* 3. 음성 메모 요약 */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>② 음성 메모 요약</CardTitle>
          <div className="flex gap-1 rounded-full border border-slate-300 p-0.5">
            <button
              type="button"
              onClick={() => setVoiceMode("record")}
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium transition-colors",
                voiceMode === "record" ? "bg-slate-900 text-white" : "text-slate-500"
              )}
            >
              녹음
            </button>
            <button
              type="button"
              onClick={() => setVoiceMode("manual")}
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium transition-colors",
                voiceMode === "manual" ? "bg-slate-900 text-white" : "text-slate-500"
              )}
            >
              직접 입력
            </button>
          </div>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {voiceMode === "record" ? (
            <div className="flex flex-col items-center gap-3 rounded-lg bg-slate-50 py-6">
              {!recordedUrl ? (
                <>
                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    className={cn(
                      "flex h-16 w-16 items-center justify-center rounded-full text-white transition-colors",
                      isRecording ? "bg-red-500 animate-pulse" : "bg-mint text-slate-900 hover:bg-mint-deep"
                    )}
                  >
                    {isRecording ? <StopIcon className="h-6 w-6" /> : <MicIcon className="h-6 w-6" />}
                  </button>
                  <p className="text-sm text-slate-500">
                    {isRecording ? `녹음 중... ${formatSeconds(recordingSeconds)}` : "버튼을 눌러 음성 메모 녹음"}
                  </p>
                </>
              ) : (
                <div className="flex w-full flex-col items-center gap-3 px-4">
                  <audio controls src={recordedUrl} className="w-full" />
                  <div className="flex gap-2">
                    <Button type="button" variant="secondary" size="sm" onClick={startRecording}>
                      다시 녹음
                    </Button>
                    <Button type="button" variant="accent" size="sm" onClick={handleUploadRecording} disabled={transcribing}>
                      {transcribing ? "변환/요약 중..." : "업로드 후 요약"}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <>
              <Textarea
                rows={4}
                value={voiceText}
                onChange={(e) => setVoiceText(e.target.value)}
                placeholder="수업 중 음성 메모를 텍스트로 입력하세요 (예: 오늘 하체 운동 진행, 무릎이 안쪽으로 모이는 경향...)"
              />
              <Button variant="secondary" onClick={handleSummarizeVoice} disabled={summarizing || !voiceText.trim()}>
                {summarizing ? "요약 중..." : "음성 메모 요약"}
              </Button>
            </>
          )}

          {voiceError && <p className="text-sm text-red-600">{voiceError}</p>}

          {voiceSummary && (
            <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
              <p>운동 내용: {voiceSummary.exercise_summary}</p>
              <p>주의사항: {voiceSummary.caution_note}</p>
              <p>과제 후보: {voiceSummary.assignment_candidate}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 4. 자세 분석 */}
      <Card>
        <CardHeader>
          <CardTitle>③ 자세 분석 (AI/YOLO)</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Field label="운동 동작">
            <Input value={movementName} onChange={(e) => setMovementName(e.target.value)} />
          </Field>
          <div className="flex flex-wrap items-center gap-2">
            {/* capture="environment"는 모바일 브라우저에서 후면 카메라를 바로 열어준다.
                데스크탑에서는 무시되고 기존 파일 선택 창이 그대로 뜬다. */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleSelectFile}
              className="text-sm"
            />
            <Button type="button" variant="secondary" size="sm" onClick={handleUploadImage} disabled={uploading}>
              <CameraIcon className="h-4 w-4" />
              {uploading ? "업로드 중..." : "사진 업로드"}
            </Button>
          </div>

          {selectedPreviewUrl && !uploading && (
            <div className="flex flex-col gap-1">
              <p className="text-xs text-slate-400">촬영/선택한 사진 미리보기 (아직 업로드 전)</p>
              <img
                src={selectedPreviewUrl}
                alt="선택한 사진 미리보기"
                className="max-h-64 w-full rounded-lg border border-dashed border-slate-300 object-contain"
              />
            </div>
          )}

          {postureImage && (
            <div className="flex flex-col gap-2">
              <img
                src={postureImage.image_path}
                alt="업로드된 자세 사진"
                className="max-h-64 w-full rounded-lg border border-slate-200 object-contain"
              />
              <Button size="sm" onClick={handleAnalyze} disabled={analyzing}>
                {analyzing ? "분석 중..." : "AI로 분석하기"}
              </Button>
            </div>
          )}

          {postureError && <p className="text-sm text-red-600">{postureError}</p>}

          {postureImage?.analysis && (
            <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
              <p className="font-medium">자세 점수: {postureImage.analysis.total_score}점</p>
              <p>주요 문제: {postureImage.analysis.main_issue}</p>
              <p>보조 문제: {postureImage.analysis.sub_issue}</p>
              <p>개선 포인트: {postureImage.analysis.improvement_points}</p>
              <p className="mt-1 text-xs text-slate-400">
                모델: {postureImage.analysis.model_name || "-"} · {postureImage.analysis.result_note}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 5. 트레이너 피드백 */}
      <Card>
        <CardHeader>
          <CardTitle>④ 트레이너 피드백</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Field label="코멘트">
            <Textarea rows={2} value={trainerComment} onChange={(e) => setTrainerComment(e.target.value)} />
          </Field>
          <Field label="주의사항">
            <Input value={cautionNote} onChange={(e) => setCautionNote(e.target.value)} />
          </Field>
          <Field label="다음 수업 확인사항">
            <Input value={nextCheckPoint} onChange={(e) => setNextCheckPoint(e.target.value)} />
          </Field>
          <Button onClick={handleSaveFeedback} disabled={savingFeedback || !trainerComment.trim()}>
            {savingFeedback ? "저장 중..." : "피드백 저장"}
          </Button>
          {feedbackSaved && <p className="text-xs text-emerald-600">피드백이 저장되었습니다</p>}
        </CardContent>
      </Card>

      {/* 6. 과제 등록 */}
      <Card>
        <CardHeader>
          <CardTitle>⑤ 과제 등록</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Field label="과제명">
            <Input value={assignmentTitle} onChange={(e) => setAssignmentTitle(e.target.value)} placeholder="예: 벽 스쿼트 20회" />
          </Field>
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="목표량">
              <Input value={assignmentTarget} onChange={(e) => setAssignmentTarget(e.target.value)} placeholder="예: 20회" />
            </Field>
            <Field label="마감일">
              <Input type="date" value={assignmentDue} onChange={(e) => setAssignmentDue(e.target.value)} />
            </Field>
          </div>
          <Button onClick={handleSaveAssignment} disabled={savingAssignment || !assignmentTitle.trim()}>
            {savingAssignment ? "저장 중..." : "과제 저장"}
          </Button>
          {assignmentSaved && <p className="text-xs text-emerald-600">과제가 등록되었습니다</p>}
        </CardContent>
      </Card>
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
