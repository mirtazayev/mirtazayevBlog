from typing import List, Union

from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.engine import SessionLocal
from services.user_service import create_user

BOT_TOKEN = "1788680340:AAExSyS1HJrV0jVJt50084bv1IFKxJdbEpU"
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


def create_markup(rows: List[List[Union[InlineKeyboardButton, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=rows)


def create_button(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url)


def website_btn() -> InlineKeyboardMarkup:
    return create_markup([
        [create_button("Go to Website", url='https://mirtazayev.com/auth')]
    ])


@dp.message(Command(commands=["start"]))
async def start_command(message: Message):
    db = SessionLocal()
    try:
        create_user(message.from_user.id, db)
        response_text = f"Your ID: `{message.from_user.id}`\n\nCopy and enter this ID on the website to log in."
        await message.answer(response_text, reply_markup=website_btn(), parse_mode='markdown')
    finally:
        db.close()
