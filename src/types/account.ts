export type AccountRole = 'super_admin' | 'user'

export interface Account {
  id: string
  account: string      // 唯一
  nickname: string     // 唯一
  password: string
  role: AccountRole
  status: 'active' | 'inactive'
  createdAt: string
}

export type AccountFormData = Omit<Account, 'id' | 'createdAt' | 'status'>
