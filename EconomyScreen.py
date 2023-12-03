from Screen import Screen
import sqlite3
import pygame
import Plot
import Events
import Clickable
import GUI

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

    self.GUI_Button_Size = (100,30)
    self.GUI_Elements = {}
    self.GUI_identifier = 'EconomyTabs'
    self.images_GUI = {}
    self.tab_pos = (50,100)
    self.plot_size = (game.width-100,game.height-game.GUI_Top_Anchor[1]-100)
    self.tabs = {'Stockpiles': Plot.Plot(self.game, self.Events, self, self.plot_size, self.tab_pos ),
                 'Economy': Plot.Plot(self.game, self.Events, self, self.plot_size, self.tab_pos),
                 'Military': Plot.Plot(self.game, self.Events, self, self.plot_size, self.tab_pos)
                 }
    self.active_tab = 'Economy'
    #self.UpdateEconomyData()


  def UpdateEconomyData(self):
    if (self.GUI_Elements == {}):
      self.InitGUI()
    else:
      self.UpdateGUI()

    self.GetWealthData()
    self.GetPopulationData()
    self.GetStockpileData()
    self.GetShipData()
    self.GetStationData()


  def UpdateGUI(self):
    pass


  def InitGUI(self):
    idGUI = 1
    x = self.tab_pos[0]
    y = self.tab_pos[1]-self.GUI_Button_Size[1]
    bb = (x,y,self.GUI_Button_Size[0],self.GUI_Button_Size[1])
    name = 'Economy'
    gui_cl = self.game.MakeClickable(name, bb, self.SwitchTabs, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, tab = True, enabled = True if self.active_tab == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Button_Size[0]+5
    bb = (x,y,self.GUI_Button_Size[0],self.GUI_Button_Size[1])
    name = 'Stockpiles'
    gui_cl = self.game.MakeClickable(name, bb, self.SwitchTabs, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, tab = True, enabled = True if self.active_tab == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Button_Size[0]+5
    bb = (x,y,self.GUI_Button_Size[0],self.GUI_Button_Size[1])
    name = 'Military'
    gui_cl = self.game.MakeClickable(name, bb, self.SwitchTabs, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, tab = True, enabled = True if self.active_tab == name else False, radioButton = True, radioGroup = 0)


  def GetWealthData(self):
    #results = self.game.db.execute('''SELECT IncrementTime, WealthAmount from FCT_WealthHistory WHERE GameID = %d and RaceID = %d;'''%(self.game.gameID, self.game.myRaceID)).fetchall()
    #if len (results) == 0:
    #  results = self.game.db.execute('''SELECT TimeUsed, Amount from FCT_WealthData WHERE GameID = %d and RaceID = %d;'''%(self.game.gameID, self.game.myRaceID)).fetchall()
    self.wealthHistory = []
    min_x = 10000000000000000000000000000
    min_y = 10000000000000000000000000000
    max_x = -10000000000000000000000000000
    max_y = -10000000000000000000000000000
    #for tuple in results:
    for timestamp in self.game.statisticsWealth:
      value = self.game.statisticsWealth[timestamp]
      ts = int(timestamp) + self.game.gameTimestampStart
      min_x = min([min_x, ts])
      min_y = min([min_y, value])
      max_x = max([max_x, ts])
      max_y = max([max_y, value])
      self.wealthHistory.append([ts, value])
    self.tabs['Economy'].AddData('Wealth', self.wealthHistory, ((min_x,min_y),(max_x,max_y)), axis = 1, unit = '€')


  def GetPopulationData(self):
    history = []
    min_x = 10000000000000000000000000000
    min_y = 10000000000000000000000000000
    max_x = -10000000000000000000000000000
    max_y = -10000000000000000000000000000
    unit = 'k'
    for timestamp in self.game.statisticsPopulation:
      value = self.game.statisticsPopulation[timestamp]*1000
      ts = int(timestamp) + self.game.gameTimestampStart
      min_x = min([min_x, ts])
      min_y = min([min_y, value])
      max_x = max([max_x, ts])
      max_y = max([max_y, value])
      history.append([ts, value])
    self.tabs['Economy'].AddData('Population', history, ((min_x,min_y),(max_x,max_y)), unit=unit)


  def GetStockpileData(self):
    for name in self.game.statisticsStockpile:
      unit = ''
      min_x = 10000000000000000000000000000
      min_y = 10000000000000000000000000000
      max_x = -10000000000000000000000000000
      max_y = -10000000000000000000000000000
      history = []
      unit = 't'
      if (name == 'Fuel'):
        unit = 'L'
      for timestamp in self.game.statisticsStockpile[name]:
        value = self.game.statisticsStockpile[name][timestamp]
        ts = int(timestamp) + self.game.gameTimestampStart
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
        unit = 'k'+unit
      self.tabs['Stockpiles'].AddData(name, history, ((min_x,min_y),(max_x,max_y)), unit=unit)


  def GetShipData(self):
    min_x = 10000000000000000000000000000
    min_y = 10000000000000000000000000000
    max_x = -10000000000000000000000000000
    max_y = -10000000000000000000000000000
    history = []
    for timestamp in self.game.statisticsShips:
      value = self.game.statisticsShips[timestamp]
      ts = int(timestamp) + self.game.gameTimestampStart
      min_x = min([min_x, ts])
      min_y = min([min_y, value])
      max_x = max([max_x, ts])
      max_y = max([max_y, value])
      history.append([ts, value])
    self.tabs['Military'].AddData('Ships', history, ((min_x,min_y),(max_x,max_y)))


  def GetStationData(self):
    min_x = 10000000000000000000000000000
    min_y = 10000000000000000000000000000
    max_x = -10000000000000000000000000000
    max_y = -10000000000000000000000000000
    history = []
    for timestamp in self.game.statisticsStations:
      value = self.game.statisticsStations[timestamp]
      ts = int(timestamp) + self.game.gameTimestampStart
      min_x = min([min_x, ts])
      min_y = min([min_y, value])
      max_x = max([max_x, ts])
      max_y = max([max_y, value])
      history.append([ts, value])
    self.tabs['Military'].AddData('Stations', history, ((min_x,min_y),(max_x,max_y)))


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      self.tabs[self.active_tab].Draw(self.surface)

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit


  def SwitchTabs(self, id, parent, mousepos):
    thisGroup = None
    thisElement = None
    if (id in self.GUI_Elements):
      thisElement = self.GUI_Elements[id]
      if (thisElement.radioButton):
        thisGroup = thisElement.radioGroup
        if (not thisElement.enabled):
          thisElement.enabled = True
          self.reDraw = True
          self.reDraw_GUI = True
          self.active_tab = thisElement.name
          for otherID in self.GUI_Elements:
            if (otherID != id):
              otherElement = self.GUI_Elements[otherID]
              if (otherElement.radioButton):
                if (otherElement.radioGroup == thisGroup):
                  otherElement.enabled = False