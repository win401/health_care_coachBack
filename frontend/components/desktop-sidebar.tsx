"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ICONS } from "@/components/ui/icons";
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
    <aside className="dark-panel hidden md:flex md:w-64 md:flex-col md:text-white">
      <div className="flex h-20 items-center px-6">
        <span className="font-display text-2xl uppercase text-white">{title}</span>
      </div>
      <nav className="flex-1 space-y-1 px-4">
        {items.map((item, index) => {
          const Icon = NAV_ICONS[item.icon];
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-xl border-l-2 px-3 py-3 font-ui text-sm font-semibold transition-colors",
                active
                  ? "border-mint bg-white/10 text-white"
                  : "border-transparent text-white/58 hover:bg-white/8 hover:text-white"
              )}
            >
              <span className="mono-label w-6 text-[10px] text-white/35">{String(index + 1).padStart(2, "0")}</span>
              <Icon className="h-4.5 w-4.5 text-current" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-white/10 p-4">
        <div className="mb-2 px-3 py-1 text-xs text-white/45">{userName}</div>
        <LogoutButton className="w-full" />
      </div>
    </aside>
  );
}
