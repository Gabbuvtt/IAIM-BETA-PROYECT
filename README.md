# 🛩️ IAIM - Sistema de Gestión de Tickets y Personal

**Sistema integral de gestión de tickets y personal para el Instituto Aeronáutico Internacional de México**

---

## 📋 Descripción del Proyecto

El Sistema de Gestión IAIM es una plataforma web moderna diseñada para optimizar la gestión de reportes de fallas técnicas y la administración de personal en entornos aeroportuarios. El sistema proporciona una interfaz intuitiva para técnicos, supervisores y administradores, permitiendo un flujo eficiente de trabajo y comunicación.

### 🎯 Objetivos Principales

- **Gestión Centralizada**: Control unificado de tickets de mantenimiento y personal
- **Flujo de Trabajo Optimizado**: Procesos claros para reporte, asignación y resolución de incidencias
- **Acceso Rol-Based**: Interfaces adaptadas según el rol de usuario (Técnico, Supervisor, Administrador)
- **Seguridad Robusta**: Autenticación JWT y gestión de permisos granular
- **Escalabilidad**: Arquitectura moderna basada en microservicios

---

## 🏗️ Arquitectura Tecnológica

### Backend (FastAPI + Python)
```
Backend/
├── API/
│   ├── main.py              # Aplicación principal FastAPI
│   ├── models.py            # Modelos de datos SQLAlchemy
│   ├── schemas.py           # Esquemas Pydantic para validación
│   ├── database.py          # Configuración de base de datos
│   ├── auth.py              # Sistema de autenticación JWT
│   └── routers/             # Endpoints organizados por módulo
│       ├── users.py         # Gestión de usuarios
│       └── tickets.py       # Gestión de tickets
├── Auth/
│   └── Login/
│       └── login.py         # Endpoint de autenticación
├── .env.example             # Variables de entorno ejemplo
└── requirements.txt         # Dependencias Python
```

### Frontend (Next.js + React + TypeScript)
```
Frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx         # Página principal (Login)
│   │   ├── admin/           # Dashboard administrativo
│   │   └── tecnico/         # Dashboard técnico
│   ├── components/
│   │   ├── LoginForm.tsx    # Formulario de login
│   │   ├── DashboardLayout.tsx # Layout principal
│   │   ├── StatsCard.tsx    # Tarjetas de estadísticas
│   │   ├── TicketsTable.tsx # Tabla de tickets
│   │   └── UsersTable.tsx   # Tabla de usuarios
│   ├── hooks/
│   │   └── useAuth.tsx      # Hook de autenticación
│   └── globals.css          # Estilos globales Tailwind
├── package.json            # Dependencias Node.js
├── tailwind.config.js       # Configuración Tailwind CSS
└── tsconfig.json            # Configuración TypeScript
```

### Base de Datos (PostgreSQL + Supabase)
- **PostgreSQL** como motor de base de datos principal
- **Supabase** como servicio de hosting y gestión
- **Pool de conexiones** configurado para alta disponibilidad

---

## 🚀 Instalación y Configuración

### Prerrequisitos
- Node.js 18+ 
- Python 3.9+
- PostgreSQL (o cuenta de Supabase)
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/iaim-sistema-gestion.git
cd iaim-sistema-gestion
```

### 2. Configurar Backend
```bash
cd Backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase
```

### 3. Configurar Base de Datos
```bash
# En tu archivo .env:
DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
SECRET_KEY="tu-clave-segura-aqui"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Iniciar Backend
```bash
cd Backend
python -m uvicorn API.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Configurar Frontend
```bash
cd Frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Iniciar servidor de desarrollo
npm run dev
```

---

## 📊 Características Principales

### 🔐 Sistema de Autenticación
- **JWT Tokens** para sesión segura
- **Gestión de Cookies** con configuración de seguridad
- **Roles de Usuario**: Admin, Supervisor, Técnico
- **Redirección Automática** según rol

### 🎫 Gestión de Tickets
- **Creación de Tickets**: Reporte de fallas con prioridad y descripción
- **Estados**: Abierto, En Progreso, Resuelto, Cerrado
- **Prioridades**: Baja, Media, Alta, Crítica
- **Asignación Automática** al usuario que crea el ticket
- **Actualizaciones Parciales** (PATCH) para cambios rápidos

### 👥 Gestión de Usuarios
- **Registro de Personal**: Nombre, Carnet, Email, Rol
- **Validación de Email Único**
- **Gestión de Contraseñas** con hashing bcrypt
- **CRUD Completo** para administradores

### 📈 Dashboard Administrativo
- **Estadísticas en Tiempo Real**
- **Tablas Interactivas** con paginación
- **Indicadores Visuales** de estado
- **Gestión Multi-Tab** (Tickets/Usuarios)

### 🛠️ Dashboard Técnico
- **Vista Simplificada** para técnicos
- **Mis Tickets**: Solo tickets propios
- **Reporte Rápido** de nuevas fallas
- **Estado Actualizado** en tiempo real

---

## 🎨 Diseño UI/UX

### Identidad Visual Aeronáutica
- **Paleta de Colores Institucional**: Azul primario, grises técnicos, blancos
- **Tipografía Moderna**: Inter para legibilidad óptima
- **Iconografía Consistente**: Lucide React para iconos uniformes
- **Diseño Responsive**: Mobile-first approach

### Componentes Reutilizables
- **Cards** con sombras sutiles y bordes redondeados
- **Badges** de estado con colores semánticos
- **Botones** con estados hover y loading
- **Formularios** con validación en tiempo real
- **Tablas** con ordenamiento y filtros

---

## 🔧 Endpoints de la API

### Autenticación
- `POST /auth/login` - Inicio de sesión
- `GET /users/me` - Obtener usuario actual

### Usuarios
- `GET /users` - Listar todos los usuarios (Admin/Supervisor)
- `POST /users` - Crear nuevo usuario (Admin)
- `PUT /users/{id}` - Actualizar usuario (Admin)
- `DELETE /users/{id}` - Eliminar usuario (Admin)

### Tickets
- `GET /tickets` - Listar tickets (según rol)
- `POST /tickets` - Crear nuevo ticket
- `PUT /tickets/{id}` - Actualizar ticket completo
- `PATCH /tickets/{id}` - Actualización parcial
- `DELETE /tickets/{id}` - Eliminar ticket (Admin)

---

## 🛡️ Seguridad

### Implementaciones de Seguridad
- **Hashing de Contraseñas** con bcrypt
- **JWT Tokens** con expiración configurable
- **Validación de Entradas** con Pydantic
- **CORS Configurado** para dominios específicos
- **Variables de Entorno** para credenciales
- **SQLAlchemy ORM** para prevención de SQL Injection

### Mejores Prácticas
- **Principio de Mínimo Privilegio** en roles
- **Cookies Seguras** (HttpOnly, Secure, SameSite)
- **Validación del Lado Servidor** y cliente
- **Manejo de Errores** sin exposición de datos sensibles

---

## 🚀 Despliegue

### Producción - Backend
```bash
# Usando Docker
docker build -t iaim-backend .
docker run -p 8000:8000 iaim-backend

# O directamente con Uvicorn
uvicorn API.main:app --host 0.0.0.0 --port 8000
```

### Producción - Frontend
```bash
# Construir para producción
npm run build

# Iniciar servidor de producción
npm start
```

### Variables de Entorno Producción
```bash
DATABASE_URL="postgresql://..."
SECRET_KEY="clave-super-segura-produccion"
ACCESS_TOKEN_EXPIRE_MINUTES=60
NEXT_PUBLIC_API_URL="https://api.tu-dominio.com"
```

---

## 📝 Desarrollo

### Scripts Útiles
```bash
# Backend
pip install -r requirements.txt    # Instalar dependencias
python -m pytest                  # Ejecutar tests
uvicorn API.main:app --reload     # Desarrollo con auto-reload

# Frontend
npm install                       # Instalar dependencias
npm run dev                      # Desarrollo
npm run build                    # Build producción
npm run lint                     # Linter ESLint
```

### Extensiones VSCode Recomendadas
- Python (Microsoft)
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Prettier - Code formatter
- TypeScript Importer

---

## 🤝 Contribuir

1. **Fork** el repositorio
2. **Crear rama** de feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abrir Pull Request**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Soporte

Para soporte técnico o preguntas:

- **Email**: soporte@iaim.aero
- **Documentación**: [Wiki del Proyecto](https://github.com/tu-usuario/iaim-sistema-gestion/wiki)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/iaim-sistema-gestion/issues)

---

## 🏆 Créditos

Desarrollado para el **Instituto Aeronáutico Internacional de México (IAIM)**

- **Arquitectura Backend**: FastAPI + SQLAlchemy
- **Frontend Moderno**: Next.js + React + Tailwind CSS
- **Base de Datos**: PostgreSQL + Supabase
- **Diseño UI/UX**: Sistema de diseño aeronáutico institucional

---

**© 2024 Instituto Aeronáutico Internacional de México - Todos los derechos reservados**
