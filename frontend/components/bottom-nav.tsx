"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ICONS } from "@/components/ui/icons";
import type { NavItem } from "@/lib/nav";
import { cn } from "@/lib/utils";

/**
 * 모바일(<md) 전용 하단 고정 탭바. 실제 앱처럼 4개 핵심 메뉴만 노출한다.
 */
export function BottomNav({ items }: { items: NavItem[] }) {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 flex border-t border-slate-200 bg-white/95 backdrop-blur md:left-1/2 md:right-auto md:bottom-6 md:w-auto md:-translate-x-1/2 md:rounded-2xl md:border-0 md:bg-slate-900/94 md:px-4 md:py-1.5 md:shadow-2xl md:shadow-black/20">
      <span className="hidden items-center px-3 font-mono text-xs uppercase tracking-[0.18em] text-white/28 md:flex">
        Screens
      </span>
      {items.map((item) => {
        const Icon = NAV_ICONS[item.icon];
        const active = pathname === item.href || pathname.startsWith(item.href + "/");
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-1 flex-col items-center gap-1 py-2.5 font-ui text-[11px] font-bold md:flex-none md:flex-row md:rounded-xl md:px-4 md:py-2.5 md:text-sm",
              active
                ? "text-mint md:bg-[var(--acc)] md:text-black"
                : "text-slate-400 md:text-white/62 md:hover:text-white"
            )}
          >
            <Icon className="h-5 w-5 md:hidden" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
