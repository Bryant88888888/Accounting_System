"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Users,
  Package,
  FileBarChart,
  Clock,
  Bell,
  User,
  Building2,
  BarChart3,
  UserCog,
} from "lucide-react"

const mainNav = [
  { name: "儀表盤", href: "/", icon: LayoutDashboard },
  { name: "帳號管理", href: "/accounts", icon: UserCog },
  { name: "夥伴管理", href: "/partners", icon: Users },
  { name: "產品管理", href: "/products", icon: Package },
  { name: "結算報表", href: "/reports/settlement", icon: FileBarChart },
  { name: "定時任務", href: "/tasks", icon: Clock },
  { name: "推播設定", href: "/notifications", icon: Bell },
  { name: "個人資訊", href: "/profile", icon: User },
]

const adminNav = [
  { name: "租戶管理", href: "/admin/tenants", icon: Building2 },
  { name: "統計概覽", href: "/admin/statistics", icon: BarChart3 },
]

export function Sidebar() {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/"
    return pathname.startsWith(href)
  }

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-60 bg-[#1e1e2d] text-[#9899ac] flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-5 border-b border-[#2a2a3d]">
        <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">代</span>
        </div>
        <span className="text-white font-semibold text-lg">代理分帳系統</span>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="space-y-1">
          {mainNav.map((item) => {
            const Icon = item.icon
            const active = isActive(item.href)
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    active
                      ? "text-orange-500 bg-[#2a2a3d]"
                      : "hover:bg-[#2a2a3d] hover:text-white"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              </li>
            )
          })}
        </ul>

        {/* Admin Section */}
        <div className="mt-6">
          <div className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-[#6c6c80]">
            管理後台
          </div>
          <ul className="space-y-1">
            {adminNav.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                      active
                        ? "text-orange-500 bg-[#2a2a3d]"
                        : "hover:bg-[#2a2a3d] hover:text-white"
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.name}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>
      </nav>
    </aside>
  )
}
