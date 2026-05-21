"use client"

import { useEffect, useState } from "react"
import { Bell, ExternalLink, Play, Save, Send } from "lucide-react"
import {
  getAutoQueryFrequencies,
  getAutoQueryLogs,
  getAutoQuerySetting,
  getTelegramBotInfo,
  runAutoQueryNow,
  testTelegram,
  updateAutoQuerySetting,
} from "@/lib/api/auto-query"
import { AutoQueryLog, AutoQuerySetting, FrequencyOption, TelegramBotInfo } from "@/types/auto-query"
import { ApiError } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

function formatTime(value: string | null) {
  if (!value) return "-"
  return new Date(value).toLocaleString("zh-TW", { hour12: false })
}

function statusLabel(status: string | null) {
  if (!status) return "尚未執行"
  if (status === "success") return "成功"
  if (status === "partial_failed") return "部分失敗"
  if (status === "failed") return "失敗"
  return status
}

export default function TasksPage() {
  const [setting, setSetting] = useState<AutoQuerySetting | null>(null)
  const [botInfo, setBotInfo] = useState<TelegramBotInfo | null>(null)
  const [frequencies, setFrequencies] = useState<FrequencyOption[]>([])
  const [logs, setLogs] = useState<AutoQueryLog[]>([])
  const [message, setMessage] = useState("")
  const [loadError, setLoadError] = useState("")
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    load()
  }, [])

  async function load() {
    setLoading(true)
    setLoadError("")
    try {
      const [settingData, frequencyData, logData, botData] = await Promise.all([
        getAutoQuerySetting(),
        getAutoQueryFrequencies(),
        getAutoQueryLogs(),
        getTelegramBotInfo(),
      ])
      setSetting(settingData)
      setFrequencies(frequencyData)
      setLogs(logData)
      setBotInfo(botData)
    } catch (error) {
      setLoadError(error instanceof ApiError ? error.message : "載入定時任務設定失敗")
    } finally {
      setLoading(false)
    }
  }

  async function handleSave() {
    if (!setting) return
    setSaving(true)
    setMessage("")
    try {
      const updated = await updateAutoQuerySetting({
        telegramEnabled: setting.telegramEnabled,
        telegramChatId: setting.telegramChatId,
        autoQueryEnabled: setting.autoQueryEnabled,
        frequencyMinutes: setting.frequencyMinutes,
      })
      setSetting(updated)
      setMessage("設定已儲存")
    } catch (error) {
      setMessage(error instanceof ApiError ? error.message : "儲存失敗")
    } finally {
      setSaving(false)
    }
  }

  async function handleTestTelegram() {
    setTesting(true)
    setMessage("")
    try {
      const res = await testTelegram()
      setMessage(res.message)
    } catch (error) {
      setMessage(error instanceof ApiError ? error.message : "測試推播失敗")
    } finally {
      setTesting(false)
    }
  }

  async function handleRunNow() {
    setRunning(true)
    setMessage("")
    try {
      const res = await runAutoQueryNow()
      setMessage(res.log ? `立即執行完成：${statusLabel(res.log.status)}` : res.error || "立即執行完成")
      const [settingData, logData] = await Promise.all([getAutoQuerySetting(), getAutoQueryLogs()])
      setSetting(settingData)
      setLogs(logData)
    } catch (error) {
      setMessage(error instanceof ApiError ? error.message : "立即執行失敗")
    } finally {
      setRunning(false)
    }
  }

  if (loading) {
    return <div className="text-gray-500">載入中...</div>
  }

  if (loadError || !setting) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">定時任務</h1>
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {loadError || "找不到定時任務設定"}
        </div>
        <div className="text-sm text-gray-500">
          這個功能是租戶級設定；如果你目前使用超級管理員帳號，請切換到租戶帳號測試。
        </div>
        <Button type="button" variant="outline" onClick={load}>
          重新載入
        </Button>
      </div>
    )
  }

  const botName = botInfo?.username || "系統 Telegram Bot"

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">定時任務</h1>
        <p className="mt-1 text-sm text-gray-500">系統每小時檢查一次，到期後自動查詢本週帳務並推送 Telegram。</p>
      </div>

      {message && (
        <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 shadow-sm">
          {message}
        </div>
      )}

      <section className="rounded-lg border border-gray-200 bg-white p-5">
        <div className="mb-4 flex items-center gap-2">
          <Bell className="h-5 w-5 text-orange-500" />
          <h2 className="text-lg font-semibold text-gray-900">Telegram 推播</h2>
        </div>

        <div className="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700">
          <div className="font-medium text-gray-900">Bot：{botName}</div>
          <div className="mt-1">狀態：{botInfo?.configured ? "系統 Bot 已設定" : "系統尚未設定 TELEGRAM_BOT_TOKEN"}</div>
          <div className="mt-3 space-y-1">
            <div>1. 到 Telegram 開啟 Bot。</div>
            <div>2. 對 Bot 傳送 <span className="font-mono">/start</span> 或 <span className="font-mono">/id</span>。</div>
            <div>3. Bot 會回覆這個聊天室的 Chat ID，將它貼到下方欄位。</div>
          </div>
          {botInfo?.url && (
            <a
              href={botInfo.url}
              target="_blank"
              rel="noreferrer"
              className="mt-3 inline-flex items-center gap-1 text-orange-600 hover:text-orange-700"
            >
              開啟 Telegram Bot
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={setting.telegramEnabled}
              onChange={e => setSetting({ ...setting, telegramEnabled: e.target.checked })}
              className="h-4 w-4"
            />
            啟用 Telegram 推播
          </label>
          <div>
            <Label htmlFor="telegramChatId">Telegram Chat ID</Label>
            <Input
              id="telegramChatId"
              value={setting.telegramChatId}
              onChange={e => setSetting({ ...setting, telegramChatId: e.target.value })}
              placeholder="例如 123456789 或 -1001234567890"
              className="mt-1"
            />
          </div>
        </div>

        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <Button type="button" onClick={handleSave} disabled={saving}>
            <Save className="h-4 w-4" />
            {saving ? "儲存中..." : "儲存設定"}
          </Button>
          <Button type="button" variant="outline" onClick={handleTestTelegram} disabled={testing || !botInfo?.configured}>
            <Send className="h-4 w-4" />
            {testing ? "測試中..." : "測試推播"}
          </Button>
        </div>
      </section>

      <section className="rounded-lg border border-gray-200 bg-white p-5">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">自動查帳</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={setting.autoQueryEnabled}
              onChange={e => setSetting({ ...setting, autoQueryEnabled: e.target.checked })}
              className="h-4 w-4"
            />
            啟用自動查帳
          </label>
          <div>
            <Label>查詢頻率</Label>
            <Select
              value={String(setting.frequencyMinutes)}
              onValueChange={value => setSetting({ ...setting, frequencyMinutes: Number(value) })}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {frequencies.map(option => (
                  <SelectItem key={option.value} value={String(option.value)}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-3 text-sm text-gray-600 md:grid-cols-3">
          <div>查詢範圍：本週</div>
          <div>最近執行：{formatTime(setting.lastRunAt)}</div>
          <div>下次執行：{formatTime(setting.nextRunAt)}</div>
          <div>最近狀態：{statusLabel(setting.lastStatus)}</div>
        </div>

        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <Button type="button" onClick={handleSave} disabled={saving}>
            <Save className="h-4 w-4" />
            {saving ? "儲存中..." : "儲存設定"}
          </Button>
          <Button type="button" variant="outline" onClick={handleRunNow} disabled={running}>
            <Play className="h-4 w-4" />
            {running ? "執行中..." : "立即執行一次"}
          </Button>
        </div>
      </section>

      <section className="rounded-lg border border-gray-200 bg-white p-5">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">最近執行紀錄</h2>
        {logs.length === 0 ? (
          <div className="py-8 text-center text-sm text-gray-500">尚無執行紀錄</div>
        ) : (
          <div className="space-y-3">
            {logs.map(log => (
              <div key={log.id} className="rounded border border-gray-200 p-4">
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                  <div className="font-medium text-gray-900">{formatTime(log.startedAt)}</div>
                  <div className="text-sm text-gray-600">
                    {statusLabel(log.status)}，成功 {log.successCount}，失敗 {log.failedCount}
                  </div>
                </div>
                {log.errorMessage && <div className="mt-2 text-sm text-red-600">{log.errorMessage}</div>}
                {log.messageText && (
                  <pre className="mt-3 whitespace-pre-wrap rounded bg-gray-50 p-3 text-xs text-gray-700">
                    {log.messageText}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
