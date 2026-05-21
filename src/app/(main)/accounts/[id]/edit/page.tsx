"use client"

import { use, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Account } from "@/types/account"
import { getAccount, updateAccount } from "@/lib/api/accounts"
import { AccountForm } from "@/components/accounts/account-form"
import { useAuth } from "@/context/auth-context"

export default function EditAccountPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [account, setAccount] = useState<Account | null>(null)
  const [loading, setLoading] = useState(true)
  const isSuperAdmin = user?.role === "super_admin"

  useEffect(() => {
    if (isLoading) return
    if (!isSuperAdmin) {
      router.replace("/products")
      return
    }
    getAccount(id).then(acc => {
      setAccount(acc || null)
      setLoading(false)
    })
  }, [id, isLoading, isSuperAdmin, router])

  if (isLoading || !isSuperAdmin || loading) return <div className="text-gray-500">載入中...</div>
  if (!account) return <div className="text-red-500">找不到帳號</div>

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">編輯帳號</h1>
      <AccountForm
        initial={account}
        isEdit
        onSubmit={(data) => updateAccount(id, data)}
      />
    </div>
  )
}
