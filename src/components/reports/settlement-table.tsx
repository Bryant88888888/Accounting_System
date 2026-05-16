"use client"

import { useState, Fragment } from "react"
import { SettlementReport, SettlementProduct } from "@/types/report"
import { formatNumber } from "@/lib/utils"
import { ChevronRight, ChevronDown } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface SettlementTableProps {
  report: SettlementReport
}

function valueColor(value: number): string {
  if (value < 0) return "text-red-500"
  if (value > 0) return "text-green-600"
  return ""
}

export function SettlementTable({ report }: SettlementTableProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  function toggleExpand(productId: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(productId)) {
        next.delete(productId)
      } else {
        next.add(productId)
      }
      return next
    })
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">產品</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">投注數</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">投注金額</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">有效投注</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">原始輸贏</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">返水比例</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">返水金額</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">折扣比例</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">折扣金額</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">佔成比例</th>
              <th className="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">結算</th>
            </tr>
          </thead>
          <tbody>
            {report.products.map((product: SettlementProduct) => {
              const isExpanded = expanded.has(product.id)
              const hasMembers = product.memberCount > 0

              return (
                <Fragment key={product.id}>
                  {/* Product row */}
                  <tr
                    className={`border-b border-gray-100 ${hasMembers ? "cursor-pointer hover:bg-gray-50" : ""}`}
                    onClick={() => hasMembers && toggleExpand(product.id)}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {hasMembers && (
                          isExpanded
                            ? <ChevronDown className="w-4 h-4 text-gray-400" />
                            : <ChevronRight className="w-4 h-4 text-gray-400" />
                        )}
                        {!hasMembers && <span className="w-4" />}
                        <div>
                          <div className="font-bold text-gray-900">{product.productName}</div>
                          <div className="text-xs text-gray-400">{product.productCode}</div>
                        </div>
                        {product.memberCount > 0 && (
                          <Badge variant="secondary" className="text-xs ml-1">{product.memberCount}會員</Badge>
                        )}
                      </div>
                    </td>
                    <td className="text-right px-4 py-3">{formatNumber(product.betCount)}</td>
                    <td className="text-right px-4 py-3">{formatNumber(product.betAmount)}</td>
                    <td className="text-right px-4 py-3">{formatNumber(product.validBet)}</td>
                    <td className={`text-right px-4 py-3 ${valueColor(product.rawWinLoss)}`}>{formatNumber(product.rawWinLoss)}</td>
                    <td className="text-right px-4 py-3">{product.rebateRate}%</td>
                    <td className="text-right px-4 py-3">{formatNumber(product.rebateAmount)}</td>
                    <td className="text-right px-4 py-3">{product.discountRate}%</td>
                    <td className="text-right px-4 py-3">{formatNumber(product.discountAmount)}</td>
                    <td className="text-right px-4 py-3">{product.shareRate}%</td>
                    <td className={`text-right px-4 py-3 font-medium ${valueColor(product.settlement)}`}>{formatNumber(product.settlement)}</td>
                  </tr>

                  {/* Member sub-rows */}
                  {isExpanded && product.members.map((member) => (
                    <tr key={member.id} className="border-b border-gray-50 bg-gray-50/50">
                      <td className="px-4 py-2 pl-14">
                        <span className="text-gray-600 text-sm">{member.name}</span>
                      </td>
                      <td className="text-right px-4 py-2 text-gray-600">{formatNumber(member.betCount)}</td>
                      <td className="text-right px-4 py-2 text-gray-600">{formatNumber(member.betAmount)}</td>
                      <td className="text-right px-4 py-2 text-gray-600">{formatNumber(member.validBet)}</td>
                      <td className={`text-right px-4 py-2 ${valueColor(member.rawWinLoss)}`}>{formatNumber(member.rawWinLoss)}</td>
                      <td className="text-right px-4 py-2 text-gray-600">{member.rebateRate}%</td>
                      <td className="text-right px-4 py-2 text-gray-600">{formatNumber(member.rebateAmount)}</td>
                      <td className="text-right px-4 py-2 text-gray-600">{member.discountRate}%</td>
                      <td className="text-right px-4 py-2 text-gray-600">{formatNumber(member.discountAmount)}</td>
                      <td className="text-right px-4 py-2 text-gray-600">{member.shareRate}%</td>
                      <td className={`text-right px-4 py-2 font-medium ${valueColor(member.settlement)}`}>{formatNumber(member.settlement)}</td>
                    </tr>
                  ))}
                </Fragment>
              )
            })}

            {/* Totals row */}
            <tr className="bg-gray-100 font-bold border-t border-gray-300">
              <td className="px-4 py-3 text-gray-900">合計</td>
              <td className="text-right px-4 py-3">{formatNumber(report.totals.betCount)}</td>
              <td className="text-right px-4 py-3">{formatNumber(report.totals.betAmount)}</td>
              <td className="text-right px-4 py-3">{formatNumber(report.totals.validBet)}</td>
              <td className={`text-right px-4 py-3 ${valueColor(report.totals.rawWinLoss)}`}>{formatNumber(report.totals.rawWinLoss)}</td>
              <td className="text-right px-4 py-3">-</td>
              <td className="text-right px-4 py-3">{formatNumber(report.totals.rebateAmount)}</td>
              <td className="text-right px-4 py-3">-</td>
              <td className="text-right px-4 py-3">{formatNumber(report.totals.discountAmount)}</td>
              <td className="text-right px-4 py-3">-</td>
              <td className={`text-right px-4 py-3 ${valueColor(report.totals.settlement)}`}>{formatNumber(report.totals.settlement)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
