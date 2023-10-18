import pygame
import Utils

class GUI():
  def __init__(self, gameClass, id, name, rect, clickable, parent = None, enabled = True, parentName = '', textButton = False, radioButton = False, radioGroup = None):
    self.ID = id
    self.name = name
    self.rect = rect
    self.gameClass = gameClass
    self.parent = parent
    self.parentName = parentName
    self.open = False
    self.textButton = textButton
    self.enabled = enabled
    self.radioButton = radioButton
    self.radioGroup = radioGroup
    self.children = []
    self.tooltip = 'This is a GUI element'
    self.image_enabled = None
    self.image_disabled = None
    self.visible = True if (parent == None) else False
    self.clickable = clickable
    self.label = self.name
    if (not self.textButton):
      find_space = self.name.find(' ')
      if (find_space > -1):
        self.label = (self.name[find_space+1:])[0]
      else:
        self.label = self.name[0]

  def Draw(self, surface):
    if (not self.enabled or self.children):
      if (not self.image_disabled):
        pygame.draw.rect(surface, Utils.SUPER_DARK_GRAY, self.rect, 0)
        pygame.draw.rect(surface, Utils.GRAY, self.rect, 3)
        Utils.DrawText2Surface(surface, self.label, (self.rect[0]+10,self.rect[1]+5),20,Utils.GRAY)
      else:
        surface.blit(self.image_disabled,(self.rect[0],self.rect[1]))
    else:
      if (not self.image_enabled):
        pygame.draw.rect(surface, Utils.SUPER_DARK_GRAY, self.rect, 0)
        pygame.draw.rect(surface, Utils.LIGHT_BLUE, self.rect, 3)
        Utils.DrawText2Surface(surface, self.label, (self.rect[0]+10,self.rect[1]+5),20,Utils.LIGHT_BLUE)
      else:
        surface.blit(self.image_enabled,(self.rect[0],self.rect[1]))


  def AddChildren(self, child):
    self.children.append(child)


  def SetImages(self, image_enabled, image_disabled):
    self.image_enabled = image_enabled
    self.image_disabled = image_disabled


  def GetID(self):
    return self.ID



