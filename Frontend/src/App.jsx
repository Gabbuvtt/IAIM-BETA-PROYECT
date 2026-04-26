import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import LoginForm from './components/LoginForm'
import DashboardLayout from './components/DashboardLayout'
import AdminDashboard from './pages/AdminDashboard'
import TechnicianDashboard from './pages/TechnicianDashboard'
import { useAuth } from './hooks/useAuth'
import './index.css'

function App() {
  const { user, loading, isAuthenticated } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-stone-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-stone-700"></div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-stone-50">
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1e293b',
              color: '#fff',
            },
          }}
        />
        
        <Routes>
          {/* Ruta principal - Login */}
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                <Navigate 
                  to={
                    user?.rol === 'admin' || user?.rol === 'supervisor' 
                      ? '/admin' 
                      : '/tecnico'
                  } 
                  replace 
                />
              ) : (
                <LoginForm />
              )
            } 
          />
          
          {/* Dashboard Admin */}
          <Route 
            path="/admin" 
            element={
              isAuthenticated && (user?.rol === 'admin' || user?.rol === 'supervisor') ? (
                <DashboardLayout>
                  <AdminDashboard />
                </DashboardLayout>
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          
          {/* Dashboard Técnico */}
          <Route 
            path="/tecnico" 
            element={
              isAuthenticated && user?.rol === 'tecnico' ? (
                <DashboardLayout>
                  <TechnicianDashboard />
                </DashboardLayout>
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          
          {/* Ruta por defecto */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
