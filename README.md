# 🛩️ IAIM — Sistema de Gestión de Tickets y Personal

Plataforma web para gestionar reportes de fallas técnicas y personal del Instituto Aeronáutico Internacional de Maiquetía. Acceso por roles (admin, supervisor, técnico), autenticación JWT y dashboards diferenciados.

---

## 🏗️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| **Frontend** | Vite 8 + React 19 (JSX), Tailwind CSS, React Router, Axios |
| **Backend** | FastAPI + SQLAlchemy 2 + python-jose (JWT) + bcrypt |
| **Base de datos** | PostgreSQL (Replit / Render / Neon / Supabase) |
| **Deploy** | Vercel (frontend) + Render (backend) |

```
.
├── Frontend/                # Vite + React (despliega a Vercel)
│   ├── src/
│   │   ├── config.js        # Lee VITE_API_URL
│   │   ├── hooks/useAuth.jsx
│   │   ├── components/
│   │   └── pages/
│   ├── vercel.json          # Rewrites SPA
│   └── .env.example
└── Backend/                 # FastAPI (despliega a Render)
    ├── API/                 # main.py, models, schemas, routers
    ├── Auth/Login/          # endpoint /auth/login
    ├── requirements.txt
    └── .env.example
```

---

## ⚡ Desarrollo local (Replit)

El repo viene preconfigurado con dos workflows:

- **Backend API** → `cd Backend && uvicorn API.main:app --host 0.0.0.0 --port 8000`
- **Start application** → `cd Frontend && npm run dev` (Vite en `:5000`, hace proxy de `/auth`, `/users`, `/tickets` al backend)

### Variables de entorno necesarias en Replit (Secrets)

| Clave | Obligatoria | Descripción |
|---|---|---|
| `DATABASE_URL` | ✅ (auto) | Provista por Replit Postgres |
| `SECRET_KEY` | ✅ | Para firmar JWT. Generar con `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | opcional | Por defecto `60` |
| `FRONTEND_URL` | opcional | Si está vacía, CORS permite cualquier origen (modo dev) |

### Usuario admin de prueba

```
email:    admin@iaim.aero
password: admin12345
```

---

## 💻 Desarrollo local fuera de Replit

```bash
# Backend
cd Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # editar DATABASE_URL y SECRET_KEY
uvicorn API.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (en otra terminal)
cd Frontend
npm install
cp .env.example .env   # dejar VITE_API_URL vacío para usar el proxy de Vite
npm run dev            # http://localhost:5000
```

El proxy de Vite (`vite.config.js`) reenvía `/auth`, `/users`, `/tickets`, `/docs` y `/openapi.json` al backend en `http://localhost:8000` durante desarrollo.

---

## 🚀 Despliegue a Producción

### 🟦 Backend en Render

1. Crea un servicio nuevo: **New → Web Service** y conecta tu repo de GitHub.
2. Configuración:
   | Campo | Valor |
   |---|---|
   | Root Directory | `Backend` |
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn API.main:app --host 0.0.0.0 --port $PORT` |
3. Agrega un **PostgreSQL** desde Render (o usa Neon/Supabase) y copia el `Internal Database URL`.
4. En **Environment**, define:
   | Clave | Valor |
   |---|---|
   | `DATABASE_URL` | URL del Postgres |
   | `SECRET_KEY` | Tu clave aleatoria (mínimo 64 chars) |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
   | `FRONTEND_URL` | (déjala vacía hasta tener la URL de Vercel) |
   | `PYTHON_VERSION` | `3.12` |
5. Despliega. Anota la URL pública (ej. `https://iaim-backend.onrender.com`).

### 🟪 Frontend en Vercel

1. **Import Project** desde GitHub.
2. Configuración:
   | Campo | Valor |
   |---|---|
   | Framework Preset | Vite (autodetectado) |
   | Root Directory | `Frontend` |
   | Build Command | `npm run build` (autodetectado) |
   | Output Directory | `dist` (autodetectado) |
3. En **Environment Variables**:
   | Clave | Valor |
   |---|---|
   | `VITE_API_URL` | URL del backend en Render, sin slash final |
4. Despliega. Anota la URL pública (ej. `https://iaim.vercel.app`).

### 🔁 Cerrar el círculo (CORS)

Vuelve a Render → Environment y define:
```
FRONTEND_URL=https://iaim.vercel.app
```
Esto bloquea CORS a tu dominio de Vercel y activa `allow_credentials=True`. Render reiniciará el servicio automáticamente.

> 💡 Si tienes preview deployments en Vercel y necesitas que también funcionen, puedes pasar varias URLs separadas por coma:  
> `FRONTEND_URL=https://iaim.vercel.app,https://iaim-staging.vercel.app`

### 🗄️ Inicializar la base de datos en producción

FastAPI crea las tablas automáticamente la primera vez que arranca (`models.Base.metadata.create_all`). Para crear el usuario admin inicial, conéctate al Postgres y ejecuta:

```sql
INSERT INTO usuarios (id, nombre_completo, carnet, email, password_hash, rol)
VALUES (
  gen_random_uuid()::text,
  'Administrador IAIM',
  'ADM-001',
  'admin@iaim.aero',
  -- Genera el hash en local: python -c "import bcrypt; print(bcrypt.hashpw(b'TU_PASSWORD', bcrypt.gensalt()).decode())"
  '$2b$12$...',
  'admin'
);
```

---

## 📡 Endpoints principales

| Método | Ruta | Acceso |
|---|---|---|
| `POST` | `/auth/login` | Público (form: `username`, `password`) |
| `GET` | `/users/me` | Autenticado |
| `GET` | `/users` | admin, supervisor |
| `POST` | `/users` | admin |
| `PUT` / `DELETE` | `/users/{id}` | admin |
| `GET` | `/tickets` | admin/supervisor (todos), técnico (propios) |
| `POST` | `/tickets` | autenticado |
| `PUT` / `PATCH` | `/tickets/{id}` | admin, técnico |
| `DELETE` | `/tickets/{id}` | admin |

Documentación interactiva en `/docs` (Swagger UI) y `/redoc`.

---

## 🛡️ Seguridad

- Contraseñas hasheadas con **bcrypt**.
- JWT firmados con `SECRET_KEY` (HS256).
- Validación de payloads con **Pydantic v2**.
- CORS restringido por `FRONTEND_URL` en producción.
- Variables sensibles **siempre** en variables de entorno (nunca en el repo).
- ORM SQLAlchemy → previene SQL injection.

---

## 🧰 Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| `401` en `/users/me` tras login | Token no se está enviando | Revisar `Authorization: Bearer ...` en headers |
| `CORS error` en navegador | `FRONTEND_URL` mal configurada en Render | Asegurarse de que coincide exactamente con la URL de Vercel (con `https://`, sin slash final) |
| `500` y `psycopg2.OperationalError` | `DATABASE_URL` mal o DB caída | Verificar credenciales y que el Postgres acepta conexiones externas |
| `Module not found: python-jose` | `requirements.txt` desactualizado | Reinstalar con `pip install -r requirements.txt` |
| El frontend en Vercel hace requests a su propio dominio | `VITE_API_URL` no está set | Definirla en Vercel y **redeploy** (las VITE_ se inyectan en build time) |
| Render free tier "duerme" después de 15 min | Comportamiento esperado del plan gratuito | Primer request tras inactividad tarda ~30 s; usar plan paid o un cron de keepalive |

---

## 📝 Licencia

Uso interno — Instituto Aeronáutico Internacional de Maiquetía.
