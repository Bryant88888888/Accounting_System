import { Tenant, TenantFormData } from '@/types/tenant'
import { apiClient, ApiError } from '@/lib/api-client'

interface TenantResponse {
  id: number
  account: string
  name: string
  email: string | null
  phone: string | null
  note: string | null
  status: string
  created_at: string | null
}

function toTenant(r: TenantResponse): Tenant {
  return {
    id: String(r.id),
    account: r.account,
    name: r.name,
    email: r.email,
    phone: r.phone,
    note: r.note,
    status: r.status as Tenant['status'],
    createdAt: r.created_at || '',
  }
}

export async function getTenants(): Promise<Tenant[]> {
  const data = await apiClient.get<TenantResponse[]>('/api/tenants')
  return data.map(toTenant)
}

export async function getTenant(id: string): Promise<Tenant | undefined> {
  try {
    const data = await apiClient.get<TenantResponse>(`/api/tenants/${id}`)
    return toTenant(data)
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return undefined
    throw e
  }
}

export async function createTenant(data: TenantFormData): Promise<{ success: boolean; error?: string; tenant?: Tenant }> {
  try {
    const res = await apiClient.post<TenantResponse>('/api/tenants', {
      account: data.account,
      name: data.name,
      password: data.password,
      email: data.email || undefined,
      phone: data.phone || undefined,
      note: data.note || undefined,
    })
    return { success: true, tenant: toTenant(res) }
  } catch (e) {
    if (e instanceof ApiError) return { success: false, error: e.message }
    throw e
  }
}

export async function updateTenant(id: string, data: Partial<TenantFormData>): Promise<{ success: boolean; error?: string; tenant?: Tenant }> {
  try {
    const res = await apiClient.put<TenantResponse>(`/api/tenants/${id}`, {
      account: data.account,
      name: data.name,
      password: data.password || undefined,
      email: data.email || undefined,
      phone: data.phone || undefined,
      note: data.note || undefined,
    })
    return { success: true, tenant: toTenant(res) }
  } catch (e) {
    if (e instanceof ApiError) return { success: false, error: e.message }
    throw e
  }
}

export async function deleteTenant(id: string): Promise<{ success: boolean; error?: string }> {
  try {
    await apiClient.delete(`/api/tenants/${id}`)
    return { success: true }
  } catch (e) {
    if (e instanceof ApiError) return { success: false, error: e.message }
    throw e
  }
}

export async function toggleTenantStatus(id: string): Promise<{ success: boolean; error?: string }> {
  try {
    await apiClient.put(`/api/tenants/${id}/toggle-status`, {})
    return { success: true }
  } catch (e) {
    if (e instanceof ApiError) return { success: false, error: e.message }
    throw e
  }
}
