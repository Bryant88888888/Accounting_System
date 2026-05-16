export interface Tenant {
  id: string
  account: string
  name: string
  email: string | null
  phone: string | null
  note: string | null
  status: 'active' | 'inactive'
  createdAt: string
}

export type TenantFormData = {
  account: string
  name: string
  password: string
  email: string
  phone: string
  note: string
}
