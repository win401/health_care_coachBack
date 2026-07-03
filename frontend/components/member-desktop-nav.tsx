"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ICONS } from "@/components/ui/icons";
import type { NavItem } from "@/lib/nav";
import { LogoutButton } from "./logout-button";
import { cn } from "@/lib/utils";

/**
 * 회원 포털은 트레이너용 관리 도구와 달리 "개인 앱" 느낌을 유지한다.
 * 데스크탑에서도 사이드바 대신 중앙 정렬된 좁은 카드 + 상단 가로 탭으로 노출한다.
 */
export function MemberDesktopNav({ items, userName }: { items: NavItem[]; userName: string }) {
  const pathname = usePathname();

  return (
    <header className="hidden border-b border-slate-200 bg-white md:block">
      <div className="mx-auto flex max-w-md items-center justify-between px-4 py-3">
        <div>
          <p className="text-sm font-bold text-slate-900">FitNote</p>
          <p className="text-xs text-slate-400">{userName} 회원님</p>
        </div>
        <LogoutButton />
      </div>
      <nav className="mx-auto flex max-w-md gap-1 px-4 pb-2">
        {items.map((item) => {
          const Icon = NAV_ICONS[item.icon];
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-1 flex-col items-center gap-1 rounded-lg py-2 text-xs font-medium",
                active ? "bg-slate-900 text-white" : "text-slate-500 hover:bg-slate-100"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
