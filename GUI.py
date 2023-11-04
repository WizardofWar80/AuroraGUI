import pygame
import Utils

class GUI():
  def __init__(self, gameClass, id, name, rect, clickable, type, parent = None, enabled = True, parentName = '', tab = False, textButton = False, radioButton = False, radioGroup = None, state = 0, content = [], dropUp = False):
    self.ID = id
    self.type = type
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
    self.dropdownSelection = None
    self.extendedBB = None
    self.scroll_position = 0
    self.children = []
    self.content = content
    self.maxLength = 10
    self.maxScroll = 0
    self.dropUp = dropUp
    self.isTab = tab
    self.tooltip = name
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
    if (type == 'Dropdown'):
      num_entries = len(self.content)
      max_entries = min(self.maxLength,num_entries)
      if (num_entries > 1):
        if (self.dropUp):
          self.extendedBB = pygame.Rect((self.rect[0],self.rect[1]-self.rect[3]*max_entries),(self.rect[2]-self.rect[3], self.rect[3]*max_entries))
        else:
          self.extendedBB = pygame.Rect((self.rect[0],self.rect[1]+self.rect[3]),(self.rect[2]-self.rect[3], self.rect[3]*max_entries))
        self.maxScroll = min(0,self.maxLength-num_entries)


  def Draw(self, surface):
    if (self.type == 'Button'):
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
    elif (self.type == 'Dropdown'):
      temp_surf = pygame.Surface((self.rect[2], self.rect[3]), pygame.SRCALPHA,32)
      pos = (0, 0)
      size = (self.rect[2], self.rect[3])
      pygame.draw.rect(temp_surf, self.insideColor, ((pos[0],pos[1]),(size[0], size[1])), 0)
      pygame.draw.rect(temp_surf, Utils.GRAY, (pos,size), 2)
      text=''
      if (len(self.content) > 0) and (self.dropdownSelection > -1) and (self.dropdownSelection < len(self.content)):
        text = self.content[self.dropdownSelection]
      Utils.DrawText2Surface(temp_surf, text, (pos[0]+5,pos[1]+1),20,Utils.WHITE)
      pygame.draw.rect(temp_surf, Utils.GRAY, ((pos[0]+size[0]-self.rect[3],pos[1]),(self.rect[3], self.rect[3])), 0)
      Utils.DrawSizedTriangle(temp_surf,(pos[0]+size[0]-self.rect[3]+13,pos[1]+10),Utils.BLACK,[8,4], 0, upside_down = True)
      surface.blit(temp_surf,(self.rect[0],self.rect[1]))
      if self.open:
        num_entries = len(self.content)
        if (num_entries > 1):
          pygame.draw.rect(surface, self.insideColor, self.extendedBB, 0)
          pygame.draw.rect(surface, Utils.GRAY, self.extendedBB, 2)
          lineNr = 0
          for i in range(num_entries):
            if (self.scroll_position+i >= 0):
              text= self.content[i]
              if (len(self.content) > 0) and (self.dropdownSelection > -1) and (self.dropdownSelection < len(self.content)):
                text = self.content[i]
              Utils.DrawText2Surface(surface, text, (self.extendedBB[0]+5,self.extendedBB[1]+1+lineNr*self.rect[3]),20,Utils.WHITE)
              lineNr += 1
              if (lineNr >= self.maxLength):
                break


  def ClearContent(self):
    self.content = []
    self.self.dropdropdownSelection = -1


  def AddContent(self, text):
    self.content.append(text)


  def AddChildren(self, child):
    self.children.append(child)


  def SetImages(self, image_enabled, image_disabled):
    self.image_enabled = image_enabled
    self.image_disabled = image_disabled


  def GetID(self):
    return self.ID




