import client from './client'
import type { DashboardSummary, TimelinePoint } from '../types'

export const getDashboardSummary = () =>
  client.get<DashboardSummary>('/dashboard/summary')

export const getTimeline = () =>
  client.get<TimelinePoint[]>('/dashboard/timeline')

export const getTopThreats = () =>
  client.get<Array<{ type: string; count: number; severity: string }>>('/dashboard/top-threats')

export const getTopSources = () =>
  client.get<Array<{ ip: string; count: number }>>('/dashboard/top-sources')

export const getTopServices = () =>
  client.get<Array<{ service: string; count: number }>>('/dashboard/top-services')
