"use client"

import { TenantForm } from "@/components/tenants/tenant-form"
import { createTenant } from "@/lib/api/tenants"

export default function NewTenantPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">新增租戶</h1>
      <TenantForm onSubmit={createTenant} />
    </div>
  )
}
