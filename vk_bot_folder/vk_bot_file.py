import vk_api
import re
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_bot_folder.functions import get_city, get_user_info, save_photos
import os
import shutil
from settings_file import VK_BOT_TOKEN, FOLDER_NAME, BASE_MSG, TIMEOUT_MSG
import time
from random import randrange


vk = vk_api.VkApi(token=VK_BOT_TOKEN)
longpoll = VkLongPoll(vk)
upload = vk_api.VkUpload(vk)


def write_msg(user_id, message, attachment=None):
    vk.method('messages.send', {'user_id': user_id, 'message': message,
                                'attachment': attachment, 'random_id': randrange(10 ** 7)})


def get_msg():
    conversation_data = vk.method('messages.getConversations', {'offset': 0, 'count': 1, 'filter': 'unread'})
    if conversation_data['items']:
        dialogue_id = conversation_data['items'][0]['conversation']['peer']['local_id']
        user_message_data = vk.method('messages.getHistory', {'peer_id': dialogue_id, 'count': 1})
        user_message_text = user_message_data['items'][0]['text']
    else:
        user_message_text = None

    return user_message_text


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


def bot_commander():

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text

                if request == 'Привет':
                    write_msg(event.user_id, f'Привет, {event.user_id}')
                elif request == 'Пока':
                    write_msg(event.user_id, 'Пока((')
                elif request == 'Подбери мне пару':

                    data = get_user_info(event.user_id)
                    user_city = None
                    user_bdate = None

                    if 'city' not in data['response'][0]:
                        write_msg(event.user_id, 'Ваш город?')
                        time.sleep(15)
                        user_response = get_msg()
                        if user_response:
                            while get_city(user_response) is None:
                                write_msg(event.user_id, 'Такого города в списке нет, попробуйте ещё раз!')
                                time.sleep(15)
                                user_response = get_msg()
                                if user_response:
                                    user_city = user_response
                                else:
                                    write_msg(event.user_id, TIMEOUT_MSG)
                                    break
                            else:
                                user_city = user_response

                        else:
                            write_msg(event.user_id, TIMEOUT_MSG)
                    else:
                        user_city = data['response'][0]['city']['title']

                    if user_city:
                        pattern = re.compile('[0-9]{4}')
                        if 'bdate' not in data['response'][0] or pattern.search(data['response'][0]['bdate']) is None:
                            write_msg(event.user_id, 'Напишите свою дату рождения в формате ДД.ММ.ГГГГ!')
                            time.sleep(15)
                            user_response = get_msg()
                            if user_response:
                                full_pattern = re.compile('[0-9]{2}\.[0-9]{2}\.[0-9]{4}')
                                while full_pattern.fullmatch(user_response) is None:
                                    write_msg(event.user_id, 'Неправильный формат, попробуйте ещё раз!')
                                    time.sleep(15)
                                    user_response = get_msg()
                                    if user_response:
                                        user_bdate = user_response
                                    else:
                                        write_msg(event.user_id, TIMEOUT_MSG)
                                        break
                                else:
                                    user_bdate = user_response
                            else:
                                write_msg(event.user_id, TIMEOUT_MSG)
                        else:
                            user_bdate = data['response'][0]['bdate']

                    if user_city and user_bdate:
                        write_msg(event.user_id, 'Пожалуйста, подождите, пока запрос выполняется :)')
                        os.mkdir(FOLDER_NAME)
                        save_photos(event.user_id, user_city, user_bdate)
                        write_msg(event.user_id, BASE_MSG)

                        for folder in list(os.walk(FOLDER_NAME))[1:]:
                            main_folder = folder[0].split('\\')
                            source_id = main_folder[1]
                            main_folder = f'{FOLDER_NAME}/{main_folder[1]}'
                            images = list()

                            for file in folder[2]:
                                file_name = f'{main_folder}/{file}'
                                images.append(file_name)
                            upload_photo_message(event.user_id, source_id, images)

                        shutil.rmtree(FOLDER_NAME)

                else:
                    write_msg(event.user_id, 'Не понял вашего ответа...')


if __name__ == '__main__':
    bot_commander()
