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
    label: "Coral",
    solid: "#F26B45",
    deep: "#F55C3C",
    soft: "#FFCEB8",
    grad: "linear-gradient(135deg,#FF6B4A,#FF9E4D)",
    hover: "linear-gradient(135deg,#F55C3C,#F58F3D)",
  },
  {
    key: "indigo",
    label: "Indigo",
    solid: "#6366F1",
    deep: "#4F46E5",
    soft: "#C7D2FE",
    grad: "linear-gradient(135deg,#5B6CFF,#8B5CF6)",
    hover: "linear-gradient(135deg,#4F46E5,#7C3AED)",
  },
  {
    key: "emerald",
    label: "Emerald",
    solid: "#0EA478",
    deep: "#047857",
    soft: "#A7F3D0",
    grad: "linear-gradient(135deg,#10B981,#0EA5A0)",
    hover: "linear-gradient(135deg,#059669,#0F766E)",
  },
  {
    key: "ocean",
    label: "Ocean",
    solid: "#2E7BEE",
    deep: "#2563EB",
    soft: "#BFDBFE",
    grad: "linear-gradient(135deg,#3B82F6,#22B4E6)",
    hover: "linear-gradient(135deg,#2563EB,#0891B2)",
  },
  {
    key: "rose",
    label: "Rose",
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
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {PRESETS.map((preset) => {
        const active = selectedKey === preset.key;
        return (
          <button
            key={preset.key}
            type="button"
            onClick={() => selectPreset(preset)}
            className={cn(
              "flex items-center gap-3 rounded-xl border bg-white p-3 text-left transition-colors",
              active ? "border-mint ring-2 ring-mint-soft/60" : "border-slate-200 hover:border-slate-300"
            )}
          >
            <span
              className="h-9 w-9 shrink-0 rounded-full border border-white shadow-sm"
              style={{ background: preset.grad }}
            />
            <span>
              <span className="block font-ui text-sm font-bold text-slate-900">{preset.label}</span>
              <span className="mono-label text-[10px] text-slate-400">{preset.key}</span>
            </span>
          </button>
        );
      })}
    </div>
  );
}
