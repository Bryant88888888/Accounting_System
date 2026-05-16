"use client"

import { useEffect, useState } from "react"
import { SettlementReport } from "@/types/report"
import { getSettlementReport } from "@/lib/api/reports"
import { SettlementTable } from "@/components/reports/settlement-table"

export default function SettlementPage() {
  const [report, setReport] = useState<SettlementReport | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const data = await getSettlementReport("2026-01-01", "2026-02-01")
      setReport(data)
      setLoading(false)
    }
    load()
  }, [])

  if (loading || !report) {
    return <div className="text-gray-500">載入中...</div>
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">綜合明細</h1>
        <p className="text-sm text-gray-500 mt-1">{report.startDate} ~ {report.endDate}</p>
      </div>
      <SettlementTable report={report} />
    </div>
  )
}
