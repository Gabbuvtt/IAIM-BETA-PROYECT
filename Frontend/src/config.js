// Configuración compartida del cliente.
// VITE_API_URL apunta al backend desplegado (por ejemplo, en Render).
// En desarrollo local en Replit la dejamos vacía: vite.config.js hace proxy
// de /auth, /users y /tickets hacia el backend interno (http://localhost:8000).
export const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '')

// Construye una URL absoluta o relativa según haya VITE_API_URL.
export function apiUrl(path = '') {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${normalized}`
}
