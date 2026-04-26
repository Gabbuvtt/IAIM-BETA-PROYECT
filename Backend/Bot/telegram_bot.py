import logging
import httpx
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

# Configuración de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIGURACIÓN ---
TOKEN_TELEGRAM = "8696211885:AAFqPo5A2TEsi-0vuX99Xst6s6CpE-bEwGU"
BASE_URL_API = "http://127.0.0.1:8001"

# Estados de la conversación
EMAIL, PASSWORD, ASUNTO, DESCRIPCION = range(4)

# Memoria del bot: { telegram_id: {"token": "...", "rol": "...", "nombre": "..."} }
user_sessions = {}

# ==========================================
# UTILIDADES Y MENÚS
# ==========================================

def obtener_teclado(rol):
    """Genera botones según el rango del usuario"""
    if rol == "admin":
        return [
            ["/reportar", "/mis_tickets"],
            ["/ver_todo", "/usuarios"],
            ["/cerrar", "/logout"]
        ]
    elif rol == "supervisor":
        return [["/ver_todo"], ["/logout"]]
    else:  # técnico
        return [["/reportar", "/mis_tickets"], ["/logout"]]

# ==========================================
# COMANDOS DE ADMINISTRACIÓN
# ==========================================

async def cerrar_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permite al admin cerrar un ticket por su ID"""
    t_id = update.effective_user.id
    if t_id not in user_sessions or user_sessions[t_id]['rol'] != "admin":
        await update.message.reply_text("🚫 Solo los administradores pueden cerrar tickets.")
        return

    # Validar si el usuario proporcionó el ID después del comando
    if not context.args:
        await update.message.reply_text(
            "⚠️ **Uso:** Escribe `/cerrar` seguido del número del ticket.\n"
            "Ejemplo: `/cerrar 4`", 
            parse_mode="Markdown"
        )
        return

    ticket_id = context.args[0].replace("#", "") # Limpiamos por si el usuario pone #4
    headers = {"Authorization": f"Bearer {user_sessions[t_id]['token']}"}
    payload = {"estado": "resuelto"}
    
    async with httpx.AsyncClient() as client:
        try:
            # INTENTO 1: PATCH (Actualización parcial)
            res = await client.patch(f"{BASE_URL_API}/tickets/{ticket_id}", json=payload, headers=headers)
            
            # Si da Error 405 (Método no permitido), intentamos con PUT
            if res.status_code == 405:
                res = await client.put(f"{BASE_URL_API}/tickets/{ticket_id}", json=payload, headers=headers)
            
            if res.status_code == 200:
                await update.message.reply_text(f"✅ ¡Ticket #{ticket_id} cerrado con éxito!")
            elif res.status_code == 404:
                await update.message.reply_text(f"❌ El ticket #{ticket_id} no existe.")
            elif res.status_code == 403:
                await update.message.reply_text("🚫 No tienes permisos suficientes en el Backend.")
            else:
                await update.message.reply_text(f"❌ Error {res.status_code}: No se pudo completar la acción.")
                
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error de conexión: {e}")

async def ver_todos_los_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_id = update.effective_user.id
    if t_id not in user_sessions or user_sessions[t_id]['rol'] not in ["admin", "supervisor"]:
        await update.message.reply_text("🚫 No tienes permisos para ver la vista global.")
        return

    headers = {"Authorization": f"Bearer {user_sessions[t_id]['token']}"}
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{BASE_URL_API}/tickets/", headers=headers)
            if res.status_code == 200:
                tickets = res.json()
                if not tickets:
                    await update.message.reply_text("No hay tickets en el sistema.")
                    return
                mensaje = "🌎 **VISTA GLOBAL DE TICKETS:**\n\n"
                for t in tickets:
                    icon = "🟢" if t['estado'] == "resuelto" else "🔴"
                    mensaje += f"{icon} #{t['id']} | {t['asunto']} (`{t['estado']}`)\n"
                await update.message.reply_text(mensaje, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")

async def ver_usuarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_id = update.effective_user.id
    if t_id not in user_sessions or user_sessions[t_id]['rol'] != "admin":
        await update.message.reply_text("🚫 Acceso restringido.")
        return

    headers = {"Authorization": f"Bearer {user_sessions[t_id]['token']}"}
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{BASE_URL_API}/users/", headers=headers)
            if res.status_code == 200:
                usuarios = res.json()
                mensaje = "👥 **Personal Registrado:**\n\n"
                for u in usuarios:
                    mensaje += f"👤 {u['nombre_completo']} — `{u['rol'].upper()}`\n"
                await update.message.reply_text(mensaje, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")

# ==========================================
# LOGUEO Y REPORTES
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✈️ Sistema IAIM activo. Usa /login para comenzar.")

async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📧 Correo:")
    return EMAIL

async def procesar_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("🔑 Contraseña:")
    return PASSWORD

async def procesar_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = context.user_data.get("email")
    password = update.message.text
    t_id = update.effective_user.id

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            login_res = await client.post(f"{BASE_URL_API}/auth/login", data={"username": email, "password": password})
            
            if login_res.status_code == 200:
                token = login_res.json().get("access_token")
                headers = {"Authorization": f"Bearer {token}"}
                perfil_res = await client.get(f"{BASE_URL_API}/users/me", headers=headers)
                
                if perfil_res.status_code != 200:
                    await update.message.reply_text(f"⚠️ Error al obtener perfil: {perfil_res.status_code}\n{perfil_res.text}")
                    return ConversationHandler.END
                
                usuario = perfil_res.json()
                
                if not usuario:
                    await update.message.reply_text("⚠️ No se pudo obtener información del usuario.")
                    return ConversationHandler.END
                
                rol = usuario['rol']
                user_sessions[t_id] = {"token": token, "rol": rol, "nombre": usuario['nombre_completo']}
                
                await update.message.reply_text(
                    f"✅ Sesión iniciada: {usuario['nombre_completo']}\nRol: {rol}",
                    reply_markup=ReplyKeyboardMarkup(obtener_teclado(rol), resize_keyboard=True)
                )
                return ConversationHandler.END
            elif login_res.status_code == 401:
                await update.message.reply_text("❌ Correo o contraseña incorrectos.")
            else:
                await update.message.reply_text(f"❌ Error del servidor: {login_res.status_code}\n{login_res.text}")
            return ConversationHandler.END
        except Exception as e: 
            await update.message.reply_text(f"⚠️ Error al conectar con el backend: {str(e)}")
            return ConversationHandler.END

async def ver_mis_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_id = update.effective_user.id
    if t_id not in user_sessions: return
    headers = {"Authorization": f"Bearer {user_sessions[t_id]['token']}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL_API}/tickets/", headers=headers)
        if res.status_code == 200:
            tickets = res.json()
            # Como admin ves todo, como técnico solo los tuyos (asumiendo que el backend no filtre)
            msg = "📋 **Tus Reportes:**\n\n" + "\n".join([f"#{t['id']} {t['asunto']} ({t['estado']})" for t in tickets])
            await update.message.reply_text(msg if tickets else "No tienes tickets.", parse_mode="Markdown")

async def iniciar_reporte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 ¿Qué falla reportas?")
    return ASUNTO

async def procesar_asunto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["asunto"] = update.message.text
    await update.message.reply_text("🔧 Descripción detallada:")
    return DESCRIPCION

async def procesar_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_id = update.effective_user.id
    payload = {"asunto": context.user_data.get("asunto"), "descripcion": update.message.text, "prioridad": "media"}
    headers = {"Authorization": f"Bearer {user_sessions[t_id]['token']}"}
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL_API}/tickets/", json=payload, headers=headers)
        await update.message.reply_text("✅ Reporte enviado.")
    return ConversationHandler.END

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions.pop(update.effective_user.id, None)
    await update.message.reply_text("🚪 Sesión cerrada.", reply_markup=ReplyKeyboardRemove())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ==========================================
# INICIO DEL BOT
# ==========================================

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()

    # Handlers de Comandos (Prioridad)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mis_tickets", ver_mis_tickets))
    app.add_handler(CommandHandler("ver_todo", ver_todos_los_tickets))
    app.add_handler(CommandHandler("usuarios", ver_usuarios))
    app.add_handler(CommandHandler("cerrar", cerrar_ticket))
    app.add_handler(CommandHandler("logout", logout))

    # Handlers de Conversación
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('login', iniciar_login)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_password)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('reportar', iniciar_reporte)],
        states={
            ASUNTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_asunto)],
            DESCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_descripcion)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    print("🤖 Bot IAIM funcionando correctamente...")
    app.run_polling()