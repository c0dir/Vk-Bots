from .datatypes import AttrDict


class ApiError(Exception):

  def __init__(self, error: AttrDict):
    self.code = error.error_code
    self.message = error.error_msg
    self.raw = error
    super().__init__('[{code}] {message}'.format(**self.__dict__))


class AuthError(Exception):

  def __init__(self, response: AttrDict):
    self.name = response.error
    self.description = response.get('error_description')
    self.raw = response
    super().__init__(
      '{0}: {1}'.format(self.name, self.description) if self.description
      else self.name
    )


class UploadError(Exception):
  pass
