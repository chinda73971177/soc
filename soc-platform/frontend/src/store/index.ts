import { create } from 'zustand'
import type { User, SecurityAlert, IDSStatus, DashboardSummary } from '../types'

interface SOCStore {
  user: User | null
  setUser: (user: User | null) => void
  isAuthenticated: boolean
  setAuthenticated: (val: boolean) => void
  dashboardSummary: DashboardSummary | null
  setDashboardSummary: (data: DashboardSummary) => void
  recentAlerts: SecurityAlert[]
  setRecentAlerts: (alerts: SecurityAlert[]) => void
  idsStatus: IDSStatus | null
  setIDSStatus: (status: IDSStatus) => void
  wsConnected: boolean
  setWsConnected: (val: boolean) => void
}

export const useSOCStore = create<SOCStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  isAuthenticated: !!localStorage.getItem('access_token'),
  setAuthenticated: (val) => set({ isAuthenticated: val }),
  dashboardSummary: null,
  setDashboardSummary: (data) => set({ dashboardSummary: data }),
  recentAlerts: [],
  setRecentAlerts: (alerts) => set({ recentAlerts: alerts }),
  idsStatus: null,
  setIDSStatus: (status) => set({ idsStatus: status }),
  wsConnected: false,
  setWsConnected: (val) => set({ wsConnected: val }),
}))
