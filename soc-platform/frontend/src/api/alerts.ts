import client from './client'
import type { SecurityAlert } from '../types'

export const getAlerts = (params?: { severity?: string; status?: string; limit?: number }) =>
  client.get<SecurityAlert[]>('/alerts', { params })

export const getAlert = (id: string) =>
  client.get<SecurityAlert>(`/alerts/${id}`)

export const updateAlertStatus = (id: string, status: string) =>
  client.put(`/alerts/${id}/status`, { status })

export const createAlert = (alert: Partial<SecurityAlert>) =>
  client.post('/alerts', alert)
