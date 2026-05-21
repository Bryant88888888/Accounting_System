"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Plus } from "lucide-react"
import { Product } from "@/types/product"
import { getProducts, getProductSeries, deleteProduct } from "@/lib/api/products"
import { ProductCard } from "@/components/products/product-card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [series, setSeries] = useState<string[]>([])
  const [selectedSeries, setSelectedSeries] = useState<string>("all")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function loadData() {
      const [productsData, seriesData] = await Promise.all([
        getProducts(selectedSeries),
        getProductSeries(),
      ])
      if (cancelled) return
      setProducts(productsData)
      setSeries(seriesData)
      setLoading(false)
    }

    loadData()
    return () => {
      cancelled = true
    }
  }, [selectedSeries])

  async function handleDelete(id: string) {
    if (!confirm("確定要刪除此產品嗎？")) return
    await deleteProduct(id)
    const data = await getProducts(selectedSeries)
    setProducts(data)
  }

  if (loading && products.length === 0) {
    return <div className="text-gray-500">載入中...</div>
  }

  return (
    <div className="min-w-0">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-gray-900">產品管理</h1>
        <Button asChild className="w-full sm:w-auto">
          <Link href="/products/new">
            <Plus className="h-4 w-4" />
            新增產品
          </Link>
        </Button>
      </div>

      <div className="mb-6">
        <Select value={selectedSeries} onValueChange={setSelectedSeries}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="選擇系列" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部系列</SelectItem>
            {series.map((s) => (
              <SelectItem key={s} value={s}>{s}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid min-w-0 grid-cols-1 gap-4 lg:grid-cols-2 2xl:grid-cols-3">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onDelete={handleDelete}
          />
        ))}
      </div>

      {products.length === 0 && !loading && (
        <div className="py-12 text-center text-gray-500">
          尚無產品資料
        </div>
      )}
    </div>
  )
}
