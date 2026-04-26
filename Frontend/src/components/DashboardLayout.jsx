import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { 
  Users, 
  FileText, 
  LogOut, 
  Menu, 
  X,
  Plane
} from 'lucide-react'

export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const navigation = [
    { name: 'Tickets', href: user?.rol === 'tecnico' ? '/tecnico' : '/admin', icon: FileText },
    ...(user?.rol === 'admin' || user?.rol === 'supervisor' ? [{ name: 'Usuarios', href: '/admin', icon: Users }] : []),
  ]

  const isActive = (href) => {
    if (href === '/') return location.pathname === '/'
    return location.pathname.startsWith(href)
  }

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-stone-900 bg-opacity-50" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white">
          <div className="flex h-16 items-center justify-between px-4 border-b border-stone-100">
            <div className="flex items-center">
              <Plane className="h-8 w-8 text-stone-700" />
              <span className="ml-2 text-xl font-bold text-stone-800">IAIM</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-stone-400 hover:text-stone-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => (
              <button
                key={item.name}
                onClick={() => navigate(item.href)}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md w-full text-left ${
                  isActive(item.href)
                    ? 'bg-stone-100 text-stone-800'
                    : 'text-stone-500 hover:text-stone-800 hover:bg-stone-50'
                }`}
              >
                <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                {item.name}
              </button>
            ))}
          </nav>

          <div className="border-t border-stone-100 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-stone-700 flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.nombre_completo?.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-stone-800">{user?.nombre_completo}</p>
                <p className="text-xs text-stone-400 capitalize">{user?.rol}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="mt-4 w-full flex items-center px-2 py-2 text-sm font-medium rounded-md text-red-600 hover:bg-red-50"
            >
              <LogOut className="mr-3 h-5 w-5" />
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col lg:bg-white lg:border-r lg:border-stone-100">
        <div className="flex h-16 items-center px-6 border-b border-stone-100">
          <Plane className="h-8 w-8 text-stone-700" />
          <span className="ml-2 text-xl font-bold text-stone-800">IAIM</span>
        </div>
        
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => (
            <button
              key={item.name}
              onClick={() => navigate(item.href)}
              className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md w-full text-left ${
                isActive(item.href)
                  ? 'bg-stone-100 text-stone-800'
                  : 'text-stone-500 hover:text-stone-800 hover:bg-stone-50'
              }`}
            >
              <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
              {item.name}
            </button>
          ))}
        </nav>

        <div className="border-t border-stone-100 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-stone-700 flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {user?.nombre_completo?.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-stone-800">{user?.nombre_completo}</p>
              <p className="text-xs text-stone-400 capitalize">{user?.rol}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="mt-4 w-full flex items-center px-2 py-2 text-sm font-medium rounded-md text-red-600 hover:bg-red-50"
          >
            <LogOut className="mr-3 h-5 w-5" />
            Cerrar Sesión
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        <div className="sticky top-0 z-10 flex h-16 flex-shrink-0 bg-white border-b border-stone-100 lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="px-4 text-stone-400 hover:text-stone-600 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-stone-400"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex flex-1 justify-center items-center px-4">
            <Plane className="h-6 w-6 text-stone-700" />
            <span className="ml-2 text-lg font-semibold text-stone-800">IAIM</span>
          </div>
        </div>

        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
