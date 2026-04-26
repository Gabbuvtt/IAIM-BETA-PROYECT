import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'
import { Plane } from 'lucide-react'

export default function LoginForm() {
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  const onSubmit = async (data) => {
    setLoading(true)
    
    try {
      await login(data.email, data.password)
      toast.success('Inicio de sesión exitoso')
      
      // La navegación será manejada por el componente App
      setTimeout(() => {
        navigate(0) // Forzar re-render para redirección
      }, 1000)
    } catch (error) {
      toast.error(error.message || 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-stone-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-stone-800 rounded-full flex items-center justify-center mb-6">
            <Plane className="h-8 w-8 text-stone-100" />
          </div>
          <h2 className="text-3xl font-bold text-stone-800">
            Sistema de Gestión
          </h2>
          <p className="mt-2 text-stone-500">
            Sistema de gestión de tickets y personal para aeropuertos
          </p>
        </div>
        
        <div className="bg-white rounded-lg border border-stone-200 p-6 shadow-soft">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-stone-600 mb-2">
                Correo Electrónico
              </label>
              <input
                {...register('email', {
                  required: 'El correo electrónico es requerido',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Formato de correo inválido',
                  },
                })}
                type="email"
                autoComplete="email"
                className={`w-full px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-1 focus:ring-stone-400 focus:border-stone-400 transition-all duration-200 ${
                  errors.email ? 'border-red-400' : ''
                }`}
                placeholder="correo@ejemplo.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-stone-600 mb-2">
                Contraseña
              </label>
              <input
                {...register('password', {
                  required: 'La contraseña es requerida',
                  minLength: {
                    value: 6,
                    message: 'La contraseña debe tener al menos 6 caracteres',
                  },
                })}
                type="password"
                autoComplete="current-password"
                className={`w-full px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-1 focus:ring-stone-400 focus:border-stone-400 transition-all duration-200 ${
                  errors.password ? 'border-red-400' : ''
                }`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-stone-800 hover:bg-stone-900 text-white font-medium py-2 px-4 rounded-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Iniciando sesión...
                  </div>
                ) : (
                  'Iniciar Sesión'
                )}
              </button>
            </div>
          </form>
        </div>
        
        <div className="text-center text-sm text-stone-400">
          <p>Instituto Aeropuerto Internacional de Maiquetía</p>
          <p className="mt-1">Portal de Gestión Técnica</p>
        </div>
      </div>
    </div>
  )
}
