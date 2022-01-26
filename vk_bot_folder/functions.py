import requests
import datetime
from datetime import date
from random import randrange
import os
from settings_file import *
from vk_bot_folder.db_connection import *
import json
import time


def get_user_info(search_id):

    response = requests.get(GET_USER_INFO_URL, params={
        'access_token': VK_TOKEN,
        'v': V,
        'user_ids': search_id,
        'fields': 'sex, city, bdate'
    })
    data = response.json()

    return data


def get_city(user_city):

    response = requests.get(GET_CITY_ID, params={
        'access_token': VK_TOKEN,
        'v': V,
        'need_all': 0,
        'country_id': 1
    })
    items = response.json()['response']['items']

    for item in items:
        if user_city == item['title']:
            result = item['id']
            return result


def get_age(bdate):

    birth_date = bdate.split('.')
    for i, num in enumerate(birth_date):
        number = int(num)
        birth_date[i] = number

    birth_date = datetime.datetime(birth_date[2], birth_date[1], birth_date[0])
    current_date = date.today()
    age = current_date.year - birth_date.year - (
                (current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    return age


def extract_info(search_id, user_city, user_bdate):

    data = get_user_info(search_id)

    city = get_city(user_city)

    sex = data['response'][0]['sex']
    if sex == 1:
        search_sex = 2
    else:
        search_sex = 1

    age = get_age(user_bdate)

    return [city, search_sex, age]


def get_photos_info(user_id):

    response = requests.get(PHOTOS_GET_URL, params={
        'access_token': VK_TOKEN,
        'v': V,
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': 1
    })

    data = response.json()
    photos_popularity = list()

    for photo in data['response']['items']:
        time.sleep(0.1)
        url = photo['sizes'][-1]['url']
        likes = photo['likes']['count']
        comments = photo['comments']['count']
        photos_popularity.append([likes + comments, url])

    three_popular_photos = sorted(photos_popularity, reverse=True)[:3]
    result = list()

    for item in three_popular_photos:
        photo_url = item[1]
        result.append(photo_url)

    return result


def search_users(search_id, user_city, user_bdate):

    result = extract_info(search_id, user_city, user_bdate)
    city = result[0]
    sex = result[1]
    age_from = result[2]
    age_to = result[2] + 5
    offset = 1

    db_chek = execute_read_query(connection)
    responses_list = list()
    users_list = list()

    while len(responses_list) != 10:
        response = requests.get(USERS_SEARCH_URL, params={
            'access_token': VK_TOKEN,
            'count': 1,
            'offset': offset,
            'v': V,
            'city': city,
            'sex': sex,
            'status': 6,
            'age_from': age_from,
            'age_to': age_to,
            'has_photo': 1
        })
        offset += 1
        item = response.json()
        data = item['response']['items']

        for user_data in data:
            user_info = (user_data['id'], user_data['first_name'], user_data['last_name'])
            time.sleep(0.1)
            if user_data['is_closed'] is False and user_info not in db_chek:
                responses_list.append(item)
                users_list.append(user_info)

    result = dict()
    for user in responses_list:
        items = user['response']['items']
        for item in items:
            user_id = item['id']
            photos = get_photos_info(user_id)
            result[f'https://vk.com/id{user_id}'] = photos

    with open('vk_result.json', 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    execute_insert_query(connection, users_list)

    return result


def save_photos(search_id, user_city, user_bdate):

    data = search_users(search_id, user_city, user_bdate)
    for keys, values in data.items():
        folder_name = keys.split('/')[3]
        os.mkdir(f'{FOLDER_NAME}/{folder_name}')

        for photo_url in values:
            file_name = str(randrange(10 ** 10)) + '.jpg'
            photo_raw = requests.get(photo_url)
            with open(os.path.join(FOLDER_NAME, folder_name, file_name), 'wb') as f:
                f.write(photo_raw.content)


if __name__ == '__main__':
    os.mkdir(FOLDER_NAME)
