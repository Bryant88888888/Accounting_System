import { apiClient } from "@/lib/api-client"
import { AuthUser } from "@/types/auth"

interface LoginResponse {
  access_token: string
  token_type: string
  account: AuthUser
}

export async function loginApi(account: string, password: string): Promise<LoginResponse> {
  return apiClient.post<LoginResponse>("/api/auth/login", { account, password })
}

export async function getMeApi(): Promise<AuthUser> {
  return apiClient.get<AuthUser>("/api/auth/me")
}
