
class Clickable():
  def __init__(self, gameClass, name, rect, parameter=None, color_mask=None, LeftClickCallBack = None, RightClickCallBack = None, DoubleClickCallBack = None, parent = None, enabled = True, persistent = False):
    self.name = name
    self.rect = rect
    self.parameter = parameter
    self.color_mask = color_mask
    self.gameClass = gameClass
    self.parent = parent
    self.leftClicked = False
    self.rightClicked = False
    self.doubleClicked = False
    self.toBeProcessed = False
    self.persistent = persistent
    self.enabled = enabled
    self.LeftClickCallBack = LeftClickCallBack
    self.RightClickCallBack = RightClickCallBack
    self.DoubleClickCallBack = DoubleClickCallBack
    self.parameter = parameter
    self.mousepos = None


  def Process(self):
    if (self.enabled):
      self.toBeProcessed = False
      if (self.leftClicked):
        self.LeftClickCallBack(self.parameter, self.parent, self.mousepos)
        self.leftClicked = False
      if (self.rightClicked):
        self.RightClickCallBack(self.parameter, self.parent, self.mousepos)
        self.rightClicked = False
      if (self.doubleClicked):
        self.DoubleClickCallBack(self.parameter, self.parent, self.mousepos)
        self.doubleClicked = False


  def LeftClick(self):
    if (self.enabled):
      self.leftClicked = True
      self.toBeProcessed = True


  def RightClick(self):
    if (self.enabled):
      self.rightClicked = True
      self.toBeProcessed = True


  def DoubleClick(self):
    if (self.enabled):
      self.doubleClicked = True
      self.toBeProcessed = True
