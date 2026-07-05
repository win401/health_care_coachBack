'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SettingsIcon } from '@/components/ui/icons';

const META = [
  {
    match: '/trainer/dashboard',
    eyebrow: 'HOME · 회원 대시보드',
    title: '오늘의 트레이닝',
  },
  {
    match: '/trainer/sessions',
    eyebrow: 'SESSION · 수업 기록',
    title: '세션 기록 & 자세 분석',
  },
  {
    match: '/trainer/reports',
    eyebrow: 'REPORT · 회원 리포트',
    title: '오늘의 PT 리포트',
  },
  {
    match: '/trainer/members',
    eyebrow: 'MEMBER · 신규 등록',
    title: '회원 등록 / 프로필',
  },
  {
    match: '/trainer/settings',
    eyebrow: 'SETTINGS · 환경 설정',
    title: '설정',
  },
];

export function TrainerTopBar({ userName }: { userName: string }) {
  const pathname = usePathname();
  const current =
    META.find(
      (item) =>
        pathname === item.match || pathname.startsWith(`${item.match}/`),
    ) ?? META[0];

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-background/92 backdrop-blur">
      <div className="flex min-h-28 items-center justify-between gap-5 px-5 py-5 md:px-10">
        <div>
          <p className="mono-label text-sm text-slate-400">{current.eyebrow}</p>
          <h1 className="mt-1 font-heading text-3xl font-black leading-none text-slate-950 md:text-2xl">
            {current.title}
          </h1>
        </div>
        <div className="hidden items-center gap-6 sm:flex">
          <Link
            href="/trainer/settings"
            className="flex h-12 w-12 items-center justify-center rounded-xl border border-slate-200 bg-white shadow-sm transition-colors hover:border-[var(--acc)]"
            aria-label="설정"
          >
            <SettingsIcon className="h-5 w-5 text-slate-600" />
          </Link>
          <div className="text-right">
            <p className="font-ui text-base font-black text-slate-950">
              {userName}
            </p>
            <p className="mt-1 font-mono text-sm text-slate-400">
              2026 · 7월 3일 (금)
            </p>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-950 font-heading text-xl font-black text-[var(--acc)]">
            {userName.slice(0, 1)}
          </div>
        </div>
      </div>
    </header>
  );
}
