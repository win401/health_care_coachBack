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
    <nav className="fixed inset-x-0 bottom-0 z-40 flex border-t border-slate-200 bg-white/95 backdrop-blur md:hidden">
      {items.map((item) => {
        const Icon = NAV_ICONS[item.icon];
        const active = pathname === item.href || pathname.startsWith(item.href + "/");
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-1 flex-col items-center gap-1 py-2.5 text-[11px] font-medium",
              active ? "text-slate-900" : "text-slate-400"
            )}
          >
            <Icon className="h-5 w-5" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
