"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Tenant, TenantFormData } from "@/types/tenant"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Eye, EyeOff } from "lucide-react"

interface TenantFormProps {
  initial?: Tenant
  onSubmit: (data: TenantFormData) => Promise<{ success: boolean; error?: string }>
  isEdit?: boolean
}

export function TenantForm({ initial, onSubmit, isEdit }: TenantFormProps) {
  const router = useRouter()
  const [form, setForm] = useState<TenantFormData>({
    account: initial?.account || "",
    name: initial?.name || "",
    password: "",
    email: initial?.email || "",
    phone: initial?.phone || "",
    note: initial?.note || "",
  })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  function set(field: keyof TenantFormData, value: string) {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isEdit && !form.password) {
      setError("請輸入密碼")
      return
    }
    setSubmitting(true)
    setError("")
    const result = await onSubmit(form)
    setSubmitting(false)
    if (result.success) {
      router.push("/admin/tenants")
    } else {
      setError(result.error || "發生錯誤")
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 max-w-md">
      <div className="space-y-1.5">
        <Label htmlFor="account">登入帳號</Label>
        <Input
          id="account"
          value={form.account}
          onChange={e => set("account", e.target.value)}
          required
          placeholder="租戶登入帳號"
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="name">顯示名稱</Label>
        <Input
          id="name"
          value={form.name}
          onChange={e => set("name", e.target.value)}
          required
          placeholder="租戶名稱"
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="password">
          密碼{isEdit && <span className="text-gray-400 text-xs ml-1">（空白不修改）</span>}
        </Label>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? "text" : "password"}
            value={form.password}
            onChange={e => set("password", e.target.value)}
            placeholder={isEdit ? "留空不修改" : "請輸入密碼"}
            className="pr-10"
          />
          <button
            type="button"
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            onClick={() => setShowPassword(v => !v)}
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="email">Email <span className="text-gray-400 text-xs">（選填）</span></Label>
        <Input
          id="email"
          type="email"
          value={form.email}
          onChange={e => set("email", e.target.value)}
          placeholder="tenant@example.com"
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="phone">電話 <span className="text-gray-400 text-xs">（選填）</span></Label>
        <Input
          id="phone"
          value={form.phone}
          onChange={e => set("phone", e.target.value)}
          placeholder="0912-345-678"
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="note">備註 <span className="text-gray-400 text-xs">（選填）</span></Label>
        <textarea
          id="note"
          value={form.note}
          onChange={e => set("note", e.target.value)}
          placeholder="備註說明..."
          rows={3}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 resize-none"
        />
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</p>
      )}

      <div className="flex gap-3 pt-2">
        <Button type="submit" disabled={submitting}>
          {submitting ? "儲存中..." : isEdit ? "儲存變更" : "新增租戶"}
        </Button>
        <Button type="button" variant="outline" onClick={() => router.push("/admin/tenants")}>
          取消
        </Button>
      </div>
    </form>
  )
}
