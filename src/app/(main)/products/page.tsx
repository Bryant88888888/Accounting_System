"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Product } from "@/types/product"
import { getProducts, getProductSeries, deleteProduct } from "@/lib/api/products"
import { ProductCard } from "@/components/products/product-card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus } from "lucide-react"

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [series, setSeries] = useState<string[]>([])
  const [selectedSeries, setSelectedSeries] = useState<string>("all")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    loadProducts()
  }, [selectedSeries])

  async function loadData() {
    const [productsData, seriesData] = await Promise.all([
      getProducts(),
      getProductSeries(),
    ])
    setProducts(productsData)
    setSeries(seriesData)
    setLoading(false)
  }

  async function loadProducts() {
    setLoading(true)
    const data = await getProducts(selectedSeries)
    setProducts(data)
    setLoading(false)
  }

  async function handleDelete(id: string) {
    if (!confirm("確定要刪除此產品嗎？")) return
    await deleteProduct(id)
    await loadProducts()
  }

  if (loading && products.length === 0) {
    return <div className="text-gray-500">載入中...</div>
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">產品管理</h1>
        <Button asChild>
          <Link href="/products/new">
            <Plus className="w-4 h-4" />
            新增產品
          </Link>
        </Button>
      </div>

      {/* Filter */}
      <div className="mb-6">
        <Select value={selectedSeries} onValueChange={setSelectedSeries}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="全部系列" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部系列</SelectItem>
            {series.map((s) => (
              <SelectItem key={s} value={s}>{s}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onDelete={handleDelete}
          />
        ))}
      </div>

      {products.length === 0 && !loading && (
        <div className="text-center text-gray-500 py-12">
          尚無產品資料
        </div>
      )}
    </div>
  )
}
