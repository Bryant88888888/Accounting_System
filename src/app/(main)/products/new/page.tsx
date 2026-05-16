"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Partner, ProductFormData } from "@/types/product"
import { getPartners, getProductSeries, createProduct } from "@/lib/api/products"
import { ProductForm } from "@/components/products/product-form"
import { ArrowLeft } from "lucide-react"

export default function NewProductPage() {
  const router = useRouter()
  const [partners, setPartners] = useState<Partner[]>([])
  const [seriesList, setSeriesList] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const [p, s] = await Promise.all([getPartners(), getProductSeries()])
      setPartners(p)
      setSeriesList(s)
      setLoading(false)
    }
    load()
  }, [])

  if (loading) return <div className="text-gray-500">載入中...</div>

  return (
    <div>
      <div className="mb-6">
        <Link href="/products" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-2">
          <ArrowLeft className="w-4 h-4" />
          返回列表
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">新增產品</h1>
      </div>
      <ProductForm
        partners={partners}
        seriesList={seriesList}
        onSubmit={async (data: ProductFormData) => {
          await createProduct(data)
          router.push("/products")
        }}
        onCancel={() => router.push("/products")}
      />
    </div>
  )
}
