import requests
import time

from . import captcha, datatypes, errors
from PyQt5.QtWidgets import QApplication


class Api:
  client_id = 2274003
  client_secret = 'hHbZxrka2uZ6jB1inYsH'
  delay = 0.334
  version = 5.67
  request_time = 0

  def __init__(self, access_token=None):
    self.access_token = access_token
    self.session = requests.session()
    # http://bingosoft.info/news/uznaem-user-agent-oficialnogo-prilozheniya-vkontakte-ili-zhe-minutka-yumora.html
    self.session.headers['User-Agent'] = 'VKAndroidApp/4.38-849 (Android 6.0; SDK 23; x86; Google Nexus 5X; ru)'

  def authenticate(self, username, password, captcha_key=None, captcha_sid=None):
    payload = dict(
      username=username,
      password=password,
      client_id=self.client_id,
      client_secret=self.client_secret,
      v=self.version,
      grant_type='password'
    )
    if captcha_key is not None:
      payload['captcha_key'] = captcha_key
      payload['captcha_sid'] = captcha_sid
    json = self.request('GET', 'https://oauth.vk.com/token', params=payload)
    if 'error' in json:
      if json.error == 'need_captcha':
        ans = self.prompt_captcha(json.captcha_img)
        if ans is not None:
          return self.authenticate(username, password, ans, json.captcha_sid)
      raise errors.AuthError(json)
    self.access_token = json.access_token

  def method(self, name, params={}):
    params = dict(params)
    # https://api.vk.com/api.php?oauth=1&method=captcha.force
    url = 'https://api.vk.com/method/{0}'.format(name)
    if 'v' not in params:
      params['v'] = self.version
    if 'access_token' not in params and self.access_token:
      params['access_token'] = self.access_token
    delay = self.delay + self.request_time - time.time()
    if delay > 0:
      time.sleep(delay)
    json = self.request('POST', url, data=params)
    self.request_time = time.time()
    if 'error' in json:
      error = json.error
      if error.error_code == errors.API_ERROR_CAPTCHA:
        ans = self.prompt_captcha(error.captcha_img)
        if ans is not None:
          params['captcha_key'] = ans
          params['captcha_sid'] = error.captcha_sid
          return self.method(name, params)
      raise errors.ApiError(error)
    return json.response

  def upload(self, server_url, files):
    json = self.request('POST', server_url, files=files)
    if 'error' in json:
      raise errors.UploadError(json.error)
    return json

  def __getattr__(self, name):
    return ApiMethod(self, name)

  def prompt_captcha(self, url):
    a = QApplication([])
    r = self.session.get(url)
    w = captcha.CaptchaDialog(r.content)
    if w.exec_():
      return w.result
    return None

  def request(self, method, url, **kw):
    r = self.session.request(method, url, **kw)
    return r.json(object_hook=datatypes.AttrDict)


class ApiMethod:

  def __init__(self, api, name):
    self.__api = api
    self.__name = name

  def __getattr__(self, name):
    return ApiMethod(self.__api, '{}.{}'.format(self.__name, name))

  def __call__(self, *args, **kw):
    if kw:
      # from_ -> from
      kw = {
        k[:-1] if len(k) > 1 and k.endswith('_')
        else k: v
        for k, v in kw.items()
      }
    elif args and isinstance(args[0], dict):
      kw = args[0]
    return self.__api.method(self.__name, kw)
