import type {
  AssessmentResult,
  InterestRoundResponse,
  InterestSubmitRequest,
  InterestSubmitResponse,
  ResponseItem,
  SessionCreated,
} from "./types"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail ?? "请求失败")
  }
  return res.json() as Promise<T>
}

export async function createSession(): Promise<SessionCreated> {
  return request<SessionCreated>("/api/v1/sessions", { method: "POST" })
}

export async function getNextInterestRound(sessionId: string): Promise<InterestRoundResponse> {
  return request<InterestRoundResponse>(`/api/v1/sessions/${sessionId}/interest/next`)
}

export async function submitInterestRound(
  sessionId: string,
  body: InterestSubmitRequest
): Promise<InterestSubmitResponse> {
  return request<InterestSubmitResponse>(`/api/v1/sessions/${sessionId}/interest`, {
    method: "POST",
    body: JSON.stringify(body),
  })
}

export async function submitResponses(
  sessionId: string,
  responses: ResponseItem[]
): Promise<void> {
  await fetch(`${BASE_URL}/api/v1/sessions/${sessionId}/responses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ responses }),
  })
}

export async function completeSession(sessionId: string): Promise<AssessmentResult> {
  return request<AssessmentResult>(`/api/v1/sessions/${sessionId}/complete`, { method: "POST" })
}

export async function getResult(sessionId: string): Promise<AssessmentResult> {
  return request<AssessmentResult>(`/api/v1/sessions/${sessionId}/result`)
}
