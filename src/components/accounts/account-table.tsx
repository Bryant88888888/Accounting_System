"use client"

import { Account } from "@/types/account"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { Pencil, Trash2, ToggleLeft, ToggleRight } from "lucide-react"

interface AccountTableProps {
  accounts: Account[]
  onDelete: (id: string) => void
  onToggleStatus: (id: string) => void
}

const roleLabel: Record<string, string> = {
  super_admin: "超級管理者",
  user: "一般用戶",
}

export function AccountTable({ accounts, onDelete, onToggleStatus }: AccountTableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">帳號</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">暱稱</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">角色</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">狀態</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">建立日期</th>
            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {accounts.map((acc) => (
            <tr key={acc.id} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3 font-medium text-gray-900">{acc.account}</td>
              <td className="px-4 py-3 text-gray-600">{acc.nickname}</td>
              <td className="px-4 py-3">
                <Badge variant={acc.role === "super_admin" ? "default" : "secondary"}>
                  {roleLabel[acc.role] || acc.role}
                </Badge>
              </td>
              <td className="px-4 py-3">
                <Badge variant={acc.status === "active" ? "default" : "secondary"}
                  className={acc.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}>
                  {acc.status === "active" ? "啟用" : "停用"}
                </Badge>
              </td>
              <td className="px-4 py-3 text-gray-500">{acc.createdAt}</td>
              <td className="px-4 py-3">
                <div className="flex items-center justify-end gap-2">
                  {acc.role !== "super_admin" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onToggleStatus(acc.id)}
                      title={acc.status === "active" ? "停用" : "啟用"}
                    >
                      {acc.status === "active"
                        ? <ToggleRight className="w-4 h-4 text-green-600" />
                        : <ToggleLeft className="w-4 h-4 text-gray-400" />
                      }
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/accounts/${acc.id}/edit`}>
                      <Pencil className="w-4 h-4" />
                    </Link>
                  </Button>
                  {acc.role !== "super_admin" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(acc.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
