/**
 * 백엔드 호출 공용 fetch 래퍼.
 *
 * next.config.ts의 rewrites()가 /api/* 를 FastAPI(BACKEND_ORIGIN)로 프록시하기 때문에,
 * 브라우저 입장에서는 항상 같은 오리진(:3000)과만 통신한다. 그래야 FastAPI가 내려주는
 * httpOnly 쿠키가 프론트엔드와 같은 도메인 쿠키로 저장되어 서버 컴포넌트에서도 읽을 수 있다.
 */

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // ignore json parse error
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: body !== undefined ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
  postForm: <T>(path: string, formData: FormData) =>
    fetch(`/api${path}`, { method: "POST", credentials: "include", body: formData }).then(async (res) => {
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new ApiError(res.status, data.detail || res.statusText);
      }
      return (await res.json()) as T;
    }),
};
