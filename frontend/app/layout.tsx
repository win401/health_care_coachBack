import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FitNote Trainer",
  description: "PT 트레이너용 회원 관리 · 자세 분석 · 리포트 서비스",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900">{children}</body>
    </html>
  );
}
