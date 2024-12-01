import pygame
import Utils
from operator import itemgetter
import math
from datetime import datetime
import Clickable
import Events

class Tab():
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

    #self.x_axis_start = (pad[0]+self.legend_width, self.size[1]-pad[1])
    #self.x_axis_end = (self.size[0]-pad[0]-self.legend_width, self.size[1]-pad[1])
    #self.x_axis_length = abs(self.x_axis_start[0]-self.x_axis_end[0])
    #self.y_axis_start = (pad[0]+self.legend_width, self.size[1]-pad[1])
    #self.y_axis_end = (pad[0]+self.legend_width, pad[1])
    #self.y_axis_length = abs(self.y_axis_start[1]-self.y_axis_end[1])
    self.data = {}
    #self.colors = [Utils.BLUE, Utils.GREEN, Utils.RED, Utils.YELLOW, Utils.CYAN, Utils.LIGHT_GREEN, Utils.PURPLE2, Utils.ORANGE, Utils.AUQA_MARINE,
    #               Utils.PINK, Utils.BROWN, Utils.OLIVE, Utils.BISQUE
    #               #, Utils.TEAL, Utils.MED_GREEN, Utils.MED_YELLOW, Utils.LIGHT_CYAN
    #               ]

  def AddData(self, name, data, boundaries, axis = 0, unit = ''):
    pass
    #self.min_x = min([self.min_x, boundaries[0][0]])
    #self.max_x = max([self.max_x, boundaries[1][0]])
    #self.data[name] = {'data': data,'Boundaries':boundaries, 'Enabled':True, 'Axis':axis, 'Unit':unit}


  def DrawData(self):
    pass
    #colorIndex = 0
    #x_spread = max(self.max_x-self.min_x,1)
    #x_scale = self.x_axis_length/x_spread
    #min_y1, max_y1, y_scale1, min_y2, max_y2, y_scale2 = self.GetYaxises()

    #for dataName in self.data:
    #  color = self.colors[colorIndex%len(self.colors)]
    #  data = self.data[dataName]['data']
    #  if self.data[dataName]['Enabled']:
    #    x_start = data[0][0]
    #    y_start = data[0][1]
    #    sorted_data = sorted(data, key=itemgetter(0), reverse=False)
    #    points = []
    #    y_scale = y_scale1 if self.data[dataName]['Axis'] == 0 else y_scale2
    #    min_y =  min_y1 if self.data[dataName]['Axis'] == 0 else min_y2
    #    for datapoint in sorted_data:
    #      points.append(((datapoint[0]-self.min_x)*x_scale+self.x_axis_start[0],self.y_axis_start[1]-(datapoint[1]-min_y)*y_scale))
    #      pygame.draw.circle(self.surface, color, (points[-1][0],points[-1][1]),2)
    #    if (len(points)>1):
    #      pygame.draw.lines(self.surface, color, False, points, 2)
    #  colorIndex += 1
    
    #self.DrawAxisTicks('x', self.min_x, self.max_x, x_scale)
    #self.DrawAxisTicks('y1', min_y1, max_y1, y_scale1)
    #self.DrawAxisTicks('y2', min_y2, max_y2, y_scale2)


  def Draw(self, screen):
    reblit = False
    self.reDraw = True
    # clear screen
    if (self.reDraw):

      #if (self.Events):
      self.events.ClearClickables(exclude='CommandTabs')
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      pygame.draw.rect(self.surface, Utils.GRAY, ((0,0),(self.size)),3)
      self.DrawData()
      
      reblit = True

    #reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      screen.blit(self.surface,self.anchor)

    self.reDraw = False
    
    return reblit

