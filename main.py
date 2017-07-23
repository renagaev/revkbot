import vk_api
import time
from VkUser import VkUser, vk
from collections import OrderedDict


vk_bot = vk_api.VkApi(token='95086b6f24729572677b98973a3454ab210ce076876339ddebce2ad5d63a6e96cae74db1ee5247ddc4b30')
vk_bot.auth()
data = {}
values = {'out': 0, 'count': 100, 'time_offset': 60}


def send_message(user_id, message):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message})


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
                likes = {i['name']: i['count'] for i in likes.values()}
                likes = OrderedDict(sorted(likes.items(), key=lambda t: -t[1]))

                message = target.get_name() + '\n_______\n'
                count = 0
                for i in likes:
                    if count > 30:
                        break
                    message += '\n' + str(likes[i]) + ' ❤  :  ' + i
                    count += 1

                send_message(item[u'user_id'], message)

                if item['body'].lower() == 'привет':
                    send_message(item[u'user_id'], u'Привет!')
        time.sleep(0.3)

if __name__ == '__main__':
    main()
