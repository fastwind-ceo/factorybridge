export function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
  }

  return 'http://localhost:8000/api/v1';
}

export const API_BASE_URL = getApiBaseUrl();

type ApiMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE';

function buildHeaders(token?: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function normalizeApiError(payload: unknown): string {
  if (typeof payload === 'string') {
    return payload;
  }

  if (payload && typeof payload === 'object' && 'detail' in payload) {
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === 'string') {
      return detail;
    }
    return JSON.stringify(detail);
  }

  return JSON.stringify(payload);
}

async function parseApiResponse<T>(response: Response, path: string): Promise<T> {
  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(`API ${path} failed with ${response.status}: ${normalizeApiError(payload)}`);
  }

  return payload as T;
}

export async function apiRequest<T>(method: ApiMethod, path: string, body?: unknown, token?: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method,
    headers: buildHeaders(token),
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: 'no-store',
  });

  return parseApiResponse<T>(response, path);
}

export async function apiGet<T>(path: string, token?: string): Promise<T> {
  return apiRequest<T>('GET', path, undefined, token);
}

export async function apiPost<T>(path: string, body: unknown, token?: string): Promise<T> {
  return apiRequest<T>('POST', path, body, token);
}

export async function apiPatch<T>(path: string, body: unknown, token?: string): Promise<T> {
  return apiRequest<T>('PATCH', path, body, token);
}

export async function apiDelete<T>(path: string, token?: string): Promise<T> {
  return apiRequest<T>('DELETE', path, undefined, token);
}
