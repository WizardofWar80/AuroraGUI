import pygame
import Utils
import Clickable


class Scrollbar():
  def __init__(self, surface, pos, height, visible_range, total_range, parent, game):
    self.surface = surface
    self.game = game
    self.width = 20
    self.height = height
    self.rect = pygame.Rect(pos[0], pos[1], self.width, height)
    self.visible_range = visible_range
    self.total_range = total_range
    self.invisible_range = self.total_range-self.visible_range
    self.current_position = 0
    self.parent = parent
    self.bg_color = (0,0,0)
    self.edge_color = Utils.GRAY
    self.color = Utils.LIGHT_GRAY
    self.upArrow = pygame.Rect(self.rect[0], self.rect[1], self.width, self.width)
    self.dnArrow = pygame.Rect(self.rect[0], self.rect[1]+self.height-self.width, self.width, self.width)
    self.bar_height = (self.visible_range/self.total_range)*(self.height-2*self.width)
    self.clickable = self.game.MakeClickable('Scrollbar', self.rect, self.Click, parent=self, persistent = True)
    horiz_bar_pos = self.current_position*(self.height-2*self.width-self.bar_height)+self.rect[1]+self.width
    self.barRect = pygame.Rect(self.rect[0]+2, horiz_bar_pos+1, self.width-4, self.bar_height-1)
    self.reDraw = True


  def Update(self, pos = None, height = None, visible_range = None, total_range = None, current_position = None ):
    if (pos is not None):
      self.rect = pygame.Rect(pos[0], pos[1], self.width, self.height)
      self.upArrow = pygame.Rect(self.rect[0], self.rect[1], self.width, self.width)
      self.dnArrow = pygame.Rect(self.rect[0], self.rect[1]+self.height-self.width, self.width, self.width)
    if (height is not None):
      self.height = height
      self.rect = pygame.Rect(self.rect[0], self.rect[1], self.width, self.height)
      self.dnArrow = pygame.Rect(self.rect[0], self.rect[1]+self.height-self.width, self.width, self.width)
    if (visible_range is not None):
      self.visible_range = visible_range
      self.invisible_range = self.total_range-self.visible_range
      self.bar_height = (self.visible_range/self.total_range)*(self.height-2*self.width)
    if (total_range is not None):
      self.total_range = total_range
      self.invisible_range = self.total_range-self.visible_range
      self.bar_height = (self.visible_range/self.total_range)*(self.height-2*self.width)
    if (current_position is not None):
      self.current_position = current_position/self.invisible_range
    self.MoveBar()
    self.clickable.rect = self.rect
    self.reDraw = True


  def MoveBar(self):
    horiz_bar_pos = self.current_position*(self.height-2*self.width-self.bar_height)+self.rect[1]+self.width
    self.barRect = pygame.Rect(self.rect[0]+2, horiz_bar_pos+1, self.width-4, self.bar_height-1)


  def Draw(self):
    if (self.reDraw):
      # Draw Background
      pygame.draw.rect(self.surface, self.bg_color, self.rect, 0)
      # Draw Up Arrow Box
      pygame.draw.rect(self.surface, self.color, self.upArrow, 0)
      Utils.DrawSizedTriangle(self.surface,(self.upArrow[0]+10,self.upArrow[1]+10),Utils.BLACK,[6,4], 0, upside_down = False)
      # Draw Dn Arrow Box
      pygame.draw.rect(self.surface, self.color, self.dnArrow, 0)
      Utils.DrawSizedTriangle(self.surface,(self.dnArrow[0]+10,self.dnArrow[1]+8),Utils.BLACK,[6,4], 0, upside_down = True)
      # Draw bar
      horiz_bar_pos = self.current_position*(self.height-2*self.width-self.bar_height)+self.rect[1]+self.width
      bar_rect = pygame.Rect(self.rect[0]+2, horiz_bar_pos+1, self.width-4, self.bar_height-1)
      pygame.draw.rect(self.surface, self.color, bar_rect, 0)
      # Draw outside edge
      pygame.draw.rect(self.surface, self.edge_color, self.rect, 1)
      return True
    else:
      return False


  def Click(self, par, parent, mousepos):
    if (self.upArrow.collidepoint(mousepos)):
      self.parent.scroll_position+=1
      self.current_position=-self.parent.scroll_position/self.invisible_range
      self.MoveBar()
      self.parent.context.UpdateTable()
      print('UpArrow')
    elif (self.dnArrow.collidepoint(mousepos)):
      self.parent.scroll_position-=1
      self.current_position=-self.parent.scroll_position/self.invisible_range
      self.MoveBar()
      self.parent.context.UpdateTable()
      print('DownArrow')
    elif (self.barRect.collidepoint(mousepos)):
      pass
    else:
      print('current pos:', self.current_position)
      ticks_above = self.invisible_range*(self.current_position)
      ticks_below = self.invisible_range*(1-self.current_position)
      if (mousepos[1] < self.barRect[1]):
        scrollbar_inside_start = self.upArrow[1] + self.upArrow[3]
        percentage = (mousepos[1] - scrollbar_inside_start)/(self.barRect[1]-scrollbar_inside_start)
        self.parent.scroll_position = -int(ticks_above*percentage)
        self.current_position=-self.parent.scroll_position/self.invisible_range
        self.MoveBar()
        self.parent.context.UpdateTable()
        # above bar
      elif (mousepos[1] > self.barRect[1]+self.barRect[3]):
        scrollbar_inside_end = self.dnArrow[1]
        percentage = (mousepos[1] - (self.barRect[1]+self.barRect[3]))/(scrollbar_inside_end-(self.barRect[1]+self.barRect[3]))
        self.parent.scroll_position=-(ticks_above+int(ticks_below*percentage)+1)
        self.current_position=-self.parent.scroll_position/self.invisible_range
        self.MoveBar()
        self.parent.context.UpdateTable()



