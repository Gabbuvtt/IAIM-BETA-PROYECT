import { useState } from 'react'
import toast from 'react-hot-toast'
import { Edit, Trash2, Shield, UserCheck, Wrench } from 'lucide-react'

export default function UsersTable({ users, onUpdate }) {
  const [selectedUser, setSelectedUser] = useState(null)
  const [showEditForm, setShowEditForm] = useState(false)

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <Shield className="h-4 w-4 text-accent-600" />
      case 'supervisor':
        return <UserCheck className="h-4 w-4 text-primary-600" />
      case 'tecnico':
        return <Wrench className="h-4 w-4 text-secondary-600" />
      default:
        return null
    }
  }

  const getRoleBadge = (role) => {
    const roleClasses = {
      admin: 'bg-accent-100 text-accent-800',
      supervisor: 'bg-primary-100 text-primary-800',
      tecnico: 'bg-secondary-100 text-secondary-800',
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${roleClasses[role]}`}>
        {getRoleIcon(role)}
        <span className="ml-1">{role.toUpperCase()}</span>
      </span>
    )
  }

  const handleDelete = async (userId) => {
    if (!confirm('¿Estás seguro de que deseas eliminar este usuario? Esta acción no se puede deshacer.')) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8001/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        toast.success('Usuario eliminado correctamente')
        onUpdate()
      } else {
        throw new Error('Error al eliminar usuario')
      }
    } catch (error) {
      toast.error(error.message)
    }
  }

  const handleEdit = (user) => {
    setSelectedUser(user)
    setShowEditForm(true)
  }

  const handleUserUpdated = () => {
    setShowEditForm(false)
    setSelectedUser(null)
    onUpdate()
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-secondary-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-secondary-200">
          <thead className="bg-secondary-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Carnet
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Nombre
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Rol
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-secondary-200">
            {users.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center text-secondary-500">
                  No hay usuarios registrados
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id} className="hover:bg-secondary-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-secondary-900">
                    {user.carnet}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-secondary-900">{user.nombre_completo}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-secondary-600">{user.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getRoleBadge(user.rol)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(user)}
                        className="text-primary-600 hover:text-primary-900"
                        title="Editar usuario"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      
                      <button
                        onClick={() => handleDelete(user.id)}
                        className="text-accent-600 hover:text-accent-900"
                        title="Eliminar usuario"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Edit User Modal */}
      {showEditForm && selectedUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-secondary-900 bg-opacity-75">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-secondary-900">
                Editar Usuario
              </h2>
              <button
                onClick={() => setShowEditForm(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>
            
            <UserForm 
              user={selectedUser}
              onSuccess={handleUserUpdated}
              onCancel={() => setShowEditForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}

// Componente UserForm para editar usuarios
function UserForm({ user, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    nombre_completo: user?.nombre_completo || '',
    carnet: user?.carnet || '',
    email: user?.email || '',
    rol: user?.rol || 'tecnico',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8001/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        toast.success('Usuario actualizado correctamente')
        onSuccess()
      } else {
        throw new Error('Error al actualizar usuario')
      }
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-secondary-700 mb-2">
          Nombre Completo
        </label>
        <input
          type="text"
          name="nombre_completo"
          value={formData.nombre_completo}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-secondary-700 mb-2">
          Carnet
        </label>
        <input
          type="text"
          name="carnet"
          value={formData.carnet}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-secondary-700 mb-2">
          Email
        </label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-secondary-700 mb-2">
          Rol
        </label>
        <select
          name="rol"
          value={formData.rol}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="tecnico">Técnico</option>
          <option value="supervisor">Supervisor</option>
          <option value="admin">Administrador</option>
        </select>
      </div>

      <div className="flex space-x-3 pt-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Guardando...' : 'Guardar Cambios'}
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
