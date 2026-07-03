"use client";

import { useEffect } from "react";

const PRESETS = {
  coral: {
    solid: "#F26B45",
    deep: "#F55C3C",
    soft: "#FFCEB8",
    grad: "linear-gradient(135deg,#FF6B4A,#FF9E4D)",
    hover: "linear-gradient(135deg,#F55C3C,#F58F3D)",
  },
  indigo: {
    solid: "#6366F1",
    deep: "#4F46E5",
    soft: "#C7D2FE",
    grad: "linear-gradient(135deg,#5B6CFF,#8B5CF6)",
    hover: "linear-gradient(135deg,#4F46E5,#7C3AED)",
  },
  emerald: {
    solid: "#0EA478",
    deep: "#047857",
    soft: "#A7F3D0",
    grad: "linear-gradient(135deg,#10B981,#0EA5A0)",
    hover: "linear-gradient(135deg,#059669,#0F766E)",
  },
  ocean: {
    solid: "#2E7BEE",
    deep: "#2563EB",
    soft: "#BFDBFE",
    grad: "linear-gradient(135deg,#3B82F6,#22B4E6)",
    hover: "linear-gradient(135deg,#2563EB,#0891B2)",
  },
  rose: {
    solid: "#E8477E",
    deep: "#DB2777",
    soft: "#FBCFE8",
    grad: "linear-gradient(135deg,#FF5C8A,#FF87B0)",
    hover: "linear-gradient(135deg,#E11D48,#F472B6)",
  },
} as const;

export function AccentThemeProvider() {
  useEffect(() => {
    const saved = window.localStorage.getItem("fitnote.accent") as keyof typeof PRESETS | null;
    const preset = saved ? PRESETS[saved] : null;
    if (!preset) return;

    const root = document.documentElement;
    root.style.setProperty("--acc", preset.solid);
    root.style.setProperty("--acc-deep", preset.deep);
    root.style.setProperty("--acc-soft", preset.soft);
    root.style.setProperty("--acc-grad", preset.grad);
    root.style.setProperty("--acc-grad-h", preset.hover);
  }, []);

  return null;
}
