"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

type AccentPreset = {
  key: string;
  label: string;
  solid: string;
  deep: string;
  soft: string;
  grad: string;
  hover: string;
};

const PRESETS: AccentPreset[] = [
  {
    key: "coral",
    label: "코랄",
    solid: "#F26B45",
    deep: "#F55C3C",
    soft: "#FFCEB8",
    grad: "linear-gradient(135deg,#FF6B4A,#FF9E4D)",
    hover: "linear-gradient(135deg,#F55C3C,#F58F3D)",
  },
  {
    key: "indigo",
    label: "인디고",
    solid: "#6366F1",
    deep: "#4F46E5",
    soft: "#C7D2FE",
    grad: "linear-gradient(135deg,#5B6CFF,#8B5CF6)",
    hover: "linear-gradient(135deg,#4F46E5,#7C3AED)",
  },
  {
    key: "emerald",
    label: "에메랄드",
    solid: "#0EA478",
    deep: "#047857",
    soft: "#A7F3D0",
    grad: "linear-gradient(135deg,#10B981,#0EA5A0)",
    hover: "linear-gradient(135deg,#059669,#0F766E)",
  },
  {
    key: "ocean",
    label: "오션",
    solid: "#2E7BEE",
    deep: "#2563EB",
    soft: "#BFDBFE",
    grad: "linear-gradient(135deg,#3B82F6,#22B4E6)",
    hover: "linear-gradient(135deg,#2563EB,#0891B2)",
  },
  {
    key: "rose",
    label: "로즈",
    solid: "#E8477E",
    deep: "#DB2777",
    soft: "#FBCFE8",
    grad: "linear-gradient(135deg,#FF5C8A,#FF87B0)",
    hover: "linear-gradient(135deg,#E11D48,#F472B6)",
  },
];

const STORAGE_KEY = "fitnote.accent";

function applyPreset(preset: AccentPreset) {
  const root = document.documentElement;
  root.style.setProperty("--acc", preset.solid);
  root.style.setProperty("--acc-deep", preset.deep);
  root.style.setProperty("--acc-soft", preset.soft);
  root.style.setProperty("--acc-grad", preset.grad);
  root.style.setProperty("--acc-grad-h", preset.hover);
}

export function AccentPicker() {
  const [selectedKey, setSelectedKey] = useState(() => {
    if (typeof window === "undefined") return "coral";
    return window.localStorage.getItem(STORAGE_KEY) ?? "coral";
  });

  useEffect(() => {
    const preset = PRESETS.find((item) => item.key === selectedKey) ?? PRESETS[0];
    applyPreset(preset);
  }, [selectedKey]);

  function selectPreset(preset: AccentPreset) {
    applyPreset(preset);
    setSelectedKey(preset.key);
    window.localStorage.setItem(STORAGE_KEY, preset.key);
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {PRESETS.map((preset) => {
        const active = selectedKey === preset.key;
        return (
          <button
            key={preset.key}
            type="button"
            onClick={() => selectPreset(preset)}
            className={cn(
              "flex items-center justify-between gap-4 rounded-2xl border bg-[#f7f8f4] p-5 text-left transition-colors",
              active ? "border-slate-950 ring-2 ring-slate-950" : "border-transparent hover:border-slate-300"
            )}
          >
            <span className="flex items-center gap-6">
              <span
                className="h-14 w-14 shrink-0 rounded-xl border border-white shadow-lg"
                style={{ background: preset.grad }}
              />
              <span>
                <span className="block font-heading text-xl font-black text-slate-950">{preset.label}</span>
                <span className="mt-1 block text-sm text-slate-500">
                  {preset.key === "coral" ? "따뜻·활동적" : preset.key === "indigo" ? "차분·프리미엄" : preset.key === "emerald" ? "건강·신선" : preset.key === "ocean" ? "시원·선명" : "부드러운 포인트"}
                </span>
              </span>
            </span>
            <span className={cn(
              "grid h-7 w-7 place-items-center rounded-full border-[3px] text-xs",
              active ? "border-slate-950 bg-slate-950 text-white" : "border-slate-300 text-transparent"
            )}>
              ✓
            </span>
          </button>
        );
      })}
    </div>
  );
}
