import { createContext, useContext, useEffect, useState } from 'react'
import axios from 'axios'

const AuthContext = createContext()

const API_BASE_URL = ''

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Verificar token y obtener datos del usuario
      axios
        .get(`${API_BASE_URL}/users/me`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        .then((response) => {
          setUser(response.data)
        })
        .catch(() => {
          // Token inválido, eliminarlo
          localStorage.removeItem('token')
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      const { access_token } = response.data
      
      // Almacenar token en localStorage
      localStorage.setItem('token', access_token)

      // Obtener datos del usuario
      const userResponse = await axios.get(`${API_BASE_URL}/users/me`, {
        headers: { Authorization: `Bearer ${access_token}` },
      })

      setUser(userResponse.data)
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('Credenciales inválidas')
      } else if (error.response?.status === 400) {
        throw new Error('Formato de datos inválido')
      } else {
        throw new Error('Error de conexión con el servidor')
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
