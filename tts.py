import os

from gtts import gTTS

import utils


def save_wav(text, dir_name, chat_id):
    dir_path = f'./wav/{dir_name}/{chat_id}'
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    file_name = utils.random_string()
    file_path = dir_path + f'/{file_name}.wav'
    tts_en = gTTS(text, lang='en')
    tts_en.save(file_path)
    return file_path
