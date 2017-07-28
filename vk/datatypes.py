class AttrDict(dict):

  def __init__(self, *args, **kw):
    super().__init__(*args, **kw)
    self.__dict__ = self
