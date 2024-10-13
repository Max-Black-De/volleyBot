from telegram.ext import ContextTypes
from telegram import ReplyKeyboardMarkup, Update

from handlers.message_handler import handle_leave_confirmation
from utils.notification_utils import notify_participants
from jobs.join_leave_job import join_event, leave_event
from events_utils import event_participants
from logging import getLogger

logger = getLogger(__name__)
# Функция для создания статической клавиатуры
def create_static_keyboard(event_id, chat_id):
    # Получаем список участников для данного события
    participants = event_participants.get(event_id, [])  # Используем правильный ID события

    # Проверяем, записан ли пользователь в список участников
    if any(p['user_id'] == chat_id for p in participants):
        dynamic_button_text = "Передумал! Отписываюсь("  # Если записан, изменяем текст
    else:
        dynamic_button_text = "Иду на тренировку!"  # По умолчанию

    # Создаём клавиатуру с динамической кнопкой
    keyboard = [
        [dynamic_button_text],
        ["Список участников"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция для обработки сообщений кнопок меню
async def handle_menu_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    event_id = next(iter(event_participants))  # Получаем первый доступный ID события (или добавьте вашу логику)
    pending_data = context.user_data.get('pending_leave_confirmation')

    # Логируем сообщение
    logger.info(f"Пользователь {user.first_name} отправил сообщение: {text}")

    if pending_data and pending_data['user_id'] == user.id:
        await handle_leave_confirmation(update, context)
        return

    if text == "Иду на тренировку!":
        # Записываем пользователя на тренировку
        await join_event(update, context, event_id, user)
    elif text == "Передумал! Отписываюсь(":
        # Отписываем пользователя от тренировки
        await leave_event(update, context, event_id, user)
    elif text == "Список участников":
        # Показываем список участников
        participants_list = await notify_participants(event_id)
        await update.message.reply_text(f"Список участников:\n{participants_list}")
    else:
        # Если сообщение не распознано, отвечаем по умолчанию
        await update.message.reply_text("Неизвестная команда. Используйте кнопки для выбора действия.")
