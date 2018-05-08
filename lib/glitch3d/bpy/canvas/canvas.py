import abc

class Canvas(object):
  def __init__(self, locals_copy):
    self.locals_copy = locals_copy

  def __getattr__(self, name):
    if str(name) in dir():
      return dir[str(name)]
    else:
        return self.main(str(name))

  def main(self, name):
    return self.locals_copy[name]

  __metaclass__  = abc.ABCMeta
  @abc.abstractmethod

  def render(self):
      "add additional elements to the main canvas and animate them here"