"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { Assignment } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const STATUS_LABEL: Record<string, string> = {
  unchecked: "미확인",
  in_progress: "진행 중",
  completed: "완료",
};

export function AssignmentsClient({ assignments }: { assignments: Assignment[] }) {
  const [list, setList] = useState(assignments);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  async function markCompleted(id: number) {
    setUpdatingId(id);
    try {
      const updated = await api.put<Assignment>(`/my/assignments/${id}?status_value=completed`);
      setList((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } finally {
      setUpdatingId(null);
    }
  }

  if (list.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-sm text-slate-400">
          등록된 과제가 없습니다
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {list.map((a) => (
        <Card key={a.id}>
          <CardContent className="flex items-center justify-between gap-3 py-4">
            <div>
              <p className="text-sm font-semibold text-slate-900">{a.title}</p>
              <p className="text-xs text-slate-400">
                {a.target_amount ? `목표: ${a.target_amount}` : ""}
                {a.due_date ? ` · 마감 ${a.due_date}` : ""}
              </p>
              <span
                className={`mt-1 inline-block rounded-full px-2 py-0.5 text-[11px] ${
                  a.status === "completed"
                    ? "bg-emerald-100 text-emerald-700"
                    : "bg-slate-100 text-slate-500"
                }`}
              >
                {STATUS_LABEL[a.status] || a.status}
              </span>
            </div>
            {a.status !== "completed" && (
              <Button size="sm" variant="secondary" disabled={updatingId === a.id} onClick={() => markCompleted(a.id)}>
                완료 체크
              </Button>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
