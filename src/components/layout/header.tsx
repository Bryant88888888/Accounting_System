"use client"

import { Globe, ChevronDown, LogOut, Settings, User } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/auth-context"

export function Header() {
  const { user, logout } = useAuth()
  const router = useRouter()

  function handleLogout() {
    logout()
    router.replace("/login")
  }

  return (
    <header className="sticky top-0 z-30 h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div />
      <div className="flex items-center gap-4">
        {/* Language Switcher */}
        <button className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 transition-colors">
          <Globe className="w-4 h-4" />
          <span>文A</span>
        </button>

        {/* User Menu */}
        <div className="relative group">
          <button className="flex items-center gap-2 text-sm text-gray-700 hover:text-gray-900 transition-colors">
            <div className="w-8 h-8 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <span className="font-medium">{user?.nickname ?? "管理員"}</span>
            <ChevronDown className="w-4 h-4" />
          </button>

          {/* Dropdown */}
          <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
            <div className="py-1">
              <a href="/profile" className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                <Settings className="w-4 h-4" />
                <span>個人設定</span>
              </a>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-gray-50 w-full text-left"
              >
                <LogOut className="w-4 h-4" />
                <span>登出</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
