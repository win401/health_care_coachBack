"use client";

import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { LogoutIcon } from "@/components/ui/icons";
import { cn } from "@/lib/utils";

export function LogoutButton({ className }: { className?: string }) {
  const router = useRouter();

  async function handleLogout() {
    await api.post("/auth/logout");
    router.replace("/login");
    router.refresh();
  }

  return (
    <button
      onClick={handleLogout}
      className={cn(
        "flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-500 hover:bg-slate-100 hover:text-slate-900",
        className
      )}
    >
      <LogoutIcon className="h-4 w-4" />
      로그아웃
    </button>
  );
}
