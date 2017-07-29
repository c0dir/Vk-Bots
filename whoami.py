import vk

if __name__ == '__main__':
  with open('access_token.txt') as fp:
    access_token = fp.read()
  vkapi = vk.Api(access_token)
  me, = vkapi.users.get()
  print('{first_name} {last_name}'.format(**me))
