"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { TrainerTask } from "@/lib/types";
import {
  ClockIcon,
  PieIcon,
  ListIcon,
  TableIcon,
  BoardIcon,
  PlusIcon,
  TrashIcon,
} from "@/components/ui/icons";
import { cn } from "@/lib/utils";

type Period = "today" | "week" | "all";
type ViewMode = "table" | "board";

const TABS: { key: Period; label: string; icon: typeof ClockIcon }[] = [
  { key: "today", label: "Today", icon: ClockIcon },
  { key: "week", label: "This Week", icon: PieIcon },
  { key: "all", label: "All Tasks", icon: ListIcon },
];

function today() {
  return new Date().toISOString().slice(0, 10);
}

function formatDateLabel(dateStr: string) {
  const d = new Date(`${dateStr}T00:00:00`);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

export function DailySchedule() {
  const [period, setPeriod] = useState<Period>("today");
  const [view, setView] = useState<ViewMode>("table");
  const [tasks, setTasks] = useState<TrainerTask[]>([]);
  const [loading, setLoading] = useState(true);

  const [newTime, setNewTime] = useState("");
  const [newTitle, setNewTitle] = useState("");
  const [newNotes, setNewNotes] = useState("");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    api
      .get<TrainerTask[]>(`/tasks?period=${period}`)
      .then(setTasks)
      .catch(() => setTasks([]))
      .finally(() => setLoading(false));
  }, [period]);

  async function toggleDone(task: TrainerTask) {
    const updated = await api.put<TrainerTask>(`/tasks/${task.id}`, { is_done: !task.is_done });
    setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
  }

  async function deleteTask(id: number) {
    await api.delete(`/tasks/${id}`);
    setTasks((prev) => prev.filter((t) => t.id !== id));
  }

  async function handleAdd() {
    if (!newTitle.trim()) return;
    setError(null);
    setAdding(true);
    try {
      const created = await api.post<TrainerTask>("/tasks", {
        task_date: today(),
        time_label: newTime || null,
        title: newTitle,
        notes: newNotes || null,
      });
      setTasks((prev) => [...prev, created]);
      setNewTime("");
      setNewTitle("");
      setNewNotes("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "일정 추가 중 오류가 발생했습니다");
    } finally {
      setAdding(false);
    }
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <div className="flex flex-col justify-between gap-4 border-b border-slate-200 bg-[#f7f8f4] px-5 py-4 lg:flex-row lg:items-end">
        <div>
          <p className="mono-label text-slate-400">TODAY CONTROL</p>
          <h3 className="mt-1 font-ui text-xl font-bold text-slate-950">Daily Schedule</h3>
        </div>
        <div className="flex flex-wrap items-center gap-1 rounded-full border border-slate-200 bg-white p-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const active = period === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setPeriod(tab.key)}
                className={cn(
                  "flex items-center gap-1.5 rounded-full px-3 py-2 text-xs font-semibold transition-colors",
                  active
                    ? "accent-gradient text-white"
                    : "text-slate-500 hover:bg-slate-100 hover:text-slate-900"
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex items-center gap-1 px-5 pt-4">
        <button
          onClick={() => setView("table")}
          className={cn(
            "flex items-center gap-1.5 rounded-full px-3 py-2 text-sm font-semibold transition-colors",
            view === "table"
              ? "bg-slate-950 text-white"
              : "border border-slate-300 text-slate-500 hover:bg-slate-50"
          )}
        >
          <TableIcon className="h-4 w-4" />
          Table
        </button>
        <button
          onClick={() => setView("board")}
          className={cn(
            "flex items-center gap-1.5 rounded-full px-3 py-2 text-sm font-semibold transition-colors",
            view === "board"
              ? "bg-slate-950 text-white"
              : "border border-slate-300 text-slate-500 hover:bg-slate-50"
          )}
        >
          <BoardIcon className="h-4 w-4" />
          Board
        </button>
      </div>

      <div className="p-4">
        {loading ? (
          <p className="py-6 text-center text-sm text-slate-400">불러오는 중...</p>
        ) : tasks.length === 0 ? (
          <p className="py-6 text-center text-sm text-slate-400">등록된 일정이 없습니다</p>
        ) : view === "table" ? (
          <TableView tasks={tasks} period={period} onToggle={toggleDone} onDelete={deleteTask} />
        ) : (
          <BoardView tasks={tasks} period={period} onToggle={toggleDone} onDelete={deleteTask} />
        )}

        {/* 새 일정 추가 (오늘 일정으로 추가) */}
        <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-4">
          <input
            value={newTime}
            onChange={(e) => setNewTime(e.target.value)}
            placeholder="시간"
            className="h-10 w-24 rounded-full border border-slate-200 bg-[#f7f8f4] px-3 text-sm outline-none focus:border-[var(--acc)]"
          />
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="할 일 추가"
            className="h-10 min-w-[140px] flex-1 rounded-full border border-slate-200 bg-[#f7f8f4] px-3 text-sm outline-none focus:border-[var(--acc)]"
            onKeyDown={(e) => e.key === "Enter" && handleAdd()}
          />
          <input
            value={newNotes}
            onChange={(e) => setNewNotes(e.target.value)}
            placeholder="메모"
            className="h-10 min-w-[120px] flex-1 rounded-full border border-slate-200 bg-[#f7f8f4] px-3 text-sm outline-none focus:border-[var(--acc)]"
          />
          <button
            onClick={handleAdd}
            disabled={adding || !newTitle.trim()}
            className="accent-gradient flex h-10 items-center gap-1 rounded-full px-4 text-sm font-semibold text-white transition-colors disabled:bg-slate-300 disabled:text-slate-400"
          >
            <PlusIcon className="h-3.5 w-3.5" />
            추가
          </button>
        </div>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </div>
    </div>
  );
}

type ViewProps = {
  tasks: TrainerTask[];
  period: Period;
  onToggle: (task: TrainerTask) => void;
  onDelete: (id: number) => void;
};

function TableView({ tasks, period, onToggle, onDelete }: ViewProps) {
  return (
    <table className="w-full text-left text-sm">
      <thead>
        <tr className="border-b border-slate-200 text-xs text-slate-400">
          <th className="w-8 pb-2 font-medium"></th>
          <th className="w-24 pb-2 font-medium">
            <span className="flex items-center gap-1">
              <ClockIcon className="h-3.5 w-3.5" /> Time
            </span>
          </th>
          <th className="pb-2 font-medium">
            <span className="flex items-center gap-1">
              <ListIcon className="h-3.5 w-3.5" /> Task
            </span>
          </th>
          <th className="pb-2 font-medium">Notes</th>
          <th className="w-8 pb-2"></th>
        </tr>
      </thead>
      <tbody>
        {tasks.map((t) => (
          <tr key={t.id} className="border-b border-slate-100 last:border-0 group">
            <td className="py-2.5">
              <input type="checkbox" checked={t.is_done} onChange={() => onToggle(t)} />
            </td>
            <td className="py-2.5 text-slate-600">
              {period !== "today" && <span className="mr-1 text-xs text-slate-400">{formatDateLabel(t.task_date)}</span>}
              {t.time_label || "-"}
            </td>
            <td className={cn("py-2.5 font-medium", t.is_done ? "text-slate-400 line-through" : "text-slate-800")}>
              {t.title}
            </td>
            <td className="py-2.5 text-slate-500">{t.notes || ""}</td>
            <td className="py-2.5 text-right">
              <button
                onClick={() => onDelete(t.id)}
                className="opacity-0 group-hover:opacity-100 text-slate-300 hover:text-red-500"
              >
                <TrashIcon className="h-3.5 w-3.5" />
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function BoardView({ tasks, period, onToggle, onDelete }: ViewProps) {
  const todoTasks = tasks.filter((t) => !t.is_done);
  const doneTasks = tasks.filter((t) => t.is_done);

  const columns: { label: string; items: TrainerTask[] }[] = [
    { label: "할 일", items: todoTasks },
    { label: "완료", items: doneTasks },
  ];

  return (
    <div className="grid grid-cols-2 gap-4">
      {columns.map((col) => (
        <div key={col.label} className="rounded-xl bg-slate-50 p-3">
          <p className="mb-2 text-xs font-semibold text-slate-500">
            {col.label} ({col.items.length})
          </p>
          <div className="flex flex-col gap-2">
            {col.items.map((t) => (
              <div key={t.id} className="group rounded-lg border border-slate-200 bg-white p-2.5">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className={cn("text-sm font-medium", t.is_done ? "text-slate-400 line-through" : "text-slate-800")}>
                      {t.title}
                    </p>
                    <p className="text-xs text-slate-400">
                      {period !== "today" && `${formatDateLabel(t.task_date)} · `}
                      {t.time_label || "시간 미정"}
                    </p>
                    {t.notes && <p className="mt-1 text-xs text-slate-500">{t.notes}</p>}
                  </div>
                  <button
                    onClick={() => onDelete(t.id)}
                    className="opacity-0 group-hover:opacity-100 text-slate-300 hover:text-red-500"
                  >
                    <TrashIcon className="h-3.5 w-3.5" />
                  </button>
                </div>
                <button
                  onClick={() => onToggle(t)}
                  className="mt-2 text-xs font-medium text-slate-400 hover:text-slate-700"
                >
                  {t.is_done ? "미완료로 되돌리기" : "완료로 표시"}
                </button>
              </div>
            ))}
            {col.items.length === 0 && <p className="py-4 text-center text-xs text-slate-300">없음</p>}
          </div>
        </div>
      ))}
    </div>
  );
}
