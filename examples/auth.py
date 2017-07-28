import vk

if __name__ == '__main__':
  vkapi = vk.Api()
  vkapi.authenticate('+79522195708', '***')
  vkapi.wall.post(message='Test message')
