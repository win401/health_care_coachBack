"use client";

import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { LogoutIcon } from "@/components/ui/icons";

export function MobileHeader({ title, userName }: { title: string; userName: string }) {
  const router = useRouter();

  async function handleLogout() {
    await api.post("/auth/logout");
    router.replace("/login");
    router.refresh();
  }

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur md:hidden">
      <div>
        <p className="text-sm font-bold text-slate-900">{title}</p>
        <p className="text-[11px] text-slate-400">{userName}</p>
      </div>
      <button onClick={handleLogout} className="p-2 text-slate-400 hover:text-slate-700">
        <LogoutIcon className="h-5 w-5" />
      </button>
    </header>
  );
}
