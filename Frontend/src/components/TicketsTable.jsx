import { useState } from 'react'
import toast from 'react-hot-toast'
import { Edit, Trash2, Eye, Clock, CheckCircle, AlertTriangle } from 'lucide-react'

export default function TicketsTable({ tickets, isAdmin, onUpdate }) {
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [showDetails, setShowDetails] = useState(false)

  const getStatusIcon = (status) => {
    switch (status) {
      case 'abierto':
        return <AlertTriangle className="h-4 w-4 text-accent-600" />
      case 'en_progreso':
        return <Clock className="h-4 w-4 text-primary-600" />
      case 'resuelto':
      case 'cerrado':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      default:
        return null
    }
  }

  const getStatusBadge = (status) => {
    const statusClasses = {
      abierto: 'bg-accent-100 text-accent-800',
      en_progreso: 'bg-primary-100 text-primary-800',
      resuelto: 'bg-green-100 text-green-800',
      cerrado: 'bg-gray-100 text-gray-800',
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClasses[status]}`}>
        {getStatusIcon(status)}
        <span className="ml-1">{status.replace('_', ' ').toUpperCase()}</span>
      </span>
    )
  }

  const getPriorityBadge = (priority) => {
    const priorityClasses = {
      baja: 'bg-gray-100 text-gray-800',
      media: 'bg-yellow-100 text-yellow-800',
      alta: 'bg-orange-100 text-orange-800',
      critica: 'bg-accent-100 text-accent-800',
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityClasses[priority]}`}>
        {priority.toUpperCase()}
      </span>
    )
  }

  const handleUpdateStatus = async (ticketId, newStatus) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8001/tickets/${ticketId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ estado: newStatus }),
      })

      if (response.ok) {
        toast.success('Estado actualizado correctamente')
        onUpdate()
      } else {
        throw new Error('Error al actualizar estado')
      }
    } catch (error) {
      toast.error(error.message)
    }
  }

  const handleDelete = async (ticketId) => {
    if (!confirm('¿Estás seguro de que deseas eliminar este ticket?')) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8001/tickets/${ticketId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        toast.success('Ticket eliminado correctamente')
        onUpdate()
      } else {
        throw new Error('Error al eliminar ticket')
      }
    } catch (error) {
      toast.error(error.message)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString || dateString === 'Invalid Date') return 'Sin fecha'
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Sin fecha'
    
    const datePart = date.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timeZone: 'UTC'
    })
    const timePart = date.toLocaleTimeString('es-MX', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'UTC'
    })
    return `${datePart} • ${timePart}`
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-secondary-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-secondary-200">
          <thead className="bg-secondary-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Asunto
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Prioridad
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Fecha
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-secondary-200">
            {tickets.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-secondary-500">
                  No hay tickets registrados
                </td>
              </tr>
            ) : (
              tickets.map((ticket) => (
                <tr key={ticket.id} className="hover:bg-secondary-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                    #{ticket.id}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-secondary-900">{ticket.asunto}</div>
                    <div className="text-sm text-secondary-500 truncate max-w-xs">
                      {ticket.descripcion}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getPriorityBadge(ticket.prioridad)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(ticket.estado)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                    {formatDate(ticket.fecha_creacion)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setSelectedTicket(ticket)
                          setShowDetails(true)
                        }}
                        className="text-primary-600 hover:text-primary-900"
                        title="Ver detalles"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      
                      {isAdmin && (
                        <>
                          <button
                            onClick={() => handleUpdateStatus(ticket.id, 
                              ticket.estado === 'abierto' ? 'en_progreso' : 
                              ticket.estado === 'en_progreso' ? 'resuelto' : 'abierto'
                            )}
                            className="text-secondary-600 hover:text-secondary-900"
                            title="Cambiar estado"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          
                          <button
                            onClick={() => handleDelete(ticket.id)}
                            className="text-accent-600 hover:text-accent-900"
                            title="Eliminar ticket"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Details Modal */}
      {showDetails && selectedTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-secondary-900 bg-opacity-75">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-2xl mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-secondary-900">
                Detalles del Ticket #{selectedTicket.id}
              </h2>
              <button
                onClick={() => setShowDetails(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-secondary-900">Asunto</h3>
                <p className="text-secondary-600">{selectedTicket.asunto}</p>
              </div>
              
              <div>
                <h3 className="font-medium text-secondary-900">Descripción</h3>
                <p className="text-secondary-600 whitespace-pre-wrap">{selectedTicket.descripcion}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium text-secondary-900">Prioridad</h3>
                  {getPriorityBadge(selectedTicket.prioridad)}
                </div>
                <div>
                  <h3 className="font-medium text-secondary-900">Estado</h3>
                  {getStatusBadge(selectedTicket.estado)}
                </div>
              </div>
              
              <div>
                <h3 className="font-medium text-secondary-900">Fecha de Creación</h3>
                <p className="text-secondary-600">{formatDate(selectedTicket.fecha_creacion)}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
