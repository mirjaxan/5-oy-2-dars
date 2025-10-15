from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from environs import Env

from database import is_admin
from buttons import adminmenu_kb, menu_kb
from shared import admin_reply_target

admin_router = Router()

env = Env()
env.read_env()
Admin_ID = env.str("ADMIN_CHATID")


@admin_router.message(Command("admin"))
async def admin_handler(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("👑 Admin menyusiga xush kelibsiz!", reply_markup=adminmenu_kb)
    else:
        await message.answer("⛔ Sizda admin huquqi mavjud emas.")


@admin_router.message(Command("user"))
async def get_user(message: Message):
    await message.answer("👤 Siz foydalanuvchi rejimidasiz.", reply_markup=menu_kb)


@admin_router.message(Command("contact_admin"))
async def contact_admin(message: Message):
    try:
        await message.answer("📩 Admin uchun xabaringizni yozing:")
        admin_reply_target["contacting_user"] = message.from_user.id
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")


@admin_router.message(F.reply_to_message, lambda m: str(m.from_user.id) == str(Admin_ID))
async def reply_to_user(message: Message):
    replied = message.reply_to_message

    if replied and "UserID:" in replied.text:
        try:
            user_id = int(replied.text.split("UserID:")[1].split("\n")[0])

            await message.bot.send_message(
                user_id,
                f"📩 Admin javobi:\n\n{message.text}"
            )
            await message.answer("✅ Javob foydalanuvchiga yuborildi.")
        except Exception as e:
            await message.answer(f"⚠️ Xatolik: {e}")


@admin_router.message(F.text, lambda m: str(m.from_user.id) == str(Admin_ID) and "reply_to" in admin_reply_target)
async def handle_admin_reply(message: Message):
    try:
        target_user_id = admin_reply_target["reply_to"]

        await message.bot.send_message(
            target_user_id,
            f"📩 Admin javobi:\n\n{message.text}"
        )
        await message.answer("✅ Javob foydalanuvchiga yuborildi.")

        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]

    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")
        if "reply_to" in admin_reply_target:
            del admin_reply_target["reply_to"]


@admin_router.message(F.text, lambda m: "contacting_user" in admin_reply_target and m.from_user.id == admin_reply_target["contacting_user"])
async def send_user_message_to_admin(message: Message):
    try:
        user_id = message.from_user.id
        admin_reply_target["reply_to"] = user_id
        del admin_reply_target["contacting_user"]

        await message.bot.send_message(
            Admin_ID,
            f"📨 Yangi xabar foydalanuvchidan!\n\n"
            f"👤 Ismi: {message.from_user.full_name}\n"
            f"🆔 UserID: {user_id}\n\n"
            f"💬 Xabar:\n{message.text}"
        )

        await message.answer("✅ Xabaringiz admin ga yuborildi. Tez orada javob olasiz.")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")
