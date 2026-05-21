export interface AutoQuerySetting {
  id: number
  tenantId: number
  telegramEnabled: boolean
  telegramChatId: string
  autoQueryEnabled: boolean
  frequencyMinutes: number
  lastRunAt: string | null
  nextRunAt: string | null
  lastStatus: string | null
  createdAt: string | null
  updatedAt: string | null
}

export interface TelegramBotInfo {
  configured: boolean
  username: string | null
  url: string | null
}

export interface AutoQuerySettingForm {
  telegramEnabled: boolean
  telegramChatId?: string | null
  autoQueryEnabled: boolean
  frequencyMinutes: number
}

export interface AutoQueryLog {
  id: number
  tenantId: number
  frequencyMinutes: number
  startedAt: string
  finishedAt: string | null
  status: string
  successCount: number
  failedCount: number
  messageText: string | null
  result: AutoQueryLogItem[] | null
  errorMessage: string | null
}

export interface AutoQueryLogItem {
  product_id: number | null
  name: string
  status: "success" | "failed"
  player_valid_bet?: number
  player_win_loss?: number
  error?: string
}

export interface FrequencyOption {
  value: number
  label: string
}
