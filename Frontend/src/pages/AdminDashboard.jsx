import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import StatsCard from '../components/StatsCard'
import TicketsTable from '../components/TicketsTable'
import UsersTable from '../components/UsersTable'
import { Plane, Users, AlertCircle, CheckCircle } from 'lucide-react'

export default function AdminDashboard() {
  const { user, isAuthenticated } = useAuth()
  const [tickets, setTickets] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('tickets')

  useEffect(() => {
    if (!isAuthenticated) return
    if (user && !['admin', 'supervisor'].includes(user.rol)) return

    fetchData()
  }, [isAuthenticated, user])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token') || ''
      
      // Fetch tickets and users in parallel
      const [ticketsResponse, usersResponse] = await Promise.all([
        fetch('/tickets', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('/users', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ])

      if (ticketsResponse.ok && usersResponse.ok) {
        const [ticketsData, usersData] = await Promise.all([
          ticketsResponse.json(),
          usersResponse.json(),
        ])
        setTickets(ticketsData)
        setUsers(usersData)
      }
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStats = () => {
    const stats = {
      total: tickets.length,
      open: tickets.filter(t => t.estado === 'abierto').length,
      inProgress: tickets.filter(t => t.estado === 'en_progreso').length,
      resolved: tickets.filter(t => t.estado === 'resuelto' || t.estado === 'cerrado').length,
    }
    return stats
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const stats = getStats()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Panel Administrativo</h1>
        <p className="text-secondary-600 mt-2">
          Gestión de tickets y personal del sistema IAIM
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Tickets"
          value={stats.total}
          icon={<Plane className="h-6 w-6" />}
          color="primary"
        />
        <StatsCard
          title="Tickets Abiertos"
          value={stats.open}
          icon={<AlertCircle className="h-6 w-6" />}
          color="accent"
        />
        <StatsCard
          title="En Progreso"
          value={stats.inProgress}
          icon={<Users className="h-6 w-6" />}
          color="secondary"
        />
        <StatsCard
          title="Resueltos"
          value={stats.resolved}
          icon={<CheckCircle className="h-6 w-6" />}
          color="green"
        />
      </div>

      {/* Tabs */}
      <div className="border-b border-secondary-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('tickets')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'tickets'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
            }`}
          >
            Tickets ({stats.total})
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
            }`}
          >
            Usuarios ({users.length})
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="animate-fade-in">
        {activeTab === 'tickets' ? (
          <TicketsTable 
            tickets={tickets} 
            isAdmin={true}
            onUpdate={fetchData}
          />
        ) : (
          <UsersTable 
            users={users}
            onUpdate={fetchData}
          />
        )}
      </div>
    </div>
  )
}
