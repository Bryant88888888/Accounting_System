"use client"

import { ChevronDown, LogOut, Menu, User } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/auth-context"

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuth()
  const router = useRouter()

  function handleLogout() {
    logout()
    router.replace("/login")
  }

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-gray-200 bg-white px-4 md:px-6">
      <button
        type="button"
        aria-label="切換選單"
        onClick={onMenuClick}
        className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="relative group">
        <button className="flex items-center gap-2 text-sm text-gray-700 transition-colors hover:text-gray-900">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-orange-100 text-orange-600">
            <User className="h-4 w-4" />
          </div>
          <span className="font-medium">{user?.nickname ?? "使用者"}</span>
          <ChevronDown className="h-4 w-4" />
        </button>

        <div className="invisible absolute right-0 top-full mt-1 w-40 rounded-lg border border-gray-200 bg-white opacity-0 shadow-lg transition-all group-hover:visible group-hover:opacity-100">
          <div className="py-1">
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-50"
            >
              <LogOut className="h-4 w-4" />
              <span>登出</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
