"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { AccountForm } from "@/components/accounts/account-form"
import { createAccount } from "@/lib/api/accounts"
import { useAuth } from "@/context/auth-context"

export default function NewAccountPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const isSuperAdmin = user?.role === "super_admin"

  useEffect(() => {
    if (!isLoading && !isSuperAdmin) router.replace("/products")
  }, [isLoading, isSuperAdmin, router])

  if (isLoading || !isSuperAdmin) return <div className="text-gray-500">載入中...</div>

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">新增帳號</h1>
      <AccountForm onSubmit={createAccount} />
    </div>
  )
}
