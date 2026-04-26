import { useState } from 'react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'

export default function TicketForm({ onSuccess, onCancel }) {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  const onSubmit = async (data) => {
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const ticketData = {
        ...data,
        usuario_id: user.id,
        prioridad: data.prioridad || 'media',
      }

      const response = await fetch('http://localhost:8001/tickets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(ticketData),
      })

      if (response.ok) {
        toast.success('Ticket creado correctamente')
        onSuccess()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error al crear ticket')
      }
    } catch (error) {
      toast.error(error.message || 'Error de conexión con el servidor')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="asunto" className="block text-sm font-medium text-secondary-700 mb-2">
          Asunto del Ticket *
        </label>
        <input
          {...register('asunto', {
            required: 'El asunto es requerido',
            maxLength: {
              value: 200,
              message: 'El asunto no puede exceder 200 caracteres',
            },
          })}
          type="text"
          className={`w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
            errors.asunto ? 'border-accent-500' : ''
          }`}
          placeholder="Ej: Falla en sistema de navegación"
        />
        {errors.asunto && (
          <p className="mt-1 text-sm text-accent-600">{errors.asunto.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="descripcion" className="block text-sm font-medium text-secondary-700 mb-2">
          Descripción Detallada *
        </label>
        <textarea
          {...register('descripcion', {
            required: 'La descripción es requerida',
            minLength: {
              value: 10,
              message: 'La descripción debe tener al menos 10 caracteres',
            },
          })}
          rows={6}
          className={`w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
            errors.descripcion ? 'border-accent-500' : ''
          }`}
          placeholder="Describe detalladamente la falla o problema detectado..."
        />
        {errors.descripcion && (
          <p className="mt-1 text-sm text-accent-600">{errors.descripcion.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="prioridad" className="block text-sm font-medium text-secondary-700 mb-2">
          Prioridad
        </label>
        <select
          {...register('prioridad')}
          className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
        >
          <option value="baja">Baja</option>
          <option value="media" selected>Media</option>
          <option value="alta">Alta</option>
          <option value="critica">Crítica</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="ubicacion" className="block text-sm font-medium text-secondary-700 mb-2">
            Ubicación
          </label>
          <input
            {...register('ubicacion')}
            type="text"
            className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
            placeholder="Ej: Terminal A, Puerta 12"
          />
        </div>

        <div>
          <label htmlFor="equipo_afectado" className="block text-sm font-medium text-secondary-700 mb-2">
            Equipo Afectado
          </label>
          <input
            {...register('equipo_afectado')}
            type="text"
            className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
            placeholder="Ej: Sistema de radar, GPS, etc."
          />
        </div>
      </div>

      <div className="bg-secondary-50 border border-secondary-200 rounded-lg p-4">
        <h4 className="font-medium text-secondary-900 mb-2">Información del Reportante</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-secondary-500">Nombre:</span>
            <span className="ml-2 text-secondary-900">{user?.nombre_completo}</span>
          </div>
          <div>
            <span className="text-secondary-500">Carnet:</span>
            <span className="ml-2 text-secondary-900">{user?.carnet}</span>
          </div>
        </div>
      </div>

      <div className="flex space-x-3 pt-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Creando Ticket...
            </div>
          ) : (
            'Crear Ticket'
          )}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 bg-secondary-200 hover:bg-secondary-300 text-secondary-800 font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
