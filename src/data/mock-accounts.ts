import { Account } from '@/types/account'

export const mockAccounts: Account[] = [
  {
    id: '1',
    account: 'admin',
    nickname: '超級管理員',
    password: 'admin1234',
    role: 'super_admin',
    status: 'active',
    createdAt: '2026-01-01',
  },
  {
    id: '2',
    account: 'user01',
    nickname: '張三',
    password: 'user1234',
    role: 'user',
    status: 'active',
    createdAt: '2026-01-15',
  },
  {
    id: '3',
    account: 'user02',
    nickname: '李四',
    password: 'user5678',
    role: 'user',
    status: 'active',
    createdAt: '2026-02-01',
  },
]
