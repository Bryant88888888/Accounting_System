"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  BarChart3,
  Building2,
  Clock,
  FileBarChart,
  LayoutDashboard,
  Package,
  UserCog,
  X,
} from "lucide-react"
import { useAuth } from "@/context/auth-context"

interface SidebarProps {
  open: boolean
  onClose: () => void
}

const tenantNav = [
  { name: "儀表盤", href: "/", icon: LayoutDashboard },
  { name: "產品管理", href: "/products", icon: Package },
  { name: "結算報表", href: "/reports/settlement", icon: FileBarChart },
  { name: "定時任務", href: "/tasks", icon: Clock },
]

const adminNav = [
  { name: "帳號管理", href: "/accounts", icon: UserCog },
  { name: "租戶管理", href: "/admin/tenants", icon: Building2 },
  { name: "統計概覽", href: "/admin/statistics", icon: BarChart3 },
]

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname()
  const { user } = useAuth()
  const isSuperAdmin = user?.role === "super_admin"

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/"
    return pathname.startsWith(href)
  }

  const navItemClass = (active: boolean) =>
    `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
      active ? "bg-[#2a2a3d] text-orange-500" : "hover:bg-[#2a2a3d] hover:text-white"
    }`

  function renderNavItem(item: (typeof tenantNav)[number]) {
    const Icon = item.icon
    const active = isActive(item.href)
    return (
      <li key={item.href}>
        <Link href={item.href} onClick={onClose} className={navItemClass(active)}>
          <Icon className="h-5 w-5 shrink-0" />
          <span className="truncate">{item.name}</span>
        </Link>
      </li>
    )
  }

  return (
    <>
      {open && (
        <button
          type="button"
          aria-label="關閉選單背景"
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen w-60 flex-col bg-[#1e1e2d] text-[#9899ac] transition-transform duration-200 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center gap-2 border-b border-[#2a2a3d] px-4 py-5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-orange-500">
            <span className="text-sm font-bold text-white">代</span>
          </div>
          <span className="truncate text-lg font-semibold text-white">代理分帳系統</span>
          <button
            type="button"
            aria-label="關閉選單"
            className="ml-auto rounded p-1 text-[#9899ac] hover:bg-[#2a2a3d] hover:text-white"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-1">
            {tenantNav.map(renderNavItem)}
          </ul>

          {isSuperAdmin && (
            <div className="mt-6">
              <div className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-[#6c6c80]">
                管理後台
              </div>
              <ul className="space-y-1">
                {adminNav.map(renderNavItem)}
              </ul>
            </div>
          )}
        </nav>
      </aside>
    </>
  )
}
