import vk_api
import time
from VkUser import VkUser, vk
from collections import OrderedDict
from pprint import pprint

vk_bot = vk_api.VkApi(token='95086b6f24729572677b98973a3454ab210ce076876339ddebce2ad5d63a6e96cae74db1ee5247ddc4b30')
vk_bot.auth()
data = {}
values = {'out': 0, 'count': 100, 'time_offset': 60}

def send_message(user_id, message):
    vk_bot.method('messages.send', {'user_id':user_id,'message':message})

def main():
    while True:
        response = vk_bot.method('messages.get', values)
        if response['items']:
            values['last_message_id'] = response['items'][0]['id']

            for item in response['items']:
                target = item['body'].split('/')[-1]
                try:
                    target = VkUser(target)
                except vk_api.exceptions.ApiError:
                    send_message(item['user_id'], 'Шо це таке? Мне нужна ссылка на профиль VK')
                    continue

                likes = target.get_likes_list()
                likers = ','.join([str(i) for i in likes.keys()])
                names = vk.users.get(user_ids=likers , fields='first_name, last_name')
                names = {i['id']: ' '.join([i['first_name'], i['last_name']]) for i in names}

                shit = [(str(likes[i]) + '  :  ' + names[i]) for i in likes]
                shit = {names[i] : likes[i] for i in likes}
                shit = OrderedDict(sorted(shit.items(), key=lambda t: -t[1]))

                message = 'Топ-30'
                count = 0
                for i in shit:
                    if count > 30:
                        break
                    message += '\n' + str(shit[i]) + ' ❤  :  ' + i
                    count += 1

                send_message(item[u'user_id'], message)

                if item['body'].lower() == 'привет':
                    send_message(item[u'user_id'], u'Привет!')
        time.sleep(1)

if __name__ == '__main__':
    main()