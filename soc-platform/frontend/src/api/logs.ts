import client from './client'
import type { LogEntry } from '../types'

export interface LogSearchParams {
  query?: string
  log_source?: string
  log_type?: string
  severity?: string
  host?: string
  src_ip?: string
  dst_ip?: string
  port?: number
  protocol?: string
  service?: string
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

export const searchLogs = (params: LogSearchParams) =>
  client.post<{ total: number; page: number; page_size: number; logs: LogEntry[] }>('/logs/search', params)

export const getLogStats = () =>
  client.get<{ total_today: number; by_severity: Record<string, number>; by_source: Record<string, number>; by_type: Record<string, number>; timeline: Array<{ time: string; count: number }> }>('/logs/stats')
