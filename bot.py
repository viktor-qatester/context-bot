import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from database import init_db, add_session_log, get_latest_context

# Загружаем переменные окружения вручную из файла .env
def load_env():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

load_env()

BOT_TOKEN = os.getenv("BOT_TOKEN")
REBAR_CALC_URL = os.getenv("REBAR_CALC_URL")
TASKFLOW_URL = os.getenv("TASKFLOW_URL")

if not BOT_TOKEN:
    print("Ошибка: Токен бота не найден в файле .env!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем удобное кнопочное меню для главного экрана
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Калькулятор арматуры"), KeyboardButton(text="📝 Пет-проект (TaskFlow)")],
        [KeyboardButton(text="🗂️ Показать весь текущий контекст")]
    ],
    resize_keyboard=True
)

# Словарь для отслеживания того, для какого проекта пользователь пишет лог
user_modes = {}

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Приветственное сообщение при команде /start"""
    init_db()  # На всякий случай проверяем, что база данных создана
    await message.answer(
        f"Привет, Виктор! 👋\n"
        f"Я твой личный Хранитель Контекста. Помогу не забыть, на чем остановились в проектах.\n\n"
        f"🔗 **Твои репозитории:**\n"
        f"• [Калькулятор арматуры]({REBAR_CALC_URL})\n"
        f"• [TaskFlow Checker]({TASKFLOW_URL})\n\n"
        f"Выбери проект на клавиатуре ниже, чтобы управлять контекстом 👇",
        reply_markup=main_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@dp.message(F.text == "📊 Калькулятор арматуры")
async def show_rebar_info(message: Message):
    user_modes[message.from_user.id] = "rebar"
    logs = get_latest_context("rebar")
    
    text = f"🏗️ **Проект: Калькулятор арматуры**\n🔗 [GitHub Репозиторий]({REBAR_CALC_URL})\n\n"
    if logs:
        text += "📜 *Последние сохраненные записи:*\n"
        for content, date in logs:
            text += f"🔹 [{date}] {content}\n"
    else:
        text += "❌ Записей о работе пока нет.\n"
    
    text += "\n✍️ **Чтобы добавить новую запись:** просто отправь мне сообщение следующим текстом (например: 'Починил кнопку, обновил стили для мобилки')."
    
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

@dp.message(F.text == "📝 Пет-проект (TaskFlow)")
async def show_taskflow_info(message: Message):
    user_modes[message.from_user.id] = "taskflow"
    logs = get_latest_context("taskflow")
    
    text = f"💻 **Проект: TaskFlow Checker**\n🔗 [GitHub Репозиторий]({TASKFLOW_URL})\n\n"
    if logs:
        text += "📜 *Последние сохраненные записи:*\n"
        for content, date in logs:
            text += f"🔹 [{date}] {content}\n"
    else:
        text += "❌ Записей о работе пока нет.\n"
    
    text += "\n✍️ **Чтобы добавить новую запись:** просто отправь мне следующее сообщение текстом."
    
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

@dp.message(F.text == "🗂️ Показать весь текущий контекст")
async def show_all_context(message: Message):
    rebar_logs = get_latest_context("rebar", limit=3)
    taskflow_logs = get_latest_context("taskflow", limit=3)
    
    text = "🗂️ **Глобальный срез контекста для ИИ**\n\n"
    
    text += "🏗️ **Калькулятор арматуры:**\n"
    if rebar_logs:
        for content, date in rebar_logs:
            text += f"• [{date}] {content}\n"
    else:
        text += "• Нет записей\n"
        
    text += "\n💻 **TaskFlow Checker:**\n"
    if taskflow_logs:
        for content, date in taskflow_logs:
            text += f"• [{date}] {content}\n"
    else:
        text += "• Нет записей\n"
        
    await message.answer(text, parse_mode="Markdown")

@dp.message()
async def handle_text(message: Message):
    """Ловит любые текстовые сообщения и сохраняет их в выбранный проект"""
    user_id = message.from_user.id
    mode = user_modes.get(user_id)
    
    if not mode:
        await message.answer("⚠️ Сначала выбери проект на клавиатуре (Калькулятор или Пет-проект), чтобы я знал, куда записать твою мысль.")
        return
        
    project_name = "rebar" if mode == "rebar" else "taskflow"
    project_label = "📊 Калькулятор" if mode == "rebar" else "📝 TaskFlow"
    
    add_session_log(project_name, message.text)
    await message.answer(f"✅ Успешно записано в контекст проекта **{project_label}**!")

async def main():
    print("Бот успешно запущен и слушает команды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())