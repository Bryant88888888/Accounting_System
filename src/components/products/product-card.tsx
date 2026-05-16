"use client"

import { useState } from "react"
import Link from "next/link"
import { Product } from "@/types/product"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { testConnection, fetchReport } from "@/lib/api/products"

interface ProductCardProps {
  product: Product
  onDelete: (id: string) => void
}

interface Toast {
  id: number
  message: string
  type: 'success' | 'error'
}

export function ProductCard({ product, onDelete }: ProductCardProps) {
  const [testLoading, setTestLoading] = useState(false)
  const [fetchLoading, setFetchLoading] = useState(false)
  const [toasts, setToasts] = useState<Toast[]>([])
  const [reportOpen, setReportOpen] = useState(false)
  const [reportData, setReportData] = useState<unknown>(null)

  const hasCrawler = !!product.crawlerType

  function addToast(message: string, type: 'success' | 'error') {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000)
  }

  async function handleTestConnection() {
    setTestLoading(true)
    try {
      const res = await testConnection(product.id)
      addToast(res.message, res.success ? 'success' : 'error')
    } catch {
      addToast('連線失敗，請確認後端服務', 'error')
    } finally {
      setTestLoading(false)
    }
  }

  async function handleFetchReport() {
    setFetchLoading(true)
    try {
      const res = await fetchReport(product.id)
      if (res.success) {
        setReportData(res.data)
        setReportOpen(true)
      } else {
        addToast(res.error || '抓取失敗', 'error')
      }
    } catch {
      addToast('請求失敗，請確認後端服務', 'error')
    } finally {
      setFetchLoading(false)
    }
  }

  return (
    <>
      {/* Toast notifications */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map(t => (
          <div
            key={t.id}
            className={`px-4 py-2 rounded-lg text-white text-sm shadow-lg transition-all pointer-events-auto ${
              t.type === 'success' ? 'bg-green-600' : 'bg-red-600'
            }`}
          >
            {t.message}
          </div>
        ))}
      </div>

      {/* Report Dialog */}
      {reportOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setReportOpen(false)}
          />
          <div className="relative z-50 bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
              <h2 className="text-base font-semibold text-gray-900">
                報表資料 — {product.name}
              </h2>
              <button
                onClick={() => setReportOpen(false)}
                className="text-gray-400 hover:text-gray-600 text-xl leading-none"
              >
                ×
              </button>
            </div>
            <div className="overflow-auto p-5 flex-1">
              <pre className="text-xs text-gray-700 whitespace-pre-wrap break-all bg-gray-50 rounded p-3">
                {JSON.stringify(reportData, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-lg p-4 flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between mb-1">
          <h3 className="font-bold text-base text-gray-900">{product.name}</h3>
          <Badge variant={product.status === 'active' ? 'success' : 'secondary'} className="text-xs">
            {product.status === 'active' ? '啟用' : '停用'}
          </Badge>
        </div>

        {/* Subtitle */}
        <p className="text-sm text-gray-500 mb-3">{product.series}</p>

        {/* Info rows */}
        <div className="space-y-2 text-sm flex-1">
          <div className="flex justify-between">
            <span className="text-gray-500">帳號</span>
            <span className="text-gray-900">{product.account}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">上手</span>
            <span className="text-gray-900">
              {product.upstream ? `${product.upstream.name} ${product.upstream.percentage}%` : '-'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">下手</span>
            <span className="text-gray-900">{product.downstreams.length}個</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">爬蟲</span>
            <span className={hasCrawler ? "text-blue-600 text-xs" : "text-gray-400 text-xs"}>
              {product.crawlerType ?? '未設定'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">建立時間</span>
            <span className="text-gray-900">{product.createdAt}</span>
          </div>
        </div>

        {/* Footer buttons */}
        <div className="flex gap-2 mt-4 pt-3 border-t border-gray-100">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 text-xs"
            disabled={!hasCrawler || testLoading}
            title={!hasCrawler ? "尚未設定爬蟲類型" : undefined}
            onClick={handleTestConnection}
          >
            {testLoading ? '測試中…' : '測試連接'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1 text-xs"
            disabled={!hasCrawler || fetchLoading}
            title={!hasCrawler ? "尚未設定爬蟲類型" : undefined}
            onClick={handleFetchReport}
          >
            {fetchLoading ? '抓取中…' : 'API呼叫'}
          </Button>
          <Button variant="outline" size="sm" className="flex-1 text-xs" asChild>
            <Link href={`/products/${product.id}/edit`}>編輯</Link>
          </Button>
          <Button
            variant="destructive"
            size="sm"
            className="flex-1 text-xs"
            onClick={() => onDelete(product.id)}
          >
            刪除
          </Button>
        </div>
      </div>
    </>
  )
}
