"use client"

import { AccountForm } from "@/components/accounts/account-form"
import { createAccount } from "@/lib/api/accounts"

export default function NewAccountPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">新增帳號</h1>
      <AccountForm onSubmit={createAccount} />
    </div>
  )
}
