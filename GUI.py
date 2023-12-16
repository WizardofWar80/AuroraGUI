import pygame
import Utils

GUI_LABEL_POS_TOP = 'Top'
GUI_LABEL_POS_LEFT = 'Left'
GUI_LABEL_POS_RIGHT = 'Right'
GUI_LABEL_POS_BOTTOM = 'Bottom'

class GUI():
  def __init__(self, gameClass, id, name, rect, clickable, type, parent = None, enabled = True, parentName = '', tab = False, textButton = False, radioButton = False, radioGroup = None, state = 0, content = [], dropUp = False, showLabel = False, labelPos = GUI_LABEL_POS_TOP, latching = True, tooltip = ''):
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
    self.latching = latching
    self.radioButton = radioButton
    self.radioGroup = radioGroup
    self.dropdownSelection = None
    self.extendedBB = None
    self.scroll_position = 0
    self.children = []
    self.labelPos = labelPos
    self.content = content
    self.maxLength = 10
    self.maxScroll = 0
    self.dropUp = dropUp
    self.isTab = tab
    if (tooltip == ''):
      self.tooltip = name
    else:
      self.tooltip = tooltip
    self.image_enabled = None
    self.image_disabled = None
    self.visible = True if (parent == None) else False
    self.clickable = clickable
    self.label = self.name
    self.showLabel = showLabel
    self.insideColor = Utils.SUPER_DARK_GRAY
    if (type == 'Dropdown'):
      num_entries = len(self.content)
      max_entries = min(self.maxLength,num_entries)
      if (num_entries > 1):
        if (self.dropUp):
          self.extendedBB = pygame.Rect((self.rect[0],self.rect[1]-self.rect[3]*max_entries),(self.rect[2]-self.rect[3], self.rect[3]*max_entries))
        else:
          self.extendedBB = pygame.Rect((self.rect[0],self.rect[1]+self.rect[3]),(self.rect[2]-self.rect[3], self.rect[3]*max_entries))
        self.maxScroll = min(0,self.maxLength-num_entries)
      else:
        self.extendedBB = pygame.Rect((self.rect[0],self.rect[1]),(self.rect[2],self.rect[3]))


  def Draw(self, surface):
    if (self.showLabel):
      if (self.labelPos == GUI_LABEL_POS_TOP):
        labelOffset = (0,-25)
      elif (self.labelPos == GUI_LABEL_POS_LEFT):
        labelOffset = (-100,0)
      elif (self.labelPos == GUI_LABEL_POS_RIGHT):
        labelOffset = (self.rect[3]+5,0)
      elif (self.labelPos == GUI_LABEL_POS_BOTTOM):
        labelOffset = (0,self.rect[2]+3)
      Utils.DrawText2Surface(surface, self.label, (self.rect[0]+labelOffset[0], self.rect[1]+labelOffset[1]),20,Utils.GRAY)

    if (self.type == 'Button'):
      button_text = self.name
      if (not self.textButton) and (self.type == 'Button'):
        find_space = self.name.find(' ')
        if (find_space > -1):
          button_text = (self.name[find_space+1:])[0]
        else:
          button_text = self.name[0]

      if (not self.enabled or self.children or not self.latching):
        if (self.isTab):
          temp_surf = pygame.Surface((self.rect[2], self.rect[3]), pygame.SRCALPHA,32)
          pos = (0, 0)
          size = (self.rect[2], self.rect[3]+5)
          pygame.draw.rect(temp_surf, Utils.GRAY, (pos,size), 3,5)
          Utils.DrawText2Surface(temp_surf, button_text, (pos[0]+10,pos[1]+5),20,Utils.GRAY)
          surface.blit(temp_surf,(self.rect[0],self.rect[1]))
        else:
          if (not self.image_disabled):
            pygame.draw.rect(surface, self.insideColor, self.rect, 0)
            pygame.draw.rect(surface, Utils.GRAY, self.rect, 3)
            offset = (10,5)
            if (len(button_text) == 1):
              if (self.rect[2] < 28):
                offset = (5,-2)
            #  offset = (self.rect[2]/2,self.rect[3]/2)
            #Utils.DrawTextCenteredAt(surface, button_text, self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2, pygame.font.SysFont("Times New Roman", 20, bold = True), Utils.GRAY)
            Utils.DrawText2Surface(surface, button_text, (self.rect[0]+offset[0],self.rect[1]+offset[1]),20,Utils.GRAY)
            #pygame.draw.rect(surface, Utils.RED, (self.rect[0]+offset[0],self.rect[1]+offset[1],1,1), 0)
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
          Utils.DrawText2Surface(temp_surf, button_text, (pos[0]+10,pos[1]+5),20,Utils.LIGHT_BLUE)
          surface.blit(temp_surf,(self.rect[0],self.rect[1]))
          pygame.draw.rect(surface, self.insideColor, (((self.rect[0]+3, self.rect[1]+size[1]-6)),(size[0]-6, 5)), 0)
        else:
          if (not self.image_enabled):
            pygame.draw.rect(surface, self.insideColor, self.rect, 0)
            pygame.draw.rect(surface, Utils.LIGHT_BLUE, self.rect, 3)
            Utils.DrawText2Surface(surface, button_text, (self.rect[0]+10,self.rect[1]+5),20,Utils.LIGHT_BLUE)
        
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


  def DrawTooltip(self, surface):
    if (self.clickable and self.clickable.hover):
      if (self.name.find('Table') == -1):
        tooltip_position = (self.clickable.mousepos[0]+13,self.clickable.mousepos[1])
        #tooltip_position = (self.rect[0]+self.rect[2]+self.labelOffset[0], self.rect[1]+self.labelOffset[1])
        text_width = len(self.tooltip)*10
        while (tooltip_position[0] > surface.get_rect()[2]-text_width-25):
          tooltip_position = (tooltip_position[0]-10,self.clickable.mousepos[1]+15)
        
        while (tooltip_position[1] < 10):
          tooltip_position = (tooltip_position[0],tooltip_position[1]+10)
        while (tooltip_position[1] > surface.get_rect()[3]-20):
          tooltip_position = (tooltip_position[0],tooltip_position[1]-10)
        Utils.DrawText2Surface(surface, self.tooltip, tooltip_position, 20, Utils.GRAY, transparent=False)
        return True
    return False


  def ClearContent(self):
    self.content = []
    self.self.dropdropdownSelection = -1


  def AddContent(self, text):
    self.content.append(text)


  def AddChildren(self, child):
    self.children.append(child)


  def SetImages(self, images_list, name_image_enabled, name_image_disabled = None):
    name_image_enabled_lower = name_image_enabled.lower()
    if (name_image_enabled_lower in images_list):
      self.image_enabled = images_list[name_image_enabled_lower]
    if (name_image_disabled):
      name_image_disabled_lower = name_image_disabled.lower()
      if (name_image_disabled_lower in images_list):
        self.image_disabled = images_list[name_image_disabled_lower]
    else:
      if (not self.latching):
        if (name_image_enabled_lower in images_list):
          self.image_disabled = images_list[name_image_enabled_lower]

  def GetID(self):
    return self.ID




