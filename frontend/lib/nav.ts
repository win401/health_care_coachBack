export type NavItem = {
  href: string;
  label: string;
  icon: "home" | "users" | "clipboard" | "file" | "target" | "calendar" | "chart";
};

export const trainerNavItems: NavItem[] = [
  { href: "/trainer/dashboard", label: "홈", icon: "home" },
  { href: "/trainer/members", label: "회원", icon: "users" },
  { href: "/trainer/sessions", label: "세션", icon: "clipboard" },
  { href: "/trainer/reports", label: "리포트", icon: "file" },
];

export const memberNavItems: NavItem[] = [
  { href: "/member", label: "홈", icon: "home" },
  { href: "/member/assignments", label: "과제", icon: "target" },
  { href: "/member/schedule", label: "일정", icon: "calendar" },
  { href: "/member/progress", label: "변화기록", icon: "chart" },
];
