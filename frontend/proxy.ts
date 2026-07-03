import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * /trainer, /member 하위 경로에 대한 1차 접근 가드.
 * 여기서는 쿠키 존재 여부만 빠르게 확인하고, 실제 role 검증(트레이너/회원 구분)은
 * 각 영역의 layout.tsx에서 getCurrentUser()로 백엔드에 재확인한다.
 * (Next.js 권장: Proxy 단독으로 인증을 신뢰하지 말고 레이아웃/서버 함수에서 재검증)
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = pathname.startsWith("/trainer") || pathname.startsWith("/member");
  if (!isProtected) {
    return NextResponse.next();
  }

  const token = request.cookies.get("access_token");
  if (!token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/trainer/:path*", "/member/:path*"],
};
