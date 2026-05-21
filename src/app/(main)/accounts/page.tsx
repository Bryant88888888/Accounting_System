"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Plus } from "lucide-react"
import { Account } from "@/types/account"
import { getAccounts, deleteAccount, toggleAccountStatus } from "@/lib/api/accounts"
import { AccountTable } from "@/components/accounts/account-table"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/auth-context"

export default function AccountsPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const isSuperAdmin = user?.role === "super_admin"

  useEffect(() => {
    if (isLoading) return
    if (!isSuperAdmin) {
      router.replace("/products")
      return
    }
    loadAccounts()
  }, [isLoading, isSuperAdmin, router])

  async function loadAccounts() {
    setLoading(true)
    try {
      const data = await getAccounts()
      setAccounts(data)
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("確定要刪除此帳號嗎？")) return
    const result = await deleteAccount(id)
    if (result.success) {
      await loadAccounts()
    } else {
      alert(result.error || "刪除失敗")
    }
  }

  async function handleToggleStatus(id: string) {
    const result = await toggleAccountStatus(id)
    if (result.success) {
      await loadAccounts()
    } else {
      alert(result.error || "切換狀態失敗")
    }
  }

  if (isLoading || !isSuperAdmin || (loading && accounts.length === 0)) {
    return <div className="text-gray-500">載入中...</div>
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">帳號管理</h1>
        <Button asChild>
          <Link href="/accounts/new">
            <Plus className="h-4 w-4" />
            新增帳號
          </Link>
        </Button>
      </div>

      {accounts.length === 0 && !loading ? (
        <div className="py-12 text-center text-gray-500">尚無帳號資料</div>
      ) : (
        <AccountTable
          accounts={accounts}
          onDelete={handleDelete}
          onToggleStatus={handleToggleStatus}
        />
      )}
    </div>
  )
}
