from Screen import Screen
import sqlite3
import pygame
import Plot

class EconomyScreen(Screen):
  def __init__(self, game, events):
    self.reDraw = True
    self.reDraw_GUI = True
    self.game = game
    self.width = game.width
    self.height = game.height

    self.screenCenterBeforeDrag = self.game.screenCenter
    self.FPS = 0
    self.counter_FPS = 0
    self.timestampLastSecond = pygame.time.get_ticks()
    self.timestampLast = pygame.time.get_ticks()
    
    self.cameraCenter = (self.width/2,self.height/2)
    self.screenCenter = (self.width/2,self.height/2)

    self.mouseDragged = (0,0)
    # Options
    self.Events = events
    self.surface = game.surface
    self.screen = game.screen
    self.bg_color = game.bg_color

    self.GUI_Elements = {}
    self.images_GUI = {}
    self.plot = Plot.Plot(self.game, self.Events, self, (game.width-100,game.height-game.GUI_Top_Anchor[1]-100), (50,100))
    self.GetWealthData()
    self.GetPopulationData()
    self.GetStockpileData()
    self.GetShipData()
    self.GetStationData()

  
  def GetWealthData(self):
    results = self.game.db.execute('''SELECT IncrementTime, WealthAmount from FCT_WealthHistory WHERE GameID = %d and RaceID = %d;'''%(self.game.gameID, self.game.myRaceID)).fetchall()
    self.wealthHistory = []
    min_x = 10000000000000000000000000000
    min_y = 10000000000000000000000000000
    max_x = -10000000000000000000000000000
    max_y = -10000000000000000000000000000
    for tuple in results:
      value = tuple[1]
      ts = int(tuple[0])
      min_x = min([min_x, tuple[0]])
      min_y = min([min_y, tuple[1]])
      max_x = max([max_x, tuple[0]])
      max_y = max([max_y, tuple[1]])
      self.wealthHistory.append([ts, value])
    self.plot.AddData('Wealth', self.wealthHistory, ((min_x,min_y),(max_x,max_y)), axis = 1)


  def GetPopulationData(self):
    history = []
    min_x = 10000000000000000000000000000
    min_y = 10000000000000000000000000000
    max_x = -10000000000000000000000000000
    max_y = -10000000000000000000000000000
    unit = 'k'
    for timestamp in self.game.statisticsPopulation:
      value = self.game.statisticsPopulation[timestamp]*1000
      ts = int(timestamp)
      min_x = min([min_x, ts])
      min_y = min([min_y, value])
      max_x = max([max_x, ts])
      max_y = max([max_y, value])
      history.append([ts, value])
    self.plot.AddData('Population', history, ((min_x,min_y),(max_x,max_y)), unit=unit)


  def GetStockpileData(self):
    for name in self.game.statisticsStockpile:
      unit = ''
      min_x = 10000000000000000000000000000
      min_y = 10000000000000000000000000000
      max_x = -10000000000000000000000000000
      max_y = -10000000000000000000000000000
      history = []
      for timestamp in self.game.statisticsStockpile[name]:
        value = self.game.statisticsStockpile[name][timestamp]
        ts = int(timestamp)
        min_x = min([min_x, ts])
        min_y = min([min_y, value])
        max_x = max([max_x, ts])
        max_y = max([max_y, value])
        history.append([ts, value])
      if (max_y > 1000000):
        for i in range(len(history)):
          history[i][1]*=0.001
        min_y *= 0.001
        max_y *= 0.001
      self.plot.AddData(name, history, ((min_x,min_y),(max_x,max_y)), unit=unit)


  def GetShipData(self):
    min_x = 10000000000000000000000000000
    min_y = 10000000000000000000000000000
    max_x = -10000000000000000000000000000
    max_y = -10000000000000000000000000000
    history = []
    for timestamp in self.game.statisticsShips:
      value = self.game.statisticsShips[timestamp]
      ts = int(timestamp)
      min_x = min([min_x, ts])
      min_y = min([min_y, value])
      max_x = max([max_x, ts])
      max_y = max([max_y, value])
      history.append([ts, value])
    self.plot.AddData('Ships', history, ((min_x,min_y),(max_x,max_y)))


  def GetStationData(self):
    min_x = 10000000000000000000000000000
    min_y = 10000000000000000000000000000
    max_x = -10000000000000000000000000000
    max_y = -10000000000000000000000000000
    history = []
    for timestamp in self.game.statisticsStations:
      value = self.game.statisticsStations[timestamp]
      ts = int(timestamp)
      min_x = min([min_x, ts])
      min_y = min([min_y, value])
      max_x = max([max_x, ts])
      max_y = max([max_y, value])
      history.append([ts, value])
    self.plot.AddData('Stations', history, ((min_x,min_y),(max_x,max_y)))


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      self.plot.Draw(self.surface)

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit