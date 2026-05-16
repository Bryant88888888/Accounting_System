"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Tenant } from "@/types/tenant"
import { getTenants, deleteTenant, toggleTenantStatus } from "@/lib/api/tenants"
import { TenantTable } from "@/components/tenants/tenant-table"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTenants()
  }, [])

  async function loadTenants() {
    setLoading(true)
    try {
      const data = await getTenants()
      setTenants(data)
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("確定要刪除此租戶嗎？")) return
    const result = await deleteTenant(id)
    if (result.success) {
      await loadTenants()
    } else {
      alert(result.error || "刪除失敗")
    }
  }

  async function handleToggleStatus(id: string) {
    const result = await toggleTenantStatus(id)
    if (result.success) {
      await loadTenants()
    } else {
      alert(result.error || "操作失敗")
    }
  }

  if (loading && tenants.length === 0) {
    return <div className="text-gray-500">載入中...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">租戶管理</h1>
        <Button asChild>
          <Link href="/admin/tenants/new">
            <Plus className="w-4 h-4" />
            新增租戶
          </Link>
        </Button>
      </div>

      {tenants.length === 0 && !loading ? (
        <div className="text-center text-gray-500 py-12">尚無租戶資料</div>
      ) : (
        <TenantTable
          tenants={tenants}
          onDelete={handleDelete}
          onToggleStatus={handleToggleStatus}
        />
      )}
    </div>
  )
}
