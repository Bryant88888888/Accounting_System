"use client"

import { Tenant } from "@/types/tenant"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { Pencil, Trash2, ToggleLeft, ToggleRight } from "lucide-react"

interface TenantTableProps {
  tenants: Tenant[]
  onDelete: (id: string) => void
  onToggleStatus: (id: string) => void
}

export function TenantTable({ tenants, onDelete, onToggleStatus }: TenantTableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">帳號</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">名稱</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">電話</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">狀態</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">建立日期</th>
            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {tenants.map((t) => (
            <tr key={t.id} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3 font-medium text-gray-900">{t.account}</td>
              <td className="px-4 py-3 text-gray-600">{t.name}</td>
              <td className="px-4 py-3 text-gray-500">{t.phone || "—"}</td>
              <td className="px-4 py-3">
                <Badge
                  variant={t.status === "active" ? "default" : "secondary"}
                  className={t.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}
                >
                  {t.status === "active" ? "啟用" : "停用"}
                </Badge>
              </td>
              <td className="px-4 py-3 text-gray-500">{t.createdAt}</td>
              <td className="px-4 py-3">
                <div className="flex items-center justify-end gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onToggleStatus(t.id)}
                    title={t.status === "active" ? "停用" : "啟用"}
                  >
                    {t.status === "active"
                      ? <ToggleRight className="w-4 h-4 text-green-600" />
                      : <ToggleLeft className="w-4 h-4 text-gray-400" />
                    }
                  </Button>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/admin/tenants/${t.id}/edit`}>
                      <Pencil className="w-4 h-4" />
                    </Link>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(t.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
