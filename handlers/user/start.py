from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from loader import db, dp, bot
from keyboards.inlinekeys import clints_history
from states.image_states import ImageGroup


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


@dp.message(Command("delete"))
async def get_delete_client(message: types.Message, state: FSMContext):
    await  message.answer("Iltimos tanlang: ", reply_markup=clints_history.get_clints_history(message.from_user.id))
    await state.set_state(ImageGroup.getDeleteUserState)


@dp.message(ImageGroup.getDeleteUserState)
async def get_delete_client(message: types.Message, state: FSMContext):
    if message.text == "all":
        db.delete_all_clients(message.from_user.id)
    else:
        client_name = message.text
        db.delete_clints_history(message.from_user.id, client_name)
    await  message.answer("Ma'lumotlar tozalandi")
    await state.clear()