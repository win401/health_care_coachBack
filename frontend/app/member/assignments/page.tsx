import { serverGet } from "@/lib/server-api";
import type { Assignment } from "@/lib/types";
import { AssignmentsClient } from "@/components/member/assignments-client";

export default async function MemberAssignmentsPage() {
  const assignments = (await serverGet<Assignment[]>("/my/assignments")) || [];

  return (
    <div className="flex flex-col gap-4 p-4">
      <h1 className="text-xl font-bold text-slate-900">내 과제</h1>
      <AssignmentsClient assignments={assignments} />
    </div>
  );
}
