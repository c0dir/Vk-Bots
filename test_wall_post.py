import vk

if __name__ == '__main__':
  with open('access_token.txt') as fp:
    access_token = fp.read()
  vkapi = vk.Api(access_token)
  # https://vk.com/dev/wall.post
  vkapi.wall.post(message='Test message')
