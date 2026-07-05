"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { NavItem } from "@/lib/nav";
import { LogoutButton } from "./logout-button";
import { cn } from "@/lib/utils";

/**
 * 데스크탑(≥md) 전용 좌측 고정 사이드바. 관리 도구(Notion/Linear류) 느낌으로
 * 전체 메뉴를 항상 노출한다.
 */
export function DesktopSidebar({
  items,
  title,
  userName,
}: {
  items: NavItem[];
  title: string;
  userName: string;
}) {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[112px] flex-col bg-[#0b0c0f] text-white md:flex">
      <div className="flex h-24 items-center justify-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-none accent-gradient font-ui text-lg font-black text-black">
          F
        </div>
      </div>
      <span className="sr-only">{title}</span>
      <nav className="flex flex-1 flex-col items-center gap-4 pt-3">
        {items.map((item, index) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex h-[52px] w-[52px] items-center justify-center rounded-2xl font-mono text-xs font-bold transition-colors",
                active
                  ? "accent-gradient text-black"
                  : "text-white/38 hover:bg-white/8 hover:text-white"
              )}
              title={item.label}
            >
              {String(index + 1).padStart(2, "0")}
            </Link>
          );
        })}
      </nav>
      <div className="flex flex-col items-center gap-6 px-7 pb-6">
        <div className="h-px w-full bg-white/16" />
        <span className="text-xs text-white/45">↗</span>
        <LogoutButton className="h-8 w-8 rounded-full bg-transparent p-0 text-[0px] text-white/45 hover:bg-white/8" />
        <span className="sr-only">{userName}</span>
      </div>
    </aside>
  );
}
