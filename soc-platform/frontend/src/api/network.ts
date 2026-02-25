import client from './client'
import type { Asset, NetworkChange, ScanResult } from '../types'

export const getAssets = () =>
  client.get<Asset[]>('/network/assets')

export const getAsset = (id: string) =>
  client.get<Asset>(`/network/assets/${id}`)

export const startScan = (target: string, scan_type = 'standard') =>
  client.post<{ scan_id: string; status: string }>('/network/scan', { target, scan_type })

export const getScanResult = (id: string) =>
  client.get<ScanResult>(`/network/scan/${id}`)

export const getNetworkChanges = () =>
  client.get<NetworkChange[]>('/network/changes')

export const ackChange = (id: string) =>
  client.put(`/network/changes/${id}/ack`)
