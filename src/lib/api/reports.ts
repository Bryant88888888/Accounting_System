import { SettlementReport, SettlementProduct, SettlementMember } from '@/types/report'
import { apiClient, ApiError } from '@/lib/api-client'

interface MemberRes {
  id: number
  name: string
  bet_count: number
  bet_amount: number
  valid_bet: number
  raw_win_loss: number
  rebate_rate: number
  rebate_amount: number
  discount_rate: number
  discount_amount: number
  share_rate: number
  settlement: number
}

interface ProductRes {
  id: number
  product_name: string
  product_code: string | null
  member_count: number
  bet_count: number
  bet_amount: number
  valid_bet: number
  raw_win_loss: number
  rebate_rate: number
  rebate_amount: number
  discount_rate: number
  discount_amount: number
  share_rate: number
  settlement: number
  members: MemberRes[]
}

interface ReportRes {
  id: number
  start_date: string
  end_date: string
  products: ProductRes[]
  totals: {
    bet_count: number
    bet_amount: number
    valid_bet: number
    raw_win_loss: number
    rebate_amount: number
    discount_amount: number
    settlement: number
  }
}

function toMember(m: MemberRes): SettlementMember {
  return {
    id: String(m.id),
    name: m.name,
    betCount: m.bet_count,
    betAmount: m.bet_amount,
    validBet: m.valid_bet,
    rawWinLoss: m.raw_win_loss,
    rebateRate: m.rebate_rate,
    rebateAmount: m.rebate_amount,
    discountRate: m.discount_rate,
    discountAmount: m.discount_amount,
    shareRate: m.share_rate,
    settlement: m.settlement,
  }
}

function toProduct(p: ProductRes): SettlementProduct {
  return {
    id: String(p.id),
    productName: p.product_name,
    productCode: p.product_code || '',
    memberCount: p.member_count,
    betCount: p.bet_count,
    betAmount: p.bet_amount,
    validBet: p.valid_bet,
    rawWinLoss: p.raw_win_loss,
    rebateRate: p.rebate_rate,
    rebateAmount: p.rebate_amount,
    discountRate: p.discount_rate,
    discountAmount: p.discount_amount,
    shareRate: p.share_rate,
    settlement: p.settlement,
    members: p.members.map(toMember),
  }
}

function toReport(r: ReportRes): SettlementReport {
  return {
    startDate: r.start_date,
    endDate: r.end_date,
    products: r.products.map(toProduct),
    totals: {
      betCount: r.totals.bet_count,
      betAmount: r.totals.bet_amount,
      validBet: r.totals.valid_bet,
      rawWinLoss: r.totals.raw_win_loss,
      rebateAmount: r.totals.rebate_amount,
      discountAmount: r.totals.discount_amount,
      settlement: r.totals.settlement,
    },
  }
}

export async function getSettlementReport(startDate: string, endDate: string): Promise<SettlementReport> {
  try {
    const query = `?start_date=${startDate}&end_date=${endDate}`
    const data = await apiClient.get<ReportRes>(`/api/reports/settlement${query}`)
    return toReport(data)
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      // 無資料時回傳空報表
      return {
        startDate,
        endDate,
        products: [],
        totals: { betCount: 0, betAmount: 0, validBet: 0, rawWinLoss: 0, rebateAmount: 0, discountAmount: 0, settlement: 0 },
      }
    }
    throw e
  }
}
