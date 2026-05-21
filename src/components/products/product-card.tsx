"use client"

import { useState } from "react"
import Link from "next/link"
import { Product } from "@/types/product"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { testConnection, fetchPlayerMetrics, PlayerMetrics } from "@/lib/api/products"
import { ApiError } from "@/lib/api-client"

interface ProductCardProps {
  product: Product
  onDelete: (id: string) => void
}

interface Toast {
  id: number
  message: string
  type: "success" | "error"
}

export function ProductCard({ product, onDelete }: ProductCardProps) {
  const [testLoading, setTestLoading] = useState(false)
  const [fetchLoading, setFetchLoading] = useState(false)
  const [toasts, setToasts] = useState<Toast[]>([])
  const [reportOpen, setReportOpen] = useState(false)
  const [reportData, setReportData] = useState<PlayerMetrics | null>(null)

  const hasCrawler = !!product.crawlerType
  const hasCredentials = !!product.account
  const disabledTitle = !hasCrawler
    ? "尚未設定查帳平台"
    : !hasCredentials
      ? "請先編輯並填入帳號密碼"
      : undefined

  function addToast(message: string, type: "success" | "error") {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000)
  }

  async function handleTestConnection() {
    setTestLoading(true)
    try {
      const res = await testConnection(product.id)
      addToast(res.message, res.success ? "success" : "error")
    } catch (error) {
      addToast(error instanceof ApiError ? error.message : "測試連線失敗", "error")
    } finally {
      setTestLoading(false)
    }
  }

  async function handleFetchReport() {
    setFetchLoading(true)
    try {
      const res = await fetchPlayerMetrics(product.id)
      if (res.success && res.data) {
        setReportData(res.data)
        setReportOpen(true)
      } else {
        addToast(res.error || "查詢帳務失敗", "error")
      }
    } catch (error) {
      addToast(error instanceof ApiError ? error.message : "查詢帳務失敗", "error")
    } finally {
      setFetchLoading(false)
    }
  }

  return (
    <>
      <div className="fixed top-4 right-4 z-50 flex w-[calc(100vw-2rem)] max-w-sm flex-col gap-2 pointer-events-none">
        {toasts.map(t => (
          <div
            key={t.id}
            className={`rounded-lg px-4 py-2 text-sm text-white shadow-lg pointer-events-auto ${
              t.type === "success" ? "bg-green-600" : "bg-red-600"
            }`}
          >
            {t.message}
          </div>
        ))}
      </div>

      {reportOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setReportOpen(false)} />
          <div className="relative z-50 flex max-h-[80vh] w-full max-w-2xl flex-col rounded-lg bg-white shadow-xl">
            <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4">
              <h2 className="text-base font-semibold text-gray-900">帳務查詢：{product.name}</h2>
              <button
                onClick={() => setReportOpen(false)}
                className="text-xl leading-none text-gray-400 hover:text-gray-600"
                aria-label="關閉"
              >
                ×
              </button>
            </div>
            <div className="flex-1 overflow-auto p-5">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="rounded border border-gray-200 p-4">
                  <div className="mb-1 text-xs text-gray-500">玩家有效投注</div>
                  <div className="text-xl font-semibold text-gray-900">
                    {reportData?.player_valid_bet.toLocaleString()}
                  </div>
                </div>
                <div className="rounded border border-gray-200 p-4">
                  <div className="mb-1 text-xs text-gray-500">玩家輸贏 / 未拆帳</div>
                  <div className="text-xl font-semibold text-gray-900">
                    {reportData?.player_win_loss.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex min-w-0 flex-col rounded-lg border border-gray-200 bg-white p-4">
        <div className="mb-1 flex items-start justify-between gap-3">
          <h3 className="min-w-0 break-words text-base font-bold text-gray-900">{product.name}</h3>
          <Badge variant={product.status === "active" ? "success" : "secondary"} className="shrink-0 text-xs">
            {product.status === "active" ? "啟用" : "停用"}
          </Badge>
        </div>

        <p className="mb-3 text-sm text-gray-500">{product.series}</p>

        <div className="flex-1 space-y-2 text-sm">
          <div className="flex justify-between gap-4">
            <span className="shrink-0 text-gray-500">帳號</span>
            <span className="min-w-0 break-words text-right text-gray-900">{product.account || "未設定"}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="shrink-0 text-gray-500">平台</span>
            <span className="min-w-0 break-words text-right text-gray-900">{product.crawlerType ?? "未設定"}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="shrink-0 text-gray-500">上手</span>
            <span className="min-w-0 break-words text-right text-gray-900">
              {product.upstream ? `${product.upstream.name} ${product.upstream.percentage}%` : "-"}
            </span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="shrink-0 text-gray-500">下手</span>
            <span className="text-gray-900">{product.downstreams.length} 個</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="shrink-0 text-gray-500">建立時間</span>
            <span className="text-right text-gray-900">{product.createdAt}</span>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 border-t border-gray-100 pt-3 sm:grid-cols-4">
          <Button
            variant="outline"
            size="sm"
            className="w-full min-w-0 text-xs"
            disabled={!hasCrawler || testLoading}
            title={disabledTitle}
            onClick={handleTestConnection}
          >
            {testLoading ? "測試中..." : "測試連線"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="w-full min-w-0 text-xs"
            disabled={!hasCrawler || fetchLoading}
            title={disabledTitle}
            onClick={handleFetchReport}
          >
            {fetchLoading ? "查詢中..." : "查詢帳務"}
          </Button>
          <Button variant="outline" size="sm" className="w-full min-w-0 text-xs" asChild>
            <Link href={`/products/${product.id}/edit`}>編輯</Link>
          </Button>
          <Button
            variant="destructive"
            size="sm"
            className="w-full min-w-0 text-xs"
            onClick={() => onDelete(product.id)}
          >
            刪除
          </Button>
        </div>
      </div>
    </>
  )
}
