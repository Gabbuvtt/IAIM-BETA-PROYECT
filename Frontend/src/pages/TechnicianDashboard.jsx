import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { API_BASE_URL } from '../config'
import StatsCard from '../components/StatsCard'
import TicketsTable from '../components/TicketsTable'
import TicketForm from '../components/TicketForm'
import { Plane, AlertCircle, Plus, Wrench } from 'lucide-react'

export default function TechnicianDashboard() {
  const { user, isAuthenticated } = useAuth()
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showTicketForm, setShowTicketForm] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) return
    if (user && user.rol !== 'tecnico') return

    fetchMyTickets()
  }, [isAuthenticated, user])

  const fetchMyTickets = async () => {
    try {
      const token = localStorage.getItem('token') || ''
      
      const response = await fetch(`${API_BASE_URL}/tickets`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.ok) {
        const ticketsData = await response.json()
        // Filtrar solo tickets del usuario actual
        const myTickets = ticketsData.filter(ticket => ticket.usuario_id === user?.id)
        setTickets(myTickets)
      }
    } catch (error) {
      console.error('Error fetching tickets:', error)
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

  const handleTicketCreated = () => {
    setShowTicketForm(false)
    fetchMyTickets()
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Panel Técnico</h1>
          <p className="text-secondary-600 mt-2">
            Gestión de reportes de fallas y mantenimiento
          </p>
        </div>
        <button
          onClick={() => setShowTicketForm(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nuevo Ticket
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Mis Tickets"
          value={stats.total}
          icon={<Wrench className="h-6 w-6" />}
          color="primary"
        />
        <StatsCard
          title="Abiertos"
          value={stats.open}
          icon={<AlertCircle className="h-6 w-6" />}
          color="accent"
        />
        <StatsCard
          title="En Progreso"
          value={stats.inProgress}
          icon={<Plane className="h-6 w-6" />}
          color="secondary"
        />
        <StatsCard
          title="Resueltos"
          value={stats.resolved}
          icon={<Plus className="h-6 w-6" />}
          color="green"
        />
      </div>

      {/* Ticket Form Modal */}
      {showTicketForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-secondary-900 bg-opacity-75">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-secondary-900">Nuevo Ticket</h2>
              <button
                onClick={() => setShowTicketForm(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>
            <TicketForm 
              onSuccess={handleTicketCreated}
              onCancel={() => setShowTicketForm(false)}
            />
          </div>
        </div>
      )}

      {/* My Tickets */}
      <div className="animate-fade-in">
        <TicketsTable 
          tickets={tickets} 
          isAdmin={false}
          onUpdate={fetchMyTickets}
        />
      </div>
    </div>
  )
}
