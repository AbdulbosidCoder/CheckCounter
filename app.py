import handlers
import  middlewares
from loader import dp, bot, db
from aiogram.types.bot_command_scope_all_private_chats import BotCommandScopeAllPrivateChats
import asyncio
from utils.notify_admins import start, shutdown
from utils.set_botcommands import commands
import logging
import sys

async def main():
    try:
        try:
            db.create_table_pictures()
            db.create_table_users()
        except:
            pass

        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=commands,scope=BotCommandScopeAllPrivateChats(type='all_private_chats'))
        dp.startup.register(start)
        dp.shutdown.register(shutdown)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot ishda to'xtatdi")