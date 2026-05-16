import { Account, AccountFormData } from '@/types/account'
import { apiClient, ApiError } from '@/lib/api-client'

interface AccountResponse {
  id: number
  account: string
  nickname: string
  role: string
  status: string
  created_at: string | null
}

function toAccount(r: AccountResponse): Account {
  return {
    id: String(r.id),
    account: r.account,
    nickname: r.nickname,
    password: '',
    role: r.role as Account['role'],
    status: r.status as Account['status'],
    createdAt: r.created_at || '',
  }
}

export async function getAccounts(): Promise<Account[]> {
  const data = await apiClient.get<AccountResponse[]>('/api/accounts')
  return data.map(toAccount)
}

export async function getAccount(id: string): Promise<Account | undefined> {
  try {
    const data = await apiClient.get<AccountResponse>(`/api/accounts/${id}`)
    return toAccount(data)
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return undefined
    throw e
  }
}

export async function createAccount(data: AccountFormData): Promise<{ success: boolean; error?: string; account?: Account }> {
  try {
    const res = await apiClient.post<AccountResponse>('/api/accounts', {
      account: data.account,
      nickname: data.nickname,
      password: data.password,
      role: data.role,
    })
    return { success: true, account: toAccount(res) }
  } catch (e) {
    if (e instanceof ApiError) return { success: false, error: e.message }
    throw e
  }
}

export async function updateAccount(id: string, data: Partial<AccountFormData>): Promise<{ success: boolean; error?: string; account?: Account }> {
  try {
    const res = await apiClient.put<AccountResponse>(`/api/accounts/${id}`, {
      account: data.account,
      nickname: data.nickname,
      password: data.password || undefined,
      role: data.role,
    })
    return { success: true, account: toAccount(res) }
  } catch (e) {
    if (e instanceof ApiError) return { success: false, error: e.message }
    throw e
  }
}

export async function deleteAccount(id: string): Promise<{ success: boolean; error?: string }> {
  try {
    await apiClient.delete(`/api/accounts/${id}`)
    return { success: true }
  } catch (e) {
    if (e instanceof ApiError) return { success: false, error: e.message }
    throw e
  }
}

export async function toggleAccountStatus(id: string): Promise<{ success: boolean; error?: string }> {
  try {
    await apiClient.put(`/api/accounts/${id}/toggle-status`, {})
    return { success: true }
  } catch (e) {
    if (e instanceof ApiError) return { success: false, error: e.message }
    throw e
  }
}
