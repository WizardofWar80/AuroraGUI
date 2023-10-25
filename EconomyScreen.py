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
    for tuple in results:
      self.wealthHistory.append([tuple[0], tuple[1]])
    self.plot.AddData('Wealth', self.wealthHistory)


  def GetPopulationData(self):
    self.history = []
    for timestamp in self.game.statisticsPopulation:
      self.history.append([int(timestamp), self.game.statisticsPopulation[timestamp]])
    self.plot.AddData('Population', self.history)


  def GetStockpileData(self):
    for name in self.game.statisticsStockpile:
      self.history = []
      for timestamp in self.game.statisticsStockpile[name]:
        self.history.append([int(timestamp), self.game.statisticsStockpile[name][timestamp]])
      self.plot.AddData(name, self.history)


  def GetShipData(self):
    self.history = []
    for timestamp in self.game.statisticsShips:
      self.history.append([int(timestamp), self.game.statisticsShips[timestamp]])
    self.plot.AddData('Ships', self.history)


  def GetStationData(self):
    self.history = []
    for timestamp in self.game.statisticsShips:
      self.history.append([int(timestamp), self.game.statisticsStations[timestamp]])
    self.plot.AddData('Stations', self.history)


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