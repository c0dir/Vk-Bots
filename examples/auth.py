import vk

if __name__ == '__main__':
  vkapi = vk.Api()
  vkapi.authenticate('+79522195708', '***')
  # Save access token
  with open('access_token.txt', 'w') as fp:
    fp.write(vkapi.access_token)
