import client from './client'
import type { IDSAlert, IDSStatus } from '../types'

export const getIDSStatus = () =>
  client.get<IDSStatus>('/ids/status')

export const getIDSAlerts = (limit = 100) =>
  client.get<IDSAlert[]>('/ids/alerts', { params: { limit } })

export const setIDSMode = (mode: string) =>
  client.put('/ids/mode', { mode })

export const getIDSRules = () =>
  client.get('/ids/rules')

export const createIDSRule = (rule: { name: string; content: string; severity: string }) =>
  client.post('/ids/rules', rule)
