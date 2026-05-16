export interface SettlementMember {
  id: string
  name: string
  betCount: number
  betAmount: number
  validBet: number
  rawWinLoss: number
  rebateRate: number
  rebateAmount: number
  discountRate: number
  discountAmount: number
  shareRate: number
  settlement: number
}

export interface SettlementProduct {
  id: string
  productName: string
  productCode: string
  memberCount: number
  members: SettlementMember[]
  betCount: number
  betAmount: number
  validBet: number
  rawWinLoss: number
  rebateRate: number
  rebateAmount: number
  discountRate: number
  discountAmount: number
  shareRate: number
  settlement: number
}

export interface SettlementReport {
  startDate: string
  endDate: string
  products: SettlementProduct[]
  totals: {
    betCount: number
    betAmount: number
    validBet: number
    rawWinLoss: number
    rebateAmount: number
    discountAmount: number
    settlement: number
  }
}
