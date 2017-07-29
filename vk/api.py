import requests
import time

from . import captcha, datatypes, errors
from PyQt5.QtWidgets import QApplication
from typing import Union


class Api:
  client_id = 2274003
  client_secret = 'hHbZxrka2uZ6jB1inYsH'
  delay = 0.334
  version = 5.67
  request_time = 0
  # antigate_key = None

  def __init__(self, access_token: str=None):
    self.access_token = access_token
    self.session = requests.session()
    # http://bingosoft.info/news/uznaem-user-agent-oficialnogo-prilozheniya-vkontakte-ili-zhe-minutka-yumora.html
    self.session.headers['User-Agent'] = 'VKAndroidApp/4.38-849 (Android 6.0; SDK 23; x86; Google Nexus 5X; ru)'

  def authenticate(
    self,
    username: str,
    password: str,
    captcha_key: str=None,
    captcha_sid: str=None
  ) -> None:
    params = dict(
      username=username,
      password=password,
      client_id=self.client_id,
      client_secret=self.client_secret,
      v=self.version,
      grant_type='password'
    )
    if captcha_key is not None:
      params['captcha_key'] = captcha_key
      params['captcha_sid'] = captcha_sid
    data = self.request('GET', 'https://oauth.vk.com/token', params)
    if 'error' in data:
      if data.error == 'need_captcha':
        captcha_key = self.handle_captcha(data.captcha_img)
        if captcha_key is not None:
          return self.authenticate(
            username,
            password,
            captcha_key,
            data.captcha_sid
          )
      raise errors.AuthError(data)
    self.access_token = data.access_token

  def method(self, name: str, params: dict={}) -> datatypes.AttrDict:
    params = dict(params)
    # Реальный путь до скрипта-обработчика
    # https://api.vk.com/api.php?oauth=1&method=users.get&user_id=1
    url = 'https://api.vk.com/method/{0}'.format(name)
    if 'v' not in params:
      params['v'] = self.version
    if 'access_token' in params:
      pass
    elif self.access_token is not None:
      params['access_token'] = self.access_token
    delay = self.delay + self.request_time - time.time()
    if delay > 0:
      time.sleep(delay)
    data = self.request('POST', url, data=params)
    self.request_time = time.time()
    if 'error' in data:
      error = data.error
      if error.error_code == errors.API_ERROR_CAPTCHA:
        captcha_key = self.handle_captcha(error.captcha_img)
        if captcha_key is not None:
          params['captcha_key'] = captcha_key
          params['captcha_sid'] = error.captcha_sid
          return self.method(name, params)
      raise errors.ApiError(error)
    return data.response

  def upload(self, server_url: str, files: dict) -> datatypes.AttrDict:
    data = self.request('POST', server_url, files=files)
    if 'error' in data:
      raise errors.UploadError(data.error)
    return data

  def __getattr__(self, name: str):
    return ApiMethod(self, name)

  def handle_captcha(self, url: str) -> Union[str, None]:
    # TODO: интегрировать antigate
    # https://github.com/gotlium/antigate
    a = QApplication([])
    r = self.session.get(url)
    w = captcha.CaptchaDialog(r.content)
    if w.exec_():
      return w.result
    return None

  def request(self, method: str, url: str, *args, **kw) -> datatypes.AttrDict:
    r = self.session.request(method, url, *args, **kw)
    return r.json(object_hook=datatypes.AttrDict)


class ApiMethod:

  def __init__(self, api: Api, name: str):
    self.__api = api
    self.__name = name

  def __getattr__(self, name: str) -> 'ApiMethod':
    return ApiMethod(self.__api, '{}.{}'.format(self.__name, name))

  def __call__(self, *args, **kw) -> datatypes.AttrDict:
    if kw:
      # from_ -> from
      kw = {
        k[:-1] if len(k) > 1 and k.endswith('_') else k: v
        for k, v in kw.items()
      }
    elif args and isinstance(args[0], dict):
      kw = args[0]
    return self.__api.method(self.__name, kw)
