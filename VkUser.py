import vk_api
from collections import Counter
session = vk_api.VkApi(token='5bd3c7e65325f77f7eb4abddbd7eba9ef802515a3bbe7b4bbc9263ede54b3c23267ae546c7a6a084a00d2')
tools = vk_api.VkTools(session)
vk = session.get_api()

class VkUser(object):

    def __init__(self, vk_id):
        if not vk_id.isdigit():
            vk_id = vk.users.get(user_ids=vk_id, fields='id')[0]['id']
            print(vk_id)
        self.vk_id = vk_id

    def get_wall(self):  # получает стену
        wall = tools.get_all('wall.get', 100, {'owner_id': self.vk_id})['items']
        return wall

    def get_likes_list(self):  # получает количесво лайков для каждого юзера со всех постов со стены
        def count(request):
            g = [request.result.get(key) for key in request.result.keys()]
            g = [i['items'] for i in g]
            g = [y for x in g for y in x]
            return {i: g.count(i) for i in g}

        wall = VkUser.get_wall(self)
        posts_ids = [item['id'] for item in wall]
        photos_ids = [item['id'] for item in VkUser.get_photos(self, parameter='items')]
        with vk_api.VkRequestsPool(session) as pool:
            posts = pool.method_one_param(
                'likes.getList',
                key='item_id',
                values=posts_ids,
                default_values={'owner_id': self.vk_id,
                                'type': 'post'}
            )

        with vk_api.VkRequestsPool(session) as pool:
            photos = pool.method_one_param(
                'likes.getList',
                key='item_id',
                values=photos_ids,
                default_values={'owner_id': self.vk_id,
                                'type': 'photo'}
            )
        return dict(Counter(count(photos)) + Counter(count(posts)))

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
        groups = [ i for i in groups['items'] if i['type'] != 'profile']
        return groups
