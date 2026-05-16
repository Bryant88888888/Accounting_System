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

export function ProductForm({ initialData, partners, seriesList, onSubmit, onCancel }: ProductFormProps) {
  const [name, setName] = useState(initialData?.name ?? "")
  const [series, setSeries] = useState(initialData?.series ?? "")
  const [code, setCode] = useState(initialData?.code ?? "")
  const [description, setDescription] = useState(initialData?.description ?? "")
  const [platformType, setPlatformType] = useState(initialData?.platformType ?? "")
  const [platformUrl, setPlatformUrl] = useState(initialData?.platformUrl ?? "")
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
      platformType,
      platformUrl,
      account,
      password,
      crawlerType: crawlerType === "none" ? null : crawlerType || null,
      upstream: upstreamPartner ? { id: upstreamPartner.id, name: upstreamPartner.name, percentage: upstreamPercentage } : null,
      myPercentage,
      downstreams: downstreams.map(d => ({ id: d.id, name: d.name, percentage: d.percentage })),
      rebateRate,
      discountRate,
    }
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white rounded-lg border border-gray-200 p-6">
      {/* Section 1: 產品資訊 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">產品資訊</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="name">產品名稱 *</Label>
            <Input id="name" value={name} onChange={e => setName(e.target.value)} required className="mt-1" />
          </div>
          <div>
            <Label htmlFor="series">產品系列 *</Label>
            <Select value={series} onValueChange={setSeries} required>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="選擇系列" />
              </SelectTrigger>
              <SelectContent>
                {seriesList.map(s => (
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <Label htmlFor="code">產品編碼</Label>
            <Input id="code" value={code} onChange={e => setCode(e.target.value)} placeholder="可選" className="mt-1" />
          </div>
        </div>
        <div className="mt-4">
          <Label htmlFor="description">描述</Label>
          <Textarea id="description" value={description} onChange={e => setDescription(e.target.value)} className="mt-1" />
        </div>
      </div>

      <Separator />

      {/* Section 2: 平台連接 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">平台連接</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="platformType">平台類型 *</Label>
            <Select value={platformType} onValueChange={setPlatformType} required>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="選擇平台" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="體育">體育</SelectItem>
                <SelectItem value="真人">真人</SelectItem>
                <SelectItem value="電子">電子</SelectItem>
                <SelectItem value="彩票">彩票</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="platformUrl">平台地址 *</Label>
            <Input id="platformUrl" value={platformUrl} onChange={e => setPlatformUrl(e.target.value)} required className="mt-1" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <Label htmlFor="account">帳號 *</Label>
            <Input id="account" value={account} onChange={e => setAccount(e.target.value)} required className="mt-1" />
          </div>
          <div>
            <Label htmlFor="password">密碼 {initialData ? "(留空則不修改)" : ""}</Label>
            <Input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} className="mt-1" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <Label htmlFor="crawlerType">爬蟲類型</Label>
            <Select value={crawlerType} onValueChange={setCrawlerType}>
              <SelectTrigger className="mt-1" id="crawlerType">
                <SelectValue placeholder="無（不啟用爬蟲）" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">無（不啟用爬蟲）</SelectItem>
                <SelectItem value="ag_dg18">AG DG18 (ag.dg18.vip)</SelectItem>
                <SelectItem value="cali358">Cali358 (ams.cali358.net)</SelectItem>
                <SelectItem value="kim_tae_ji_888">Kim Tae Ji 888 (xg.tg8888.in)</SelectItem>
                <SelectItem value="t9live1">T9live1 (i.t9live1.vip)</SelectItem>
                <SelectItem value="tz98">TZ98 (ag.tz98.net)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Separator />

      {/* Section 3: 上手設定 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">上手設定</h3>
        <p className="text-sm text-gray-500 mb-4">設定該產品的上手夥伴和分成比例</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            <Label htmlFor="myPercentage">我的佔比 (%)</Label>
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
          <p className="text-sm text-gray-500 mt-2">上手佔比: {upstreamPercentage}%</p>
        )}
      </div>

      <Separator />

      {/* Section 4: 結算設定 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">結算設定</h3>
        <p className="text-sm text-gray-500 mb-4">設定產品的返水和折扣比例</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="rebateRate">返水比例</Label>
            <div className="flex items-center gap-2 mt-1">
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
            <p className="text-xs text-gray-400 mt-1">玩家的返水比例</p>
          </div>
          <div>
            <Label htmlFor="discountRate">折扣比例</Label>
            <div className="flex items-center gap-2 mt-1">
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
            <p className="text-xs text-gray-400 mt-1">結算時的折扣比例</p>
          </div>
        </div>
      </div>

      <Separator />

      {/* Section 5: 下手設定 */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-lg font-semibold text-gray-900">下手設定</h3>
          <Button type="button" variant="outline" size="sm" onClick={addDownstream}>
            <Plus className="w-4 h-4" />
            新增下手
          </Button>
        </div>
        <p className="text-sm text-gray-500 mb-4">設定該產品分發給哪些下手夥伴</p>

        {downstreams.length > 0 ? (
          <div className="space-y-3">
            {downstreams.map((ds, index) => (
              <div key={ds.id} className="flex items-center gap-3">
                <div className="flex-1">
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
                </div>
                <div className="w-32">
                  <div className="flex items-center gap-1">
                    <Input
                      type="number"
                      min={0}
                      max={100}
                      value={ds.percentage}
                      onChange={e => updateDownstream(index, "percentage", Number(e.target.value))}
                    />
                    <span className="text-gray-500">%</span>
                  </div>
                </div>
                <Button type="button" variant="ghost" size="icon" onClick={() => removeDownstream(index)}>
                  <Trash2 className="w-4 h-4 text-red-500" />
                </Button>
              </div>
            ))}
            <p className="text-sm text-gray-500 mt-2">
              下手總佔比: {downstreamTotal}% (基於我的份額)
            </p>
          </div>
        ) : (
          <p className="text-sm text-gray-400">尚未設定下手夥伴</p>
        )}
      </div>

      <Separator />

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel}>取消</Button>
        <Button type="submit">{initialData ? "儲存變更" : "建立產品"}</Button>
      </div>
    </form>
  )
}
