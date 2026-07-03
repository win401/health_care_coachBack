import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { DesktopSidebar } from "@/components/desktop-sidebar";
import { BottomNav } from "@/components/bottom-nav";
import { MobileHeader } from "@/components/mobile-header";
import { trainerNavItems } from "@/lib/nav";

export default async function TrainerLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }
  if (user.role !== "trainer") {
    redirect("/member");
  }

  return (
    <div className="flex min-h-screen w-full">
      <DesktopSidebar items={trainerNavItems} title="FitNote Trainer" userName={`${user.name} 트레이너`} />
      <div className="flex min-h-screen flex-1 flex-col">
        <MobileHeader title="FitNote Trainer" userName={`${user.name} 트레이너`} />
        <main className="flex-1 pb-20 md:pb-0">{children}</main>
        <BottomNav items={trainerNavItems} />
      </div>
    </div>
  );
}
