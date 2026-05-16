"use client"

import { useEffect, useState } from "react"
import { use } from "react"
import { Tenant } from "@/types/tenant"
import { getTenant, updateTenant } from "@/lib/api/tenants"
import { TenantForm } from "@/components/tenants/tenant-form"

export default function EditTenantPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const [tenant, setTenant] = useState<Tenant | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getTenant(id).then(t => {
      setTenant(t || null)
      setLoading(false)
    })
  }, [id])

  if (loading) return <div className="text-gray-500">載入中...</div>
  if (!tenant) return <div className="text-red-500">找不到租戶</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">編輯租戶</h1>
      <TenantForm
        initial={tenant}
        isEdit
        onSubmit={(data) => updateTenant(id, data)}
      />
    </div>
  )
}
