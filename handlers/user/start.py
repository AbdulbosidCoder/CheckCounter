from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from loader import db, dp, bot
from keyboards.inlinekeys import clints_history


@dp.message(CommandStart())
async def start_bot(message: types.Message, state: FSMContext):
    await state.clear()
    db.add_user(message.from_user.id, "user", "user", message.from_user.full_name)
    await message.answer(
        """Assalomu aleykum bizning checkCounter botimizga\n<i>Xush Kelibsiz</i>\nBu bot rasmlar bilan ishlovchi bot bolib rasmlarga ism yoki siz tashlagan rasm nechinchi rasm ekanligini yozib qo'yadi\n/start""",
        reply_markup=clints_history.get_clints_history(message.from_user.id))


@dp.message(lambda msg: msg.text == "all" or msg.text in db.get_all_clients(msg.from_user.id))
async def get_all_clients(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text == "all":
        clients = db.get_all_clients(user_id)
        for client in clients:
            await message.answer_photo(photo=FSInputFile(client[0]))
    else:
        client_name = message.text
        clients = db.get_all_clients(user_id, client_name)
        for client in clients:
            await message.answer_photo(photo=FSInputFile(client[0]))
    await state.clear()
