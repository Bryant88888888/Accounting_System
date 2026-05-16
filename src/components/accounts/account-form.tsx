"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Account, AccountFormData } from "@/types/account"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface AccountFormProps {
  initial?: Account
  onSubmit: (data: AccountFormData) => Promise<{ success: boolean; error?: string }>
  isEdit?: boolean
}

export function AccountForm({ initial, onSubmit, isEdit }: AccountFormProps) {
  const router = useRouter()
  const [form, setForm] = useState<AccountFormData>({
    account: initial?.account || "",
    nickname: initial?.nickname || "",
    password: "",
    role: initial?.role || "user",
  })
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  function set(field: keyof AccountFormData, value: string) {
    setForm(prev => ({ ...prev, [field]: value } as AccountFormData))
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
      router.push("/accounts")
    } else {
      setError(result.error || "發生錯誤")
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 max-w-md">
      <div className="space-y-1.5">
        <Label htmlFor="account">帳號</Label>
        <Input
          id="account"
          value={form.account}
          onChange={e => set("account", e.target.value)}
          required
          placeholder="登入帳號"
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="nickname">暱稱</Label>
        <Input
          id="nickname"
          value={form.nickname}
          onChange={e => set("nickname", e.target.value)}
          required
          placeholder="顯示名稱"
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="password">
          密碼{isEdit && <span className="text-gray-400 text-xs ml-1">（空白不修改）</span>}
        </Label>
        <Input
          id="password"
          type="password"
          value={form.password}
          onChange={e => set("password", e.target.value)}
          placeholder={isEdit ? "留空不修改" : "請輸入密碼"}
        />
      </div>

      <div className="space-y-1.5">
        <Label>角色</Label>
        <Select value={form.role} onValueChange={v => set("role", v)}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="user">一般用戶</SelectItem>
            <SelectItem value="super_admin">超級管理者</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</p>
      )}

      <div className="flex gap-3 pt-2">
        <Button type="submit" disabled={submitting}>
          {submitting ? "儲存中..." : isEdit ? "儲存變更" : "新增帳號"}
        </Button>
        <Button type="button" variant="outline" onClick={() => router.push("/accounts")}>
          取消
        </Button>
      </div>
    </form>
  )
}
