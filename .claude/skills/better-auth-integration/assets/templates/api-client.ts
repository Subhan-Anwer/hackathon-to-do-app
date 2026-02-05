// lib/api.ts - Frontend API Client Template
const API_BASE = "/api/proxy"

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: any
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { body, ...restOptions } = options

  const config: RequestInit = {
    ...restOptions,
    credentials: "include", // CRITICAL: Sends cookies to proxy
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  }

  if (body) {
    config.body = JSON.stringify(body)
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }))
    throw new Error(error.error || `API error: ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Generic request method
  request,

  // Example methods - customize for your API
  get: <T>(endpoint: string) => request<T>(endpoint, { method: "GET" }),

  post: <T>(endpoint: string, data: any) =>
    request<T>(endpoint, { method: "POST", body: data }),

  put: <T>(endpoint: string, data: any) =>
    request<T>(endpoint, { method: "PUT", body: data }),

  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: "DELETE" }),

  patch: <T>(endpoint: string, data: any) =>
    request<T>(endpoint, { method: "PATCH", body: data }),
}
