import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider, useAuth } from '@/store/AuthContext'
import { ReactNode } from 'react'

import AppShell from '@/components/layout/AppShell'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import EmpresasPage from '@/pages/empresas/EmpresasPage'
import EmpresaFormPage from '@/pages/empresas/EmpresaFormPage'
import EcacPage from '@/pages/ecac/EcacPage'
import DarfPage from '@/pages/ecac/DarfPage'
import FgtsPage from '@/pages/fgts/FgtsPage'
import TronPage from '@/pages/tron/TronPage'
import RelatoriosPage from '@/pages/relatorios/RelatoriosPage'

const queryClient = new QueryClient()

function ProtectedRoute({ children }: { children: ReactNode }) {
  const token = localStorage.getItem("token")
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/empresas" element={<EmpresasPage />} />
          <Route path="/empresas/nova" element={<EmpresaFormPage />} />
          <Route path="/empresas/:id" element={<EmpresaFormPage />} />
          <Route path="/ecac" element={<EcacPage />} />
          <Route path="/ecac/darf" element={<DarfPage />} />
          <Route path="/fgts" element={<FgtsPage />} />
          <Route path="/tron" element={<TronPage />} />
          <Route path="/relatorios" element={<RelatoriosPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </QueryClientProvider>
  )
}
