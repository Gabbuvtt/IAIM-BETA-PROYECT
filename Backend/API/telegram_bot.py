import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from sqlalchemy.orm import Session
from API.database import SessionLocal
from API import models

# Cargar token del bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Mapeo de roles a comandos permitidos
ROLE_COMMANDS = {
    "tecnico": ["start", "mis_tickets", "crear_ticket", "ver_ticket", "ayuda"],
    "supervisor": ["start", "ver_tickets", "ver_usuarios", "ver_ticket", "ayuda"],
    "admin": ["start", "ver_tickets", "ver_usuarios", "crear_ticket", "editar_ticket", "eliminar_ticket", "cambiar_estado", "ver_ticket", "ayuda"]
}

def get_user_by_chat_id(chat_id: str):
    """Obtiene usuario por su chat_id de Telegram"""
    db = SessionLocal()
    try:
        return db.query(models.Usuario).filter(models.Usuario.telegram_chat_id == str(chat_id)).first()
    finally:
        db.close()

def get_user_menu(user):
    """Genera menú según el rol del usuario"""
    if user.rol == "tecnico":
        return [
            [InlineKeyboardButton("📋 Mis Tickets", callback_data="mis_tickets")],
            [InlineKeyboardButton("➕ Crear Ticket", callback_data="crear_ticket")],
            [InlineKeyboardButton("❓ Ayuda", callback_data="ayuda")]
        ]
    elif user.rol == "supervisor":
        return [
            [InlineKeyboardButton("📋 Ver Todos los Tickets", callback_data="ver_tickets")],
            [InlineKeyboardButton("👥 Ver Usuarios", callback_data="ver_usuarios")],
            [InlineKeyboardButton("❓ Ayuda", callback_data="ayuda")]
        ]
    elif user.rol == "admin":
        return [
            [InlineKeyboardButton("📋 Ver Tickets", callback_data="ver_tickets")],
            [InlineKeyboardButton("👥 Ver Usuarios", callback_data="ver_usuarios")],
            [InlineKeyboardButton("➕ Crear Ticket", callback_data="crear_ticket")],
            [InlineKeyboardButton("✏️ Editar Ticket", callback_data="editar_ticket")],
            [InlineKeyboardButton("🗑️ Eliminar Ticket", callback_data="eliminar_ticket")],
            [InlineKeyboardButton("🔄 Cambiar Estado", callback_data="cambiar_estado")],
            [InlineKeyboardButton("❓ Ayuda", callback_data="ayuda")]
        ]
    return [[InlineKeyboardButton("❓ Ayuda", callback_data="ayuda")]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Inicializa el bot y muestra menú"""
    chat_id = str(update.effective_chat.id)
    user = get_user_by_chat_id(chat_id)
    
    if not user:
        await update.message.reply_text(
            "🚫 *No estás registrado en el sistema*\n\n"
            "Por favor contacta al administrador para vincular tu cuenta de Telegram.",
            parse_mode="Markdown"
        )
        return
    
    welcome_msg = f"👋 Hola *{user.nombre_completo}*\n"
    welcome_msg += f"🎭 Rol: *{user.rol.upper()}*\n"
    welcome_msg += f"🪪 Carnet: *{user.carnet}*\n\n"
    welcome_msg += "Selecciona una opción:"
    
    keyboard = InlineKeyboardMarkup(get_user_menu(user))
    await update.message.reply_text(welcome_msg, reply_markup=keyboard, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los botones del menú"""
    query = update.callback_query
    await query.answer()
    
    chat_id = str(query.message.chat_id)
    user = get_user_by_chat_id(chat_id)
    
    if not user:
        await query.edit_message_text("❌ Usuario no encontrado")
        return
    
    action = query.data
    
    if action == "mis_tickets":
        await show_my_tickets(query, user)
    elif action == "ver_tickets":
        await show_all_tickets(query, user)
    elif action == "ver_usuarios":
        await show_users(query, user)
    elif action == "crear_ticket":
        await prompt_create_ticket(query, user)
    elif action == "editar_ticket":
        await prompt_edit_ticket(query, user)
    elif action == "eliminar_ticket":
        await prompt_delete_ticket(query, user)
    elif action == "cambiar_estado":
        await prompt_change_status(query, user)
    elif action == "ayuda":
        await show_help(query, user)
    elif action.startswith("ver_ticket_"):
        ticket_id = int(action.split("_")[2])
        await show_ticket_details(query, ticket_id, user)

async def show_my_tickets(query, user):
    """Muestra los tickets del técnico"""
    db = SessionLocal()
    try:
        tickets = db.query(models.Tickets).filter(
            models.Tickets.usuario_id == str(user.id)
        ).all()
        
        if not tickets:
            await query.edit_message_text("📭 No tienes tickets asignados")
            return
        
        msg = "📋 *Tus Tickets:*\n\n"
        for ticket in tickets:
            msg += f"🔹 *#{ticket.id}* - {ticket.asunto}\n"
            msg += f"   Estado: {ticket.estado} | Prioridad: {ticket.prioridad}\n"
            msg += f"   Fecha: {ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')}\n\n"
        
        keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="start")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    finally:
        db.close()

async def show_all_tickets(query, user):
    """Muestra todos los tickets (admin/supervisor)"""
    db = SessionLocal()
    try:
        tickets = db.query(models.Tickets).all()
        
        if not tickets:
            await query.edit_message_text("📭 No hay tickets en el sistema")
            return
        
        msg = "📋 *Todos los Tickets:*\n\n"
        for ticket in tickets:
            msg += f"🔹 *#{ticket.id}* - {ticket.asunto}\n"
            msg += f"   Estado: {ticket.estado} | Prioridad: {ticket.prioridad}\n"
            msg += f"   Creador ID: {ticket.usuario_id}\n\n"
        
        keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="start")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    finally:
        db.close()

async def show_users(query, user):
    """Muestra todos los usuarios (admin/supervisor)"""
    db = SessionLocal()
    try:
        users = db.query(models.Usuario).all()
        
        if not users:
            await query.edit_message_text("👥 No hay usuarios registrados")
            return
        
        msg = "👥 *Usuarios del Sistema:*\n\n"
        for u in users:
            msg += f"👤 *{u.nombre_completo}*\n"
            msg += f"   Carnet: {u.carnet}\n"
            msg += f"   Email: {u.email}\n"
            msg += f"   Rol: {u.rol}\n\n"
        
        keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="start")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    finally:
        db.close()

async def prompt_create_ticket(query, user):
    """Solicita datos para crear un ticket"""
    await query.edit_message_text(
        "➕ *Crear Nuevo Ticket*\n\n"
        "Por favor envía el ticket en el siguiente formato:\n\n"
        "`/ticket <asunto> | <descripcion> | <prioridad>`\n\n"
        "Prioridades disponibles: baja, media, alta, critica\n\n"
        "Ejemplo: `/ticket Fuga en tubería | Fuga detectada en zona 3 | alta`",
        parse_mode="Markdown"
    )

async def prompt_edit_ticket(query, user):
    """Solicita ID de ticket a editar"""
    await query.edit_message_text(
        "✏️ *Editar Ticket*\n\n"
        "Envía el comando:\n"
        "`/editar <ticket_id> | <nuevo_asunto> | <nueva_descripcion>`",
        parse_mode="Markdown"
    )

async def prompt_delete_ticket(query, user):
    """Solicita ID de ticket a eliminar"""
    await query.edit_message_text(
        "🗑️ *Eliminar Ticket*\n\n"
        "Envía el comando:\n"
        "`/eliminar <ticket_id>`",
        parse_mode="Markdown"
    )

async def prompt_change_status(query, user):
    """Solicita ID de ticket y nuevo estado"""
    await query.edit_message_text(
        "🔄 *Cambiar Estado de Ticket*\n\n"
        "Envía el comando:\n"
        "`/estado <ticket_id> | <nuevo_estado>`\n\n"
        "Estados: abierto, en_progreso, resuelto, cerrado",
        parse_mode="Markdown"
    )

async def show_help(query, user):
    """Muestra ayuda"""
    msg = "❓ *Ayuda - Comandos Disponibles:*\n\n"
    msg += f"🎭 Tu rol: *{user.rol}*\n\n"
    
    if user.rol == "tecnico":
        msg += "• `/mis_tickets` - Ver tus tickets\n"
        msg += "• `/ticket <asunto> | <desc> | <prioridad>` - Crear ticket\n"
    elif user.rol == "supervisor":
        msg += "• `/ver_tickets` - Ver todos los tickets\n"
        msg += "• `/ver_usuarios` - Ver usuarios\n"
    elif user.rol == "admin":
        msg += "• `/ver_tickets` - Ver todos los tickets\n"
        msg += "• `/ver_usuarios` - Ver usuarios\n"
        msg += "• `/ticket <asunto> | <desc> | <prioridad>` - Crear ticket\n"
        msg += "• `/editar <id> | <asunto> | <desc>` - Editar ticket\n"
        msg += "• `/eliminar <id>` - Eliminar ticket\n"
        msg += "• `/estado <id> | <nuevo_estado>` - Cambiar estado\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="start")]]
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_ticket_details(query, ticket_id, user):
    """Muestra detalles de un ticket específico"""
    db = SessionLocal()
    try:
        ticket = db.query(models.Tickets).filter(models.Tickets.id == ticket_id).first()
        
        if not ticket:
            await query.edit_message_text("❌ Ticket no encontrado")
            return
        
        msg = f"📋 *Ticket #{ticket.id}*\n\n"
        msg += f"📌 *Asunto:* {ticket.asunto}\n"
        msg += f"📝 *Descripción:* {ticket.descripcion}\n"
        msg += f"⚡ *Prioridad:* {ticket.prioridad}\n"
        msg += f"🔄 *Estado:* {ticket.estado}\n"
        msg += f"📅 *Fecha:* {ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')}\n"
        msg += f"👤 *Usuario ID:* {ticket.usuario_id}\n"
        
        keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="mis_tickets" if user.rol == "tecnico" else "ver_tickets")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    finally:
        db.close()

async def create_ticket_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para crear ticket"""
    chat_id = str(update.effective_chat.id)
    user = get_user_by_chat_id(chat_id)
    
    if not user or user.rol not in ["admin", "tecnico"]:
        await update.message.reply_text("❌ No tienes permiso para crear tickets")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Formato incorrecto. Usa: /ticket <asunto> | <descripcion> | <prioridad>")
        return
    
    try:
        parts = " ".join(context.args).split(" | ")
        if len(parts) < 2:
            await update.message.reply_text("❌ Formato incorrecto")
            return
        
        asunto = parts[0]
        descripcion = parts[1]
        prioridad = parts[2] if len(parts) > 2 else "media"
        
        db = SessionLocal()
        try:
            new_ticket = models.Tickets(
                asunto=asunto,
                descripcion=descripcion,
                prioridad=prioridad,
                usuario_id=str(user.id)
            )
            db.add(new_ticket)
            db.commit()
            db.refresh(new_ticket)
            
            await update.message.reply_text(f"✅ Ticket #{new_ticket.id} creado exitosamente")
        finally:
            db.close()
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def change_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para cambiar estado de ticket"""
    chat_id = str(update.effective_chat.id)
    user = get_user_by_chat_id(chat_id)
    
    if not user or user.rol not in ["admin", "tecnico"]:
        await update.message.reply_text("❌ No tienes permiso")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Formato: /estado <ticket_id> | <nuevo_estado>")
        return
    
    try:
        parts = " ".join(context.args).split(" | ")
        ticket_id = int(parts[0])
        nuevo_estado = parts[1]
        
        db = SessionLocal()
        try:
            ticket = db.query(models.Tickets).filter(models.Tickets.id == ticket_id).first()
            if not ticket:
                await update.message.reply_text("❌ Ticket no encontrado")
                return
            
            ticket.estado = nuevo_estado
            db.commit()
            
            await update.message.reply_text(f"✅ Estado del ticket #{ticket_id} cambiado a {nuevo_estado}")
        finally:
            db.close()
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def delete_ticket_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para eliminar ticket (solo admin)"""
    chat_id = str(update.effective_chat.id)
    user = get_user_by_chat_id(chat_id)
    
    if not user or user.rol != "admin":
        await update.message.reply_text("❌ Solo administradores pueden eliminar tickets")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Formato: /eliminar <ticket_id>")
        return
    
    try:
        ticket_id = int(context.args[0])
        
        db = SessionLocal()
        try:
            ticket = db.query(models.Tickets).filter(models.Tickets.id == ticket_id).first()
            if not ticket:
                await update.message.reply_text("❌ Ticket no encontrado")
                return
            
            db.delete(ticket)
            db.commit()
            
            await update.message.reply_text(f"✅ Ticket #{ticket_id} eliminado")
        finally:
            db.close()
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def start_bot():
    """Inicia el bot de Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN no encontrado en .env")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Registrar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ticket", create_ticket_command))
    application.add_handler(CommandHandler("estado", change_status_command))
    application.add_handler(CommandHandler("eliminar", delete_ticket_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot de Telegram iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    start_bot()
