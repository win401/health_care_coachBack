import type { NextConfig } from "next";

const BACKEND_ORIGIN = process.env.BACKEND_ORIGIN || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_ORIGIN}/:path*`,
      },
      {
        // 업로드된 자세 사진 등 정적 파일도 같은 오리진에서 서빙되도록 프록시한다.
        source: "/uploads/:path*",
        destination: `${BACKEND_ORIGIN}/uploads/:path*`,
      },
    ];
  },
};

export default nextConfig;
