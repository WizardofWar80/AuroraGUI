import pygame
import Utils

class GUI():
  def __init__(self, gameClass, id, name, rect, clickable, parent = None, enabled = True):
    self.ID = id
    self.name = name
    self.rect = rect
    self.gameClass = gameClass
    self.parent = parent
    self.open = False
    self.enabled = enabled
    self.children = []
    self.tooltip = 'This is a GUI element'
    self.image_enabled = None
    self.image_disabled = None
    self.visible = True if (parent == None) else False
    self.clickable = clickable

  def Draw(self, surface):
    if (self.enabled):
      if (not self.image_enabled):
        pygame.draw.rect(surface, Utils.SUPER_DARK_GRAY, self.rect, 0)
        pygame.draw.rect(surface, Utils.GREEN, self.rect, 3)
        find_space = self.name.find(' ')
        if (find_space > -1):
          label = (self.name[find_space+1:])[0]
        else:
          label = self.name[0]
        Utils.DrawText2Surface(surface, label, (self.rect[0]+10,self.rect[1]+5),20,Utils.GREEN)
      else:
        surface.blit(self.image_enabled,(self.rect[0],self.rect[1]))
    else:
      if (not self.image_disabled):
        pygame.draw.rect(surface, Utils.SUPER_DARK_GRAY, self.rect, 0)
        pygame.draw.rect(surface, Utils.RED, self.rect, 3)
        find_space = self.name.find(' ')
        if (find_space > -1):
          label = (self.name[find_space+1:])[0]
        else:
          label = self.name[0]
        Utils.DrawText2Surface(surface, label, (self.rect[0]+10,self.rect[1]+5),20,Utils.RED)
      else:
        surface.blit(self.image_disabled,(self.rect[0],self.rect[1]))

  def AddChildren(self, child):
    self.children.append(child)


  def SetImages(self, image_enabled, image_disabled):
    self.image_enabled = image_enabled
    self.image_disabled = image_disabled

  def GetID(self):
    return self.ID



