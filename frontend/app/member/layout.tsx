import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { BottomNav } from "@/components/bottom-nav";
import { memberNavItems } from "@/lib/nav";

export default async function MemberLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }
  if (user.role !== "member") {
    redirect("/trainer/dashboard");
  }

  return (
    <div className="flex min-h-screen w-full flex-col bg-black md:bg-background">
      <main className="mx-auto w-full max-w-md flex-1 pb-20 md:pb-28">{children}</main>
      <BottomNav items={memberNavItems} />
    </div>
  );
}
