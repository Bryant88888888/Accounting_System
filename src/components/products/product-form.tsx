"use client"

import { useState } from "react"
import { Product, Partner, ProductFormData } from "@/types/product"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Trash2, Plus } from "lucide-react"

interface ProductFormProps {
  initialData?: Product
  partners: Partner[]
  seriesList: string[]
  onSubmit: (data: ProductFormData) => void
  onCancel: () => void
}

interface DownstreamEntry {
  id: string
  name: string
  percentage: number
}

const defaultSeries = "API 平台"

const crawlerOptions = [
  { value: "cali358", label: "卡利", platformType: "API 平台", platformUrl: "https://ams.cali358.net" },
  { value: "t9live1", label: "T9", platformType: "API 平台", platformUrl: "https://i.t9live1.vip" },
  { value: "ag_dg18", label: "DG", platformType: "API 平台", platformUrl: "https://ag.dg18.vip" },
  { value: "tz98", label: "太子", platformType: "API 平台", platformUrl: "https://ag.tz98.net" },
  { value: "kim_tae_ji_888", label: "泰8", platformType: "API 平台", platformUrl: "https://xg.tg8888.in/app/" },
]

export function ProductForm({ initialData, partners, seriesList, onSubmit, onCancel }: ProductFormProps) {
  const seriesOptions = Array.from(new Set([defaultSeries, ...seriesList.filter(Boolean)]))
  const [name, setName] = useState(initialData?.name ?? "")
  const [series, setSeries] = useState(initialData?.series || defaultSeries)
  const [code, setCode] = useState(initialData?.code ?? "")
  const [description, setDescription] = useState(initialData?.description ?? "")
  const [account, setAccount] = useState(initialData?.account ?? "")
  const [password, setPassword] = useState("")
  const [crawlerType, setCrawlerType] = useState(initialData?.crawlerType || "none")
  const [upstreamId, setUpstreamId] = useState(initialData?.upstream?.id ?? "")
  const [myPercentage, setMyPercentage] = useState(initialData?.myPercentage ?? 50)
  const [rebateRate, setRebateRate] = useState(initialData?.rebateRate ?? 0)
  const [discountRate, setDiscountRate] = useState(initialData?.discountRate ?? 0)
  const [downstreams, setDownstreams] = useState<DownstreamEntry[]>(
    initialData?.downstreams?.map(d => ({ id: d.id, name: d.name, percentage: d.percentage })) ?? []
  )

  const upstreamPartner = partners.find(p => p.id === upstreamId)
  const upstreamPercentage = 100 - myPercentage
  const downstreamTotal = downstreams.reduce((sum, d) => sum + d.percentage, 0)
  const selectedCrawler = crawlerOptions.find(option => option.value === crawlerType)

  function addDownstream() {
    setDownstreams([...downstreams, { id: `new-${Date.now()}`, name: "", percentage: 0 }])
  }

  function removeDownstream(index: number) {
    setDownstreams(downstreams.filter((_, i) => i !== index))
  }

  function updateDownstream(index: number, field: keyof DownstreamEntry, value: string | number) {
    const updated = [...downstreams]
    updated[index] = { ...updated[index], [field]: value }
    setDownstreams(updated)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const formData: ProductFormData = {
      name,
      series,
      code,
      description,
      platformType: selectedCrawler?.platformType ?? defaultSeries,
      platformUrl: selectedCrawler?.platformUrl ?? "",
      account,
      password,
      crawlerType: crawlerType === "none" ? null : crawlerType || null,
      crawlerAgentId: initialData?.crawlerAgentId ?? null,
      upstream: upstreamPartner ? { id: upstreamPartner.id, name: upstreamPartner.name, percentage: upstreamPercentage } : null,
      myPercentage,
      downstreams: downstreams.map(d => ({ id: d.id, name: d.name, percentage: d.percentage })),
      rebateRate,
      discountRate,
    }
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border border-gray-200 bg-white p-4 md:p-6">
      <div>
        <h3 className="mb-4 text-lg font-semibold text-gray-900">產品資料</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="name">產品名稱 *</Label>
            <Input id="name" value={name} onChange={e => setName(e.target.value)} required className="mt-1" />
          </div>
          <div>
            <Label htmlFor="series">產品系列 *</Label>
            <Select value={series} onValueChange={setSeries} required>
              <SelectTrigger className="mt-1" id="series">
                <SelectValue placeholder="選擇系列" />
              </SelectTrigger>
              <SelectContent>
                {seriesOptions.map(s => (
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="mt-1 text-xs text-gray-500">目前提供的查帳產品都歸在 API 平台。</p>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="code">產品代碼</Label>
            <Input id="code" value={code} onChange={e => setCode(e.target.value)} className="mt-1" />
          </div>
        </div>
        <div className="mt-4">
          <Label htmlFor="description">備註</Label>
          <Textarea id="description" value={description} onChange={e => setDescription(e.target.value)} className="mt-1" />
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="mb-4 text-lg font-semibold text-gray-900">查帳設定</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="crawlerType">查帳平台 *</Label>
            <Select value={crawlerType} onValueChange={setCrawlerType}>
              <SelectTrigger className="mt-1" id="crawlerType">
                <SelectValue placeholder="選擇平台" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">不使用 API 查帳</SelectItem>
                {crawlerOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>平台網址</Label>
            <Input value={selectedCrawler?.platformUrl ?? ""} readOnly placeholder="選擇平台後自動帶入" className="mt-1 bg-gray-50" />
          </div>
        </div>
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="account">平台帳號 *</Label>
            <Input id="account" value={account} onChange={e => setAccount(e.target.value)} required className="mt-1" />
          </div>
          <div>
            <Label htmlFor="password">平台密碼 {initialData ? "(不修改可留空)" : ""}</Label>
            <Input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} className="mt-1" />
          </div>
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="mb-1 text-lg font-semibold text-gray-900">上手設定</h3>
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="upstream">上手夥伴</Label>
            <Select value={upstreamId} onValueChange={setUpstreamId}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="選擇上手" />
              </SelectTrigger>
              <SelectContent>
                {partners.map(p => (
                  <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="myPercentage">我方佔成 (%)</Label>
            <Input
              id="myPercentage"
              type="number"
              min={0}
              max={100}
              value={myPercentage}
              onChange={e => setMyPercentage(Number(e.target.value))}
              className="mt-1"
            />
          </div>
        </div>
        {upstreamId && (
          <p className="mt-2 text-sm text-gray-500">上手佔成：{upstreamPercentage}%</p>
        )}
      </div>

      <Separator />

      <div>
        <h3 className="mb-1 text-lg font-semibold text-gray-900">費率設定</h3>
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="rebateRate">返水率</Label>
            <div className="mt-1 flex items-center gap-2">
              <Input
                id="rebateRate"
                type="number"
                step="0.1"
                min={0}
                max={100}
                value={rebateRate}
                onChange={e => setRebateRate(Number(e.target.value))}
              />
              <span className="text-gray-500">%</span>
            </div>
          </div>
          <div>
            <Label htmlFor="discountRate">折扣率</Label>
            <div className="mt-1 flex items-center gap-2">
              <Input
                id="discountRate"
                type="number"
                step="0.1"
                min={0}
                max={100}
                value={discountRate}
                onChange={e => setDiscountRate(Number(e.target.value))}
              />
              <span className="text-gray-500">%</span>
            </div>
          </div>
        </div>
      </div>

      <Separator />

      <div>
        <div className="mb-1 flex items-center justify-between gap-3">
          <h3 className="text-lg font-semibold text-gray-900">下手設定</h3>
          <Button type="button" variant="outline" size="sm" onClick={addDownstream}>
            <Plus className="h-4 w-4" />
            新增下手
          </Button>
        </div>

        {downstreams.length > 0 ? (
          <div className="mt-4 space-y-3">
            {downstreams.map((ds, index) => (
              <div key={ds.id} className="grid grid-cols-[1fr_auto_auto] items-center gap-3">
                <Select
                  value={ds.id.startsWith("new-") ? "" : ds.id}
                  onValueChange={(val) => {
                    const partner = partners.find(p => p.id === val)
                    if (partner) {
                      const updated = [...downstreams]
                      updated[index] = { ...updated[index], id: partner.id, name: partner.name }
                      setDownstreams(updated)
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="選擇夥伴" />
                  </SelectTrigger>
                  <SelectContent>
                    {partners.map(p => (
                      <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className="flex w-28 items-center gap-1">
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    value={ds.percentage}
                    onChange={e => updateDownstream(index, "percentage", Number(e.target.value))}
                  />
                  <span className="text-gray-500">%</span>
                </div>
                <Button type="button" variant="ghost" size="icon" onClick={() => removeDownstream(index)}>
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            ))}
            <p className="mt-2 text-sm text-gray-500">下手佔成合計：{downstreamTotal}%</p>
          </div>
        ) : (
          <p className="mt-4 text-sm text-gray-400">尚未設定下手夥伴</p>
        )}
      </div>

      <Separator />

      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>取消</Button>
        <Button type="submit">{initialData ? "儲存變更" : "建立產品"}</Button>
      </div>
    </form>
  )
}
