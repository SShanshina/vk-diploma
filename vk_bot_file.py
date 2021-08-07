import time
from random import randrange
import vk_api
import re
from vk_api.longpoll import VkLongPoll, VkEventType
from functions import *
import os
import shutil
from settings_file import VK_BOT_TOKEN


vk = vk_api.VkApi(token=VK_BOT_TOKEN)
longpoll = VkLongPoll(vk)
upload = vk_api.VkUpload(vk)


def write_msg(user_id, message, attachment=None):
    vk.method('messages.send', {'user_id': user_id, 'message': message,
                                'attachment': attachment, 'random_id': randrange(10 ** 7)})


def get_message():
    user_response = vk.method('messages.getConversations')
    user_input_data = user_response['items'][0]['last_message']['text']
    return user_input_data


def upload_photo_message(user_id, source_id, images):
    attachments = list()
    for image in images:
        photo = upload.photo_messages(image)
        owner_id = photo[0]['owner_id']
        photo_id = photo[0]['id']
        access_key = photo[0]['access_key']
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        attachments.append(attachment)
    result = ','.join(attachments)
    write_msg(user_id, f'Фото пользователя vk.com/{source_id}', result)


if __name__ == '__main__':

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text

                if request == 'Привет':
                    write_msg(event.user_id, f'Привет, {event.user_id}')
                elif request == 'Пока':
                    write_msg(event.user_id, 'Пока((')
                elif request == 'Подбери мне пару':

                    os.mkdir(FOLDER_NAME)
                    data = get_user_info(event.user_id)

                    if 'city' not in data['response'][0]:
                        write_msg(event.user_id, 'Из какого вы города?')
                        time.sleep(15)
                        user_city = get_message()
                    else:
                        user_city = data['response'][0]['city']['title']

                    if 'bdate' not in data['response'][0] or re.match(re.compile('[0-9]{4}'), data['response'][0]['bdate']) is None:
                        write_msg(event.user_id, 'Напишите свою дату рождения в формате Д.М.ГГГГ!')
                        time.sleep(15)
                        user_bdate = get_message()
                    else:
                        user_bdate = data['response'][0]['bdate']

                    save_photos(event.user_id, user_city, user_bdate)
                    write_msg(event.user_id, BASE_MSG)

                    for folder in list(os.walk(FOLDER_NAME))[1:]:
                        main_folder = folder[0].split('\\')
                        source_id = main_folder[1]
                        main_folder = f'{FOLDER_NAME}/{main_folder[1]}'
                        print(main_folder)
                        images = list()

                        for file in folder[2]:
                            file_name = f'{main_folder}/{file}'
                            images.append(file_name)
                            print(images)
                        upload_photo_message(event.user_id, source_id, images)

                    shutil.rmtree(FOLDER_NAME)

                else:
                    write_msg(event.user_id, 'Не понял вашего ответа...')
