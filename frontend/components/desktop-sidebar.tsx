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
    <aside className="hidden md:flex md:w-60 md:flex-col md:border-r md:border-slate-200 md:bg-white">
      <div className="flex h-16 items-center px-5">
        <span className="text-lg font-bold text-slate-900">{title}</span>
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {items.map((item) => {
          const Icon = NAV_ICONS[item.icon];
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-slate-900 text-white"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )}
            >
              <Icon className="h-4.5 w-4.5" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-slate-200 p-3">
        <div className="mb-1 px-3 py-1 text-xs text-slate-400">{userName}</div>
        <LogoutButton className="w-full" />
      </div>
    </aside>
  );
}
