"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Member } from "@/lib/types";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export function MembersListClient({ members }: { members: Member[] }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(
    () => members.filter((m) => m.name.includes(query.trim())),
    [members, query]
  );

  return (
    <div className="flex flex-col gap-4 p-4 md:p-6">
      <div className="flex items-center gap-3">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="회원 이름 검색"
          className="max-w-xs"
        />
        <Link href="/trainer/members/new" className="ml-auto">
          <Button>+ 신규 회원 등록</Button>
        </Link>
      </div>

      {filtered.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-slate-400">
            등록된 회원이 없습니다
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((m) => (
            <Card key={m.id}>
              <CardContent className="flex flex-col gap-2 py-4">
                <div className="flex items-center justify-between">
                  <p className="text-base font-semibold text-slate-900">{m.name}</p>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
                    {m.status === "active" ? "활동중" : m.status}
                  </span>
                </div>
                <p className="text-sm text-slate-500">{m.fitness_goal || "목표 미입력"}</p>
                <div className="mt-2 flex gap-2">
                  <Link href={`/trainer/sessions/${m.id}`} className="flex-1">
                    <Button size="sm" variant="secondary" className="w-full">
                      세션 기록
                    </Button>
                  </Link>
                  <Link href={`/trainer/reports/${m.id}`} className="flex-1">
                    <Button size="sm" variant="secondary" className="w-full">
                      리포트
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
