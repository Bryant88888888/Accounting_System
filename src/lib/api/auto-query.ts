import { apiClient } from "@/lib/api-client"
import { AutoQueryLog, AutoQuerySetting, AutoQuerySettingForm, FrequencyOption, TelegramBotInfo } from "@/types/auto-query"

interface AutoQuerySettingResponse {
  id: number
  tenant_id: number
  telegram_enabled: boolean
  telegram_chat_id: string | null
  auto_query_enabled: boolean
  frequency_minutes: number
  last_run_at: string | null
  next_run_at: string | null
  last_status: string | null
  created_at: string | null
  updated_at: string | null
}

interface AutoQueryLogResponse {
  id: number
  tenant_id: number
  frequency_minutes: number
  started_at: string
  finished_at: string | null
  status: string
  success_count: number
  failed_count: number
  message_text: string | null
  result: AutoQueryLog["result"]
  error_message: string | null
}

function toSetting(data: AutoQuerySettingResponse): AutoQuerySetting {
  return {
    id: data.id,
    tenantId: data.tenant_id,
    telegramEnabled: data.telegram_enabled,
    telegramChatId: data.telegram_chat_id || "",
    autoQueryEnabled: data.auto_query_enabled,
    frequencyMinutes: data.frequency_minutes,
    lastRunAt: data.last_run_at,
    nextRunAt: data.next_run_at,
    lastStatus: data.last_status,
    createdAt: data.created_at,
    updatedAt: data.updated_at,
  }
}

function toLog(data: AutoQueryLogResponse): AutoQueryLog {
  return {
    id: data.id,
    tenantId: data.tenant_id,
    frequencyMinutes: data.frequency_minutes,
    startedAt: data.started_at,
    finishedAt: data.finished_at,
    status: data.status,
    successCount: data.success_count,
    failedCount: data.failed_count,
    messageText: data.message_text,
    result: data.result,
    errorMessage: data.error_message,
  }
}

export function getAutoQueryFrequencies(): Promise<FrequencyOption[]> {
  return apiClient.get("/api/auto-query/frequencies")
}

export function getTelegramBotInfo(): Promise<TelegramBotInfo> {
  return apiClient.get("/api/auto-query/bot-info")
}

export async function getAutoQuerySetting(): Promise<AutoQuerySetting> {
  const data = await apiClient.get<AutoQuerySettingResponse>("/api/auto-query/setting")
  return toSetting(data)
}

export async function updateAutoQuerySetting(data: AutoQuerySettingForm): Promise<AutoQuerySetting> {
  const res = await apiClient.put<AutoQuerySettingResponse>("/api/auto-query/setting", {
    telegram_enabled: data.telegramEnabled,
    telegram_chat_id: data.telegramChatId,
    auto_query_enabled: data.autoQueryEnabled,
    frequency_minutes: data.frequencyMinutes,
  })
  return toSetting(res)
}

export function testTelegram(): Promise<{ success: boolean; message: string }> {
  return apiClient.post("/api/auto-query/test-telegram", {})
}

export async function runAutoQueryNow(): Promise<{ success: boolean; log?: AutoQueryLog; error?: string }> {
  const res = await apiClient.post<{ success: boolean; log?: AutoQueryLogResponse; error?: string }>("/api/auto-query/run-now", {})
  return { success: res.success, log: res.log ? toLog(res.log) : undefined, error: res.error }
}

export async function getAutoQueryLogs(): Promise<AutoQueryLog[]> {
  const data = await apiClient.get<AutoQueryLogResponse[]>("/api/auto-query/logs")
  return data.map(toLog)
}
