import pygame
import Utils
from operator import itemgetter
import math
from datetime import datetime
import Clickable
import Events

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
    pad = (75,30)
    self.legend_width = 100
    self.x_axis_start = (pad[0]+self.legend_width, self.size[1]-pad[1])
    self.x_axis_end = (self.size[0]-pad[0]-self.legend_width, self.size[1]-pad[1])
    self.x_axis_length = abs(self.x_axis_start[0]-self.x_axis_end[0])
    self.y_axis_start = (pad[0]+self.legend_width, self.size[1]-pad[1])
    self.y_axis_end = (pad[0]+self.legend_width, pad[1])
    self.y_axis_length = abs(self.y_axis_start[1]-self.y_axis_end[1])
    self.data = {}
    self.colors = [Utils.BLUE, Utils.GREEN, Utils.RED, Utils.YELLOW, Utils.CYAN, Utils.LIGHT_GREEN, Utils.PURPLE2, Utils.ORANGE, Utils.AUQA_MARINE,
                   Utils.PINK, Utils.BROWN, Utils.OLIVE, Utils.BISQUE
                   #, Utils.TEAL, Utils.MED_GREEN, Utils.MED_YELLOW, Utils.LIGHT_CYAN
                   ]

    self.min_x = 10000000000000000000000000000
    self.max_x = -10000000000000000000000000000
    self.legendGUI_identifier = 'PlotLegend'

  def AddData(self, name, data, boundaries, axis = 0, unit = ''):
    self.min_x = min([self.min_x, boundaries[0][0]])
    self.max_x = max([self.max_x, boundaries[1][0]])
    self.data[name] = {'data': data,'Boundaries':boundaries, 'Enabled':True, 'Axis':axis, 'Unit':unit}


  def DrawAxis(self):
    axisColor = (255,255,255)
    pygame.draw.line(self.surface, axisColor, self.x_axis_start, self.x_axis_end)
    #Utils.DrawTriangle(self.surface, self.x_axis_end, axisColor, heading=0)
    pygame.draw.line(self.surface, axisColor, self.y_axis_start, self.y_axis_end)
    Utils.DrawTriangle(self.surface, self.y_axis_end, axisColor, heading=270)
    x2 = self.x_axis_end[0]
    pygame.draw.line(self.surface, axisColor, (x2, self.y_axis_start[1]), (x2, self.y_axis_end[1]))
    Utils.DrawTriangle(self.surface, (x2, self.y_axis_end[1]), axisColor, heading=270)
    pass


  def DrawAxisTicks(self, axisname, min_axis, max_axis, scale):
    axisColor = (255,255,255)
    t = self.GetAxisTickMarks(min_axis, max_axis)
    if (axisname == 'x'):
      for i in t:
        x_pos = (i-min_axis)*scale
        if (x_pos > 0) and (x_pos < self.x_axis_length):
          start = (self.x_axis_start[0]+x_pos, self.y_axis_start[1]+5)
          end = (self.x_axis_start[0]+x_pos, self.y_axis_start[1]-5)
          pygame.draw.line(self.surface, Utils.WHITE, start,end, 1)
          labelPos = (start[0]-20, start[1]+5)
          timestamp = i
          date_time = datetime.fromtimestamp(timestamp)
          Utils.DrawText2Surface(self.surface, date_time.strftime("%b %Y"), labelPos, 12, Utils.WHITE)
    elif(axisname[0] == 'y'):
      for i in t:
        y_pos = (i-min_axis)*scale
        if (y_pos >= 0) and (y_pos <= self.y_axis_length):
          start = (self.y_axis_start[0]-5, self.y_axis_start[1]-y_pos)
          end = (self.y_axis_start[0]+5, self.y_axis_start[1]-y_pos)
          labeloffset = 50
          if (axisname[1] == '2'):
            start = (start[0]+self.x_axis_length, start[1])
            end = (end[0]+self.x_axis_length,end[1])
            labeloffset = -15
          if (len(t) > 1):
            pygame.draw.line(self.surface, Utils.WHITE, start,end, 1)
            labelPos = (start[0]-labeloffset, start[1]-5)
            Utils.DrawText2Surface(self.surface, f"{i:,}", labelPos, 12, Utils.WHITE)


  def DrawData(self):
    colorIndex = 0
    x_spread = max(self.max_x-self.min_x,1)
    x_scale = self.x_axis_length/x_spread
    min_y1, max_y1, y_scale1, min_y2, max_y2, y_scale2 = self.GetYaxises()

    for dataName in self.data:
      color = self.colors[colorIndex%len(self.colors)]
      data = self.data[dataName]['data']
      if self.data[dataName]['Enabled']:
        x_start = data[0][0]
        y_start = data[0][1]
        sorted_data = sorted(data, key=itemgetter(0), reverse=False)
        points = []
        y_scale = y_scale1 if self.data[dataName]['Axis'] == 0 else y_scale2
        min_y =  min_y1 if self.data[dataName]['Axis'] == 0 else min_y2
        for datapoint in sorted_data:
          points.append(((datapoint[0]-self.min_x)*x_scale+self.x_axis_start[0],self.y_axis_start[1]-(datapoint[1]-min_y)*y_scale))
          pygame.draw.circle(self.surface, color, (points[-1][0],points[-1][1]),2)
        if (len(points)>1):
          pygame.draw.lines(self.surface, color, False, points, 2)
      colorIndex += 1
    
    self.DrawAxisTicks('x', self.min_x, self.max_x, x_scale)
    self.DrawAxisTicks('y1', min_y1, max_y1, y_scale1)
    self.DrawAxisTicks('y2', min_y2, max_y2, y_scale2)


  def DrawLegend(self):
    x1 = 10
    x2 = self.size[0]-self.legend_width-10
    y1 = 100
    y2 = 100
    colorIndex = 0
    leftLegendSize = 0
    rightLegendSize = 0
    for dataName in self.data:
      if (self.data[dataName]['Axis'] == 0):
        leftLegendSize +=1
      else:
        rightLegendSize +=1

    pygame.draw.rect(self.surface, Utils.BLACK, ((x1-5,y1-2),(self.legend_width, leftLegendSize * 20 + 4)))
    if (rightLegendSize):
      pygame.draw.rect(self.surface, Utils.BLACK, ((x2-5,y2-2),(self.legend_width, rightLegendSize * 20 + 4)))

    for dataName in self.data:
      color = self.colors[colorIndex%len(self.colors)]
      data = self.data[dataName]['data']
      if (self.data[dataName]['Axis'] == 0):
        labelPos = (x1, y1)
      else:
        labelPos = (x2, y2)
      unit = self.data[dataName]['Unit']
      label = dataName + ((' ('+unit+')') if unit != '' else '')
      rect = Utils.DrawText2Surface(self.surface, label, labelPos, 14, color)
      self.game.MakeClickable(dataName, rect, self.ToggleDataPlot, par=dataName, parent=self.legendGUI_identifier, anchor = self.anchor)
      if (not self.data[dataName]['Enabled']):
        pygame.draw.line(self.surface, color, (labelPos[0],labelPos[1]+8), (labelPos[0]+rect[1][0],labelPos[1]+8))
      if (self.data[dataName]['Axis'] == 0):
        y1+=20
      else:
        y2+=20
      colorIndex += 1


  def GetYaxises(self):
    min_y1 = 10000000000000000000000000000
    min_y2 = 10000000000000000000000000000
    max_y1 = -10000000000000000000000000000
    max_y2 = -10000000000000000000000000000

    for dataName in self.data:
      data = self.data[dataName]
      if (data['Enabled']):
        if (data['Axis'] == 0):
          min_y1 = min([min_y1, data['Boundaries'][0][1]])
          max_y1 = max([max_y1, data['Boundaries'][1][1]])
        elif (data['Axis'] == 1):
          min_y2 = min([min_y2, data['Boundaries'][0][1]])
          max_y2 = max([max_y2, data['Boundaries'][1][1]])

    y_spread1 = max(max_y1-min_y1,1)
    y_spread2 = max(max_y2-min_y2,1)
    y_scale1 = self.y_axis_length/y_spread1
    y_scale2 = self.y_axis_length/y_spread2

    return min_y1, max_y1, y_scale1, min_y2, max_y2, y_scale2


  def GetAxisTickMarks(self, min_value, max_value):
    spread = max_value - min_value
    x = [min_value]
    if (spread > 0):
      l = int(math.log(spread,10))
      factor = max(0.5,10**l)

      start = int(min_value/factor)*factor
      end = int(max_value/factor+1)*factor
      num = 0
      while num < 10 and factor > 0:
        x = list(range(start, end, factor))
        num = len(x)
        factor = int(factor / 2)
    return x


  def Draw(self, screen):
    reblit = False
    self.reDraw = True
    # clear screen
    if (self.reDraw):

      #if (self.Events):
      self.events.ClearClickables(exclude='EconomyTabs')
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      pygame.draw.rect(self.surface, Utils.GRAY, ((0,0),(self.size)),3)
      self.DrawAxis()
      self.DrawData()
      self.DrawLegend()
      
      reblit = True

    #reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      screen.blit(self.surface,self.anchor)

    self.reDraw = False
    
    return reblit


  def ToggleDataPlot(self, name, parent, mousepos = None):
    if name in self.data:
      self.data[name]['Enabled'] = not self.data[name]['Enabled']
      self.context.reDraw = True
