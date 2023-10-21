import pygame
import Utils
from operator import itemgetter
import math
from datetime import datetime

class Plot():
  def __init__(self, game, events, context, size, anchor):
    self.game = game
    self.events = events
    self.context = context
    self.surface = pygame.Surface(size, pygame.SRCALPHA,32)
    self.reDraw = True
    self.bg_color = Utils.SUPER_DARK_GRAY
    self.size = size
    self.anchor = anchor
    pad = (100,30)
    self.x_axis_start = (pad[0], self.size[1]-pad[1])
    self.x_axis_end = (self.size[0]-pad[0], self.size[1]-pad[1])
    self.x_axis_length = abs(self.x_axis_start[0]-self.x_axis_end[0])
    self.y_axis_start = (pad[0], self.size[1]-pad[1])
    self.y_axis_end = (pad[0], pad[1])
    self.y_axis_length = abs(self.y_axis_start[1]-self.y_axis_end[1])
    self.data = {}


  def AddData(self, name, data):
    self.data[name] = data


  def DrawAxis(self):
    axisColor = (255,255,255)
    pygame.draw.line(self.surface, axisColor, self.x_axis_start, self.x_axis_end)
    Utils.DrawTriangle(self.surface, self.x_axis_end, axisColor, heading=0)
    pygame.draw.line(self.surface, axisColor, self.y_axis_start, self.y_axis_end)
    Utils.DrawTriangle(self.surface, self.y_axis_end, axisColor, heading=270)
    pass


  def DrawAxisTicks(self, min_x, min_y, max_x, max_y, x_scale, y_scale):
    axisColor = (255,255,255)
    x = self.GetAxisTickMarks(min_x, max_x)
    for i in x:
      x_pos = (i-min_x)*x_scale
      if (x_pos > 0) and (x_pos < self.x_axis_length):
        start = (self.x_axis_start[0]+x_pos, self.y_axis_start[1]+5)
        end = (self.x_axis_start[0]+x_pos, self.y_axis_start[1]-5)
        pygame.draw.line(self.surface, Utils.WHITE, start,end, 1)
        labelPos = (start[0]-20, start[1]+5)
        timestamp = i
        date_time = datetime.fromtimestamp(timestamp)
        Utils.DrawText2Surface(self.surface, date_time.strftime("%b %Y"), labelPos, 12, Utils.WHITE)

    y = self.GetAxisTickMarks(min_y, max_y)
    for i in y:
      y_pos = (i-min_y)*y_scale
      if (y_pos > 0) and (y_pos < self.y_axis_length):
        start = (self.y_axis_start[0]-5, self.y_axis_start[1]-y_pos)
        end = (self.y_axis_start[0]+5, self.y_axis_start[1]-y_pos)
        pygame.draw.line(self.surface, Utils.WHITE, start,end, 1)
        labelPos = (start[0]-40, start[1]-5)
        Utils.DrawText2Surface(self.surface, str(i), labelPos, 12, Utils.WHITE)



  def DrawData(self):
    for dataName in self.data:
      data = self.data[dataName]
      min_x = 1000000000000000000000000
      min_y = 1000000000000000000000000
      max_x = -1000000000000000000000000
      max_y = -1000000000000000000000000
      for datapoint in data:
        min_x = min(min_x, datapoint[0])
        max_x = max(max_x, datapoint[0])
        min_y = min(min_y, datapoint[1])
        max_y = max(max_y, datapoint[1])
      x_start = data[0][0]
      y_start = data[0][1]
      sorted_data = sorted(data, key=itemgetter(0), reverse=False)
      x_spread = max_x-min_x
      y_spread = max_y-min_y
      x_scale = self.x_axis_length/x_spread
      y_scale = self.y_axis_length/y_spread
      points = []
      for datapoint in sorted_data:
        points.append(((datapoint[0]-min_x)*x_scale+self.x_axis_start[0],self.y_axis_start[1]-(datapoint[1]-min_y)*y_scale))
      pygame.draw.lines(self.surface, Utils.BLUE, False, points, 1)
      self.DrawAxisTicks(min_x, min_y, max_x, max_y, x_scale, y_scale)



  def GetAxisTickMarks(self, min, max):
    spread = max - min
    l = int(math.log(spread,10))
    factor = 10**l
    #print(min/factor)
    start = int(min/factor)*factor
    end = int(max/factor+1)*factor
    num = 0
    while num < 10:
      x = list(range(start, end, factor))
      num = len(x)
      factor = int(factor / 2)
    return x

  def Draw(self, screen):
    reblit = False
    # clear screen
    if (self.reDraw):
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      self.DrawAxis()
      self.DrawData()
      
      reblit = True

    #reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      screen.blit(self.surface,self.anchor)

    self.reDraw = False
    
    return reblit
