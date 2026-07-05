import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { DesktopSidebar } from "@/components/desktop-sidebar";
import { BottomNav } from "@/components/bottom-nav";
import { MobileHeader } from "@/components/mobile-header";
import { TrainerTopBar } from "@/components/trainer/trainer-top-bar";
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
    <div className="min-h-screen w-full">
      <DesktopSidebar items={trainerNavItems} title="FitNote Trainer" userName={`${user.name} 트레이너`} />
      <div className="min-h-screen md:pl-[112px]">
        <MobileHeader title="FitNote Trainer" userName={`${user.name} 트레이너`} />
        <div className="hidden md:block">
          <TrainerTopBar userName={`${user.name} 트레이너`} />
        </div>
        <main className="pb-28 md:pb-36">{children}</main>
        <BottomNav items={trainerNavItems} />
      </div>
    </div>
  );
}
