import Link from "next/link";
import { serverGet } from "@/lib/server-api";
import type { Member } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default async function ReportsListPage() {
  const members = (await serverGet<Member[]>("/members")) || [];

  return (
    <div className="flex flex-col gap-4 p-4 md:p-6">
      <h1 className="text-xl font-bold text-slate-900">회원 리포트</h1>
      <p className="text-sm text-slate-500">회원을 선택해 리포트를 생성하거나 지난 리포트를 확인하세요.</p>

      {members.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-slate-400">
            등록된 회원이 없습니다
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {members.map((m) => (
            <Card key={m.id}>
              <CardContent className="flex flex-col gap-2 py-4">
                <p className="text-base font-semibold text-slate-900">{m.name}</p>
                <Link href={`/trainer/reports/${m.id}`}>
                  <Button size="sm" className="mt-1 w-full">
                    리포트 보기
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
