import { cookies } from "next/headers";

const BACKEND_ORIGIN = process.env.BACKEND_ORIGIN || "http://127.0.0.1:8000";

export type CurrentUser = {
  id: number;
  name: string;
  role: "trainer" | "member";
};

/**
 * 서버 컴포넌트/레이아웃에서 로그인 상태를 확인할 때 사용한다.
 * access_token 쿠키를 백엔드로 그대로 전달해 /auth/me를 호출한다.
 */
export async function getCurrentUser(): Promise<CurrentUser | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token");
  if (!token) return null;

  try {
    const res = await fetch(`${BACKEND_ORIGIN}/auth/me`, {
      headers: { Cookie: `access_token=${token.value}` },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as CurrentUser;
  } catch {
    return null;
  }
}
