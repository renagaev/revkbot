import vk_api
from time import time

session = vk_api.VkApi(token='52d01ed5af4f982613daf93a12d2b7432551bb5968f5d7c14822dad420e2c480429454da6eae749e1da42')
tools = vk_api.VkTools(session)
vk = session.get_api()


class VkUser(object):
    def __init__(self, vk_id):
        if not vk_id.isdigit():
            vk_id = vk.users.get(user_ids=vk_id, fields='id')[0]['id']
        self.vk_id = vk_id

    def get_wall(self):  # получает стену
        wall = tools.get_all('wall.get', 100, {'owner_id': self.vk_id})['items']
        return wall

    def get_likes_list(self):  # получает количесво лайков для каждого юзера со всех постов со стены
        def count(request_dict):
            """возвращает количество лайков для каждого vk id"""
            out = {}
            for item in request_dict.values():
                for man in item['items']:
                    name = ' '.join([man['first_name'], man['last_name']])
                    vk_id_ = man['id']
                    if vk_id_ in out:
                        out[vk_id_]['count'] += 1
                    else:
                        out[vk_id_] = {'name': name,
                                       'count': 1}
            return out

        wall = VkUser.get_wall(self)
        photos = VkUser.get_photos(self, parameter='items')
        posts_ids = [item['id'] for item in wall]
        photos_ids = [item['id'] for item in photos]

        with vk_api.VkRequestsPool(session) as pool:
            posts = pool.method_one_param(
                'likes.getList',
                key='item_id',
                values=posts_ids,
                default_values=dict(owner_id=self.vk_id, type='post', extended=1))

        with vk_api.VkRequestsPool(session) as pool:
            photos = pool.method_one_param(
                'likes.getList',
                key='item_id',
                values=photos_ids,
                default_values=dict(owner_id=self.vk_id, type='photo', extended=1)
            )

        posts = count(posts.result)
        photos = count(photos.result)

        out_dict = posts
        pprint(out_dict)
        for vk_id in photos:
            if vk_id in out_dict:
                out_dict[vk_id]['count'] += photos[vk_id]['count']
            else:
                out_dict[vk_id] = photos[vk_id]

        return out_dict

    def get_photos(self, parameter=None):  # получает фото
        photos = tools.get_all('photos.getAll', 200, {'owner_id': self.vk_id})
        if parameter is None:
            return photos
        else:
            return photos[parameter]

    def get_feed(self):
        pass
        # TODO получать ленту пользователя через newsfeed.get и execute

    def get_name(self):
        answer = vk.users.get(user_ids=self.vk_id, fields='first_name, last_name')
        return ' '.join([answer[0]['first_name'], answer[0]['last_name']])

    def get_groups(self):
        groups = tools.get_all('users.getSubscriptions', 200, {'user_id': self.vk_id,
                                                               'extended': 1,
                                                               'fields': 'name'})
        groups = [i for i in groups['items'] if i['type'] != 'profile']
        return groups
