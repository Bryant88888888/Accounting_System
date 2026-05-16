"use client"

import { useEffect, useState } from "react"
import { use } from "react"
import { Account } from "@/types/account"
import { getAccount, updateAccount } from "@/lib/api/accounts"
import { AccountForm } from "@/components/accounts/account-form"

export default function EditAccountPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const [account, setAccount] = useState<Account | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAccount(id).then(acc => {
      setAccount(acc || null)
      setLoading(false)
    })
  }, [id])

  if (loading) return <div className="text-gray-500">載入中...</div>
  if (!account) return <div className="text-red-500">找不到帳號</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">編輯帳號</h1>
      <AccountForm
        initial={account}
        isEdit
        onSubmit={(data) => updateAccount(id, data)}
      />
    </div>
  )
}
