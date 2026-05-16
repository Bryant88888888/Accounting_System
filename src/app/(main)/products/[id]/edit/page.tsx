"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import Link from "next/link"
import { Product, Partner, ProductFormData } from "@/types/product"
import { getProduct, getPartners, getProductSeries, updateProduct } from "@/lib/api/products"
import { ProductForm } from "@/components/products/product-form"
import { ArrowLeft } from "lucide-react"

export default function EditProductPage() {
  const router = useRouter()
  const params = useParams()
  const id = params.id as string
  const [product, setProduct] = useState<Product | null>(null)
  const [partners, setPartners] = useState<Partner[]>([])
  const [seriesList, setSeriesList] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const [p, partners, series] = await Promise.all([
        getProduct(id),
        getPartners(),
        getProductSeries(),
      ])
      if (p) setProduct(p)
      setPartners(partners)
      setSeriesList(series)
      setLoading(false)
    }
    load()
  }, [id])

  if (loading) return <div className="text-gray-500">載入中...</div>
  if (!product) return <div className="text-gray-500">產品不存在</div>

  return (
    <div>
      <div className="mb-6">
        <Link href="/products" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-2">
          <ArrowLeft className="w-4 h-4" />
          返回列表
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">編輯產品</h1>
      </div>
      <ProductForm
        initialData={product}
        partners={partners}
        seriesList={seriesList}
        onSubmit={async (data: ProductFormData) => {
          await updateProduct(id, data)
          router.push("/products")
        }}
        onCancel={() => router.push("/products")}
      />
    </div>
  )
}
