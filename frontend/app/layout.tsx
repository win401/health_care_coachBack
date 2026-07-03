import type { Metadata } from "next";
import { Anton, Archivo, Gothic_A1, Space_Grotesk, Space_Mono } from "next/font/google";
import { AccentThemeProvider } from "@/components/accent-theme-provider";
import "./globals.css";

const anton = Anton({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-anton",
  display: "swap",
});

const gothicA1 = Gothic_A1({
  subsets: ["latin"],
  weight: ["700", "800"],
  variable: "--font-gothic-a1",
  display: "swap",
  preload: false,
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
});

const archivo = Archivo({
  subsets: ["latin"],
  variable: "--font-archivo",
  display: "swap",
});

const spaceMono = Space_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-space-mono",
  display: "swap",
});

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
    <html
      lang="ko"
      className={`h-full antialiased ${anton.variable} ${gothicA1.variable} ${spaceGrotesk.variable} ${archivo.variable} ${spaceMono.variable}`}
    >
      <body className="flex min-h-full flex-col bg-background text-foreground">
        <AccentThemeProvider />
        {children}
      </body>
    </html>
  );
}
