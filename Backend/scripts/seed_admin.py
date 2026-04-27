"""
Seed del primer usuario administrador (idempotente).

Lee las credenciales de variables de entorno y crea el usuario admin
solo si no existe ya (busca por email y por carnet). Si el usuario
ya existe, no hace nada y retorna código 0.

USO LOCAL
---------
    cd Backend
    export ADMIN_EMAIL=admin@iaim.aero
    export ADMIN_PASSWORD='unaClaveMuyLarga!'
    export ADMIN_NAME='Administrador IAIM'
    export ADMIN_CARNET='ADM-001'
    python -m scripts.seed_admin

USO EN RENDER
-------------
1. Ve a tu Web Service > Environment y define las 4 variables ADMIN_*
   (además de las que ya tienes: DATABASE_URL, SECRET_KEY, etc.).
2. Abre la pestaña "Shell" del servicio (Render > tu servicio > Shell).
3. Ejecuta:

       python -m scripts.seed_admin

   Verás "✅ Usuario admin creado" la primera vez, y
   "ℹ️  El usuario admin ya existe, no se hace nada" en ejecuciones
   posteriores. Es seguro correrlo varias veces.

4. Cuando termines, te recomiendo ELIMINAR ADMIN_PASSWORD del
   Environment de Render para no dejar la contraseña en variables.
"""

import os
import sys

from sqlalchemy.orm import Session

from API.database import SessionLocal, engine
from API.models import Base, Usuario
from API.auth import get_password_hash


REQUIRED_VARS = ("ADMIN_EMAIL", "ADMIN_PASSWORD", "ADMIN_NAME", "ADMIN_CARNET")


def _read_env() -> dict:
    """Lee y valida las variables de entorno requeridas."""
    missing = [v for v in REQUIRED_VARS if not os.getenv(v, "").strip()]
    if missing:
        print(
            "❌ Faltan variables de entorno: " + ", ".join(missing),
            file=sys.stderr,
        )
        print(
            "   Defínelas antes de ejecutar el script. Ver docstring para detalles.",
            file=sys.stderr,
        )
        sys.exit(1)

    password = os.environ["ADMIN_PASSWORD"]
    if len(password) < 8:
        print(
            "❌ ADMIN_PASSWORD debe tener al menos 8 caracteres.",
            file=sys.stderr,
        )
        sys.exit(1)

    return {
        "email": os.environ["ADMIN_EMAIL"].strip().lower(),
        "password": password,
        "nombre_completo": os.environ["ADMIN_NAME"].strip(),
        "carnet": os.environ["ADMIN_CARNET"].strip(),
    }


def seed_admin() -> int:
    """Crea el usuario admin si no existe. Retorna exit code (0 = ok)."""
    data = _read_env()

    # Asegura que las tablas existan (no-op si ya están creadas).
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        existing = (
            db.query(Usuario)
            .filter(
                (Usuario.email == data["email"])
                | (Usuario.carnet == data["carnet"])
            )
            .first()
        )

        if existing:
            print(
                f"ℹ️  El usuario admin ya existe (email={existing.email}, "
                f"carnet={existing.carnet}, rol={existing.rol}). No se hace nada."
            )
            return 0

        admin = Usuario(
            nombre_completo=data["nombre_completo"],
            carnet=data["carnet"],
            email=data["email"],
            password_hash=get_password_hash(data["password"]),
            rol="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(
            "✅ Usuario admin creado:\n"
            f"   id:     {admin.id}\n"
            f"   email:  {admin.email}\n"
            f"   carnet: {admin.carnet}\n"
            f"   rol:    {admin.rol}"
        )
        return 0

    except Exception as exc:
        db.rollback()
        print(f"❌ Error al crear el usuario admin: {exc}", file=sys.stderr)
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(seed_admin())
