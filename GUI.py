import pygame
import Utils

class GUI():
  def __init__(self, gameClass, id, name, rect, clickable, parent = None, enabled = True, parentName = '', tab = False, textButton = False, radioButton = False, radioGroup = None, state = 0):
    self.ID = id
    self.name = name
    self.rect = rect
    self.gameClass = gameClass
    self.parent = parent
    self.parentName = parentName
    self.open = False
    self.textButton = textButton
    self.enabled = enabled
    self.state = state
    self.radioButton = radioButton
    self.radioGroup = radioGroup
    self.children = []
    self.isTab = tab
    self.tooltip = 'This is a GUI element'
    self.image_enabled = None
    self.image_disabled = None
    self.visible = True if (parent == None) else False
    self.clickable = clickable
    self.label = self.name
    self.insideColor = Utils.SUPER_DARK_GRAY
    if (not self.textButton):
      find_space = self.name.find(' ')
      if (find_space > -1):
        self.label = (self.name[find_space+1:])[0]
      else:
        self.label = self.name[0]

  def Draw(self, surface):
    if (not self.enabled or self.children):
      if (self.isTab):
        temp_surf = pygame.Surface((self.rect[2], self.rect[3]), pygame.SRCALPHA,32)
        pos = (0, 0)
        size = (self.rect[2], self.rect[3]+5)
        pygame.draw.rect(temp_surf, Utils.GRAY, (pos,size), 3,5)
        Utils.DrawText2Surface(temp_surf, self.label, (pos[0]+10,pos[1]+5),20,Utils.GRAY)
        surface.blit(temp_surf,(self.rect[0],self.rect[1]))
      else:
        if (not self.image_disabled):
          pygame.draw.rect(surface, self.insideColor, self.rect, 0)
          pygame.draw.rect(surface, Utils.GRAY, self.rect, 3)
          Utils.DrawText2Surface(surface, self.label, (self.rect[0]+10,self.rect[1]+5),20,Utils.GRAY)
          if self.children:
            Utils.DrawSizedTriangle(surface, (self.rect[0]+25,self.rect[1]+7), Utils.GRAY, 4, 1)
        else:
          surface.blit(self.image_disabled,(self.rect[0],self.rect[1]))
    else:
      if (self.isTab):
        temp_surf = pygame.Surface((self.rect[2], self.rect[3]), pygame.SRCALPHA,32)
        
        pos = (0, 0)
        size = (self.rect[2], self.rect[3]+5)
        pygame.draw.rect(temp_surf, self.insideColor, ((pos[0]+3,pos[1]+3),(size[0]-6, size[1]-6)), 0)
        pygame.draw.rect(temp_surf, Utils.GRAY, (pos,size), 3,5)
        Utils.DrawText2Surface(temp_surf, self.label, (pos[0]+10,pos[1]+5),20,Utils.LIGHT_BLUE)
        surface.blit(temp_surf,(self.rect[0],self.rect[1]))
        pygame.draw.rect(surface, self.insideColor, (((self.rect[0]+3, self.rect[1]+size[1]-6)),(size[0]-6, 5)), 0)
      else:
        if (not self.image_enabled):
          pygame.draw.rect(surface, self.insideColor, self.rect, 0)
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



