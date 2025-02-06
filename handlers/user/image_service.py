import asyncio
import os
import logging
from aiogram.filters import Command
from aiogram import types
from datetime import datetime
from aiogram.fsm.context import FSMContext
from loader import dp, bot, db
from collections import defaultdict
from aiogram.utils.markdown import hbold
from aiogram.types import FSInputFile, PhotoSize
from states.image_states import ImageGroup
from utils.pic_changer import write_number_on_image

DOWNLOAD_PATH = './downloads'
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

images = {}


set_many_images = {}

media_group_data = defaultdict(lambda: {"files": [], "processed": False})


@dp.message(lambda msg: msg.media_group_id is not None and msg.photo)
async def handle_media_group(message: types.Message, state: FSMContext):
    """Handles grouped media (albums)"""
    media_group_id = message.media_group_id
    file_id = message.photo[-1].file_id

    # Store file ID
    media_group_data[media_group_id]["files"].append(file_id)

    # Wait to ensure all images are received
    await asyncio.sleep(2)

    # Process the media group only once
    if not media_group_data[media_group_id]["processed"]:
        media_group_data[media_group_id]["processed"] = True  # Mark as processed

        file_list = media_group_data[media_group_id]["files"]
        count = len(file_list)

        await message.answer(f"You sent {count} images. Downloading...")

        set_many_images[message.from_user.id]= []
        for idx, file_id in enumerate(file_list, start=1):
            file = await bot.get_file(file_id)
            file_path = file.file_path

            # Fixing numbering issue
            destination = os.path.join(DOWNLOAD_PATH, f"image_{media_group_id}_{idx}.jpg")
            set_many_images[message.from_user.id].append(destination)
            await bot.download_file(file_path, destination)

            db.add_picture(destination, datetime.utcnow(), message.from_user.id, file_id)
            number = db.get_pic_by_user_id(message.from_user.id)

            # Ensuring correct numbering
            await write_number_on_image(destination, len(number), (30, 20), font_size=50)
            await message.answer_photo(FSInputFile(destination))

        await message.answer(
            "Iltimos, bu rasmlar kimga tegishli ekanligini belgilang yoki /nothing komandasi bilan bekor qiling.")
        await state.set_state(ImageGroup.getGroupNameState)


@dp.message(lambda msg: msg.photo)
async def handle_single_photo(message: types.Message, state: FSMContext):
    """Handles a single image"""
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    destination = os.path.join(DOWNLOAD_PATH, f"image_{file_id}.jpg")
    await bot.download(file, destination)

    db.add_picture(destination,datetime.utcnow(),message.from_user.id,file_id)
    number = db.get_pic_by_user_id(message.from_user.id)

    await write_number_on_image(destination, len(number),(30, 20), font_size=50)

    images[message.from_user.id] = (destination, message.photo[-1].height)
    await message.answer_photo(FSInputFile(destination))
    await  message.answer("Iltimos rasim uchun coment yoing.")
    await  state.set_state(ImageGroup.getUserNameState)

@dp.message(ImageGroup.getUserNameState)
async def handler_image_name(message: types.Message, state: FSMContext):
    image = images[message.from_user.id]
    await  write_number_on_image(image[0], message.text, (30, 100), 50)
    await  message.answer_photo(FSInputFile(image[0]))
    await state.clear()



@dp.message(ImageGroup.getGroupNameState or Command("nothing"))
async def handler_group_name(message: types.Message, state: FSMContext):
    group_images = set_many_images[message.from_user.id]

    if not group_images:
        await message.answer("Siz hech qanday rasm yubormadingiz.")
        return

    if message.text.lower() == "nothing":
        for file_url in group_images:
            db.update_picture(file_url, message.from_user.id, "NOTHING")
            image = FSInputFile(file_url)  # Store in a variable
            await message.answer_photo(image)
        await message.answer("Botimizdan foydalanganingiz uchun rahmat.")
        await state.clear()  # Clear state and return
        return

    for file_url in group_images:
        db.update_picture(file_url, message.from_user.id, message.text)
        await write_number_on_image(file_url, message.text, (30, 100), font_size=50)
        image = FSInputFile(file_url)  # Store in a variable
        await message.answer_photo(image)

    await message.answer("Checklar guruhi muvaffaqiyatli yakunlandi.")
    await state.clear()


