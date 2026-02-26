import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useSOCStore } from './store'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import LogViewer from './pages/LogViewer'
import IDSConsole from './pages/IDSConsole'
import NetworkMap from './pages/NetworkMap'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useSOCStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="logs" element={<LogViewer />} />
          <Route path="ids" element={<IDSConsole />} />
          <Route path="network" element={<NetworkMap />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
