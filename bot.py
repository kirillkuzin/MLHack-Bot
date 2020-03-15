import io
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from difflib import SequenceMatcher

import config
import stt
import dialog
from states import MenuState


bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start_command_handler(message: types.Message, state: FSMContext):
    await message.answer('Start message 👋')

    async with state.proxy() as data:
        data['dialog_state'] = 0

    await MenuState.dialog.set()
    await next_dialog_state(message, state)


@dp.message_handler(content_types=[types.ContentType.VOICE],
                    state=MenuState.dialog)
async def dialog_voice_handler(message: types.Message, state: FSMContext):
    file_path = await download_file(file_id=message.voice.file_id)
    recognizer = stt.Recognizer()
    recognized_text = recognizer.recognize(ogg_path=file_path)
    print(recognized_text)

    string_is_equals = False
    async with state.proxy() as data:
        buttons = dialog.dialog_states[str(data['dialog_state'])]['buttons']
    if recognized_text is not None:
        for button in buttons:
            ratio = SequenceMatcher(None, button, recognized_text).ratio()
            print(f'{button} {ratio}')
            if ratio >= 0.85:
                file_path = './wav/perfect/' + button + '.wav'
                string_is_equals = True

    if not string_is_equals:
        file_path = './wav/perfect/' + buttons[0] + '.wav'
        await message.answer('No, you are wrong ❌')
        await message.answer('Please listen our voice and '
                             'try again please 🤷‍♂️')
        with open(file_path, 'rb') as f:
            read_data = io.BytesIO(f.read())
        await message.answer_voice(read_data)
    else:
        markup = types.ReplyKeyboardRemove()
        await message.answer('Excellent ! ✨✨✨', reply_markup=markup)
        await message.answer('Please listen to the perfect '
                             'pronunciation and continue the dialogue 🙏')
        with open(file_path, 'rb') as f:
            read_data = io.BytesIO(f.read())
        await message.answer_voice(read_data)
        await next_dialog_state(message, state)


async def next_dialog_state(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=False)
    async with state.proxy() as data:
        data['dialog_state'] += 1
        for button in \
                dialog.dialog_states[str(data['dialog_state'])]['buttons']:
            markup.add(button)

    message_test = dialog.dialog_states[str(data['dialog_state'])]['message']
    await message.answer(message_test, reply_markup=markup)


async def download_file(file_id: str) -> str:
    file = await bot.get_file(file_id=file_id)
    file_path = file.file_path[:-3] + 'ogg'
    await file.download(file_path)
    return file_path


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
