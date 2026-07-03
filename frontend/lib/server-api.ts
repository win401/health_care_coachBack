import { cookies } from "next/headers";

const BACKEND_ORIGIN = process.env.BACKEND_ORIGIN || "http://127.0.0.1:8000";

/**
 * 서버 컴포넌트 전용 GET 헬퍼. 로그인 쿠키를 백엔드로 그대로 전달한다.
 * 실패 시(404 등) null을 반환하므로 호출부에서 존재 여부를 처리한다.
 */
export async function serverGet<T>(path: string): Promise<T | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token");

  const res = await fetch(`${BACKEND_ORIGIN}${path}`, {
    headers: token ? { Cookie: `access_token=${token.value}` } : {},
    cache: "no-store",
  });

  if (!res.ok) return null;
  return (await res.json()) as T;
}
