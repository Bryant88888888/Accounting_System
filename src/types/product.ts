export interface Partner {
  id: string
  name: string
  percentage: number
}

export interface Product {
  id: string
  name: string
  series: string
  code: string
  description: string
  platformType: string
  platformUrl: string
  account: string
  password: string
  crawlerType: string | null
  crawlerAgentId: number | null
  status: 'active' | 'inactive'
  upstream: Partner | null
  myPercentage: number
  downstreams: Partner[]
  rebateRate: number
  discountRate: number
  createdAt: string
}

export type ProductFormData = Omit<Product, 'id' | 'createdAt' | 'status'>
