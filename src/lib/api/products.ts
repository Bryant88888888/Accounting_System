import { Product, ProductFormData, Partner } from '@/types/product'
import { apiClient } from '@/lib/api-client'

interface PartnerRef { id: string; name: string; percentage: number }
interface DownstreamRef { id: string; name: string; percentage: number }

interface ProductResponse {
  id: number
  name: string
  series: string
  code: string | null
  description: string | null
  platform_type: string | null
  platform_url: string | null
  account: string | null
  crawler_type: string | null
  crawler_agent_id: number | null
  status: string
  upstream: PartnerRef | null
  my_percentage: number | null
  downstreams: DownstreamRef[]
  rebate_rate: number | null
  discount_rate: number | null
  created_at: string | null
}

interface PartnerResponse {
  id: number
  name: string
  created_at: string | null
}

function toProduct(r: ProductResponse): Product {
  return {
    id: String(r.id),
    name: r.name,
    series: r.series,
    code: r.code || '',
    description: r.description || '',
    platformType: r.platform_type || '',
    platformUrl: r.platform_url || '',
    account: r.account || '',
    password: '',
    crawlerType: r.crawler_type ?? null,
    crawlerAgentId: r.crawler_agent_id ?? null,
    status: r.status as Product['status'],
    upstream: r.upstream
      ? { id: r.upstream.id, name: r.upstream.name, percentage: r.upstream.percentage }
      : null,
    myPercentage: r.my_percentage || 0,
    downstreams: r.downstreams.map(d => ({ id: `ds-${d.id}`, name: d.name, percentage: d.percentage })),
    rebateRate: r.rebate_rate || 0,
    discountRate: r.discount_rate || 0,
    createdAt: r.created_at || '',
  }
}

function toApiBody(data: Partial<ProductFormData>) {
  return {
    name: data.name,
    series: data.series,
    code: data.code,
    description: data.description,
    platform_type: data.platformType,
    platform_url: data.platformUrl,
    account: data.account,
    password: data.password || undefined,
    crawler_type: data.crawlerType || undefined,
    crawler_agent_id: data.crawlerAgentId || null,
    upstream_partner_id: data.upstream ? Number(data.upstream.id) : null,
    upstream_percentage: data.upstream?.percentage,
    my_percentage: data.myPercentage,
    rebate_rate: data.rebateRate,
    discount_rate: data.discountRate,
    downstreams: data.downstreams?.map(d => ({ name: d.name, percentage: d.percentage })) || [],
  }
}

export async function getProducts(series?: string): Promise<Product[]> {
  const query = series && series !== 'all' ? `?series=${encodeURIComponent(series)}` : ''
  const data = await apiClient.get<ProductResponse[]>(`/api/products${query}`)
  return data.map(toProduct)
}

export async function getProduct(id: string): Promise<Product | undefined> {
  try {
    const data = await apiClient.get<ProductResponse>(`/api/products/${id}`)
    return toProduct(data)
  } catch {
    return undefined
  }
}

export async function createProduct(data: ProductFormData): Promise<Product> {
  const res = await apiClient.post<ProductResponse>('/api/products', toApiBody(data))
  return toProduct(res)
}

export async function updateProduct(id: string, data: Partial<ProductFormData>): Promise<Product> {
  const res = await apiClient.put<ProductResponse>(`/api/products/${id}`, toApiBody(data))
  return toProduct(res)
}

export async function deleteProduct(id: string): Promise<void> {
  await apiClient.delete(`/api/products/${id}`)
}

export async function getPartners(): Promise<Partner[]> {
  const data = await apiClient.get<PartnerResponse[]>('/api/partners')
  return data.map(p => ({ id: String(p.id), name: p.name, percentage: 0 }))
}

export async function getProductSeries(): Promise<string[]> {
  return apiClient.get<string[]>('/api/products/series')
}

export async function testConnection(id: string): Promise<{ success: boolean; message: string }> {
  return apiClient.post(`/api/products/${id}/test-connection`, {})
}

export async function fetchReport(id: string): Promise<{ success: boolean; data?: unknown; error?: string }> {
  return apiClient.post(`/api/products/${id}/fetch-report`, {})
}

export interface PlayerMetrics {
  player_valid_bet: number
  player_win_loss: number
  source?: unknown
}

export async function fetchPlayerMetrics(id: string): Promise<{ success: boolean; data?: PlayerMetrics; error?: string }> {
  return apiClient.post(`/api/products/${id}/player-metrics`, {})
}
