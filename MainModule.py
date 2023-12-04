import pygame
import sqlite3
import logger as lg
import Utils
import math
import random
import Clickable
import Screen
import GUI
import Bodies
import InfoWindow
import Fleets
import Colonies
import Systems
import SystemScreen
import BodiesScreen
import EconomyScreen
import json
from datetime import datetime
from time import mktime
import ColonyDetailsScreen
import ColoniesScreen
import SurveyScreen
import ResearchScreen
import TerraformingScreen
import GalaxyScreen
import XenosScreen
import EventsScreen
import Designations
import os

class Game():
  def __init__(self, eventsclass, images_file_list, size = (1800,1000), name = 'AuroraGUI'):
    self.Debug = False
    Bodies.SetGameInstance(self)
    Fleets.SetGameInstance(self)
    InfoWindow.SetGameInstance(self)
    
    self.Events = eventsclass
    self.logger = lg.Logger(logfile= 'logMain.txt', module='MainModule.py', log_level = 1)
    self.name = name
    self.width = size[0]
    self.height = size[1]
    pygame.display.set_caption(name)
    self.screen = pygame.display.set_mode((self.width,self.height))
    self.surface = pygame.Surface((self.width,self.height), pygame.SRCALPHA,32)
    self.surface.set_colorkey(Utils.GREENSCREEN)
    self.drawStationImages = True
    self.drawShipImages = False

    self.db = None
    self.gameID = -1
    self.myRaceID = -1
    self.gameTime = 0
    self.lastGameTime = 0
    self.deltaTime = 0
    self.homeSystemID = -1
    self.currentSystem = -1
    self.cameraCenter = (self.width/2,self.height/2)
    self.screenCenter = (self.width/2,self.height/2)
    self.systemScaleStart = 50
    self.systemScale = self.systemScaleStart
    self.mousePos = (0,0)
    #self.radius_Sun = 696000
    #self.minPixelSize_Star = 15
    #self.minPixelSize_Planet = 9
    #self.minPixelSize_Moon = 5
    #self.minPixelSize_Small = 5
    #self.mouseDragged = (0,0)
    self.screenCenterBeforeDrag = self.screenCenter
    self.counter_FPS = 0
    self.timestampLastSecond = pygame.time.get_ticks()
    self.timestampLast = pygame.time.get_ticks()
    self.FPS = 0
    self.reDraw = True
    self.reDraw_GUI = True
    self.clickables = []
    self.currentScreen = 'System'
    #self.currentScreen = 'Bodies'
    self.GUI_identifier = 'Global GUI'
    self.GUI_Elements = {}
    self.GUI_Top_Anchor = (300,10)
    self.GUI_Top_Button_Size = (130,30)
    self.lastScreen = None
    self.statisticsPopulation = {}
    self.statisticsStockpile = {}
    self.statisticsShips = {}
    self.statisticsGroundUnits = {}
    self.statisticsStations = {}
    self.statisticsWealth = {}
    self.options = {}

    ## Options
    self.bg_color = Utils.BLACK

    self.images_Body = {}

    self.highlighted_fleet_ID = -1
    self.highlighted_body_ID = -1

    self.images_GUI = {}
    self.systemBodies = {}
    self.assigned_body_images = {}

    #db_filename = 'D:\\Spiele\\Aurora4x\\AuroraDB - Copy.db'
    self.aurora_folder = 'D:\\Spiele\\Aurora4x\\'
    db_filename = self.aurora_folder+'AuroraDB.db'
    try:
      db_connection = sqlite3.connect(db_filename)
      self.db = db_connection.cursor()
    except Exception as e:
      print(e)
      self.logger.write('Error connecting to DB (%s): %s'%(db_filename, repr(e)))

    if (self.db):
      self.gameID, name, self.startYear = self.db.execute('''SELECT GameID, GameName, StartYear from FCT_Game''').fetchall()[-1]
      self.LoadGameLog()
      self.gameTimestampStart = mktime(datetime(year=self.startYear, month=1, day=1).timetuple())
      print(name,': ID', self.gameID)
      self.myRaceID = self.db.execute('''SELECT RaceID from FCT_Race WHERE GameID = %d AND NPR = 0;'''%(self.gameID)).fetchone()[0]
      self.myRaceStationPicFilename = self.db.execute('''SELECT SpaceStationPic from FCT_Race WHERE GameID = %d AND NPR = 0;'''%(self.gameID)).fetchone()[0]
      self.myRaceHullPicFilename = self.db.execute('''SELECT HullPic from FCT_Race WHERE GameID = %d AND NPR = 0;'''%(self.gameID)).fetchone()[0]
      self.myRaceFlagPicFilename = self.db.execute('''SELECT FlagPic from FCT_Race WHERE GameID = %d AND NPR = 0;'''%(self.gameID)).fetchone()[0]
      self.gameTime = self.db.execute('''SELECT GameTime from FCT_Game WHERE GameID = %d '''%(self.gameID)).fetchone()[0]
      self.gameTick = self.db.execute('''SELECT GameTime from FCT_Game WHERE GameID = %d '''%(self.gameID)).fetchone()[0]
      (self.deltaTime, self.gameTick) = self.db.execute('''SELECT Length, IncrementID from FCT_Increments WHERE GameID = %d ORDER BY GameTime Desc;'''%(self.gameID)).fetchall()[0]
      self.homeSystemID = Systems.GetHomeSystemID(self)
      self.GetMySpecies()
      self.currentSystem = self.homeSystemID
      #self.currentSystem = 8497 # Alpha Centauri , knownsystem 1, component2ID 87, c2orbit 23
      #self.currentSystem = 8499 # Lalande
      #self.currentSystem = 8500
      #self.currentSystem = 8496 # EE (with Black Hole)
      self.LoadStatistics()
      self.colonies = None
      self.stellarTypes = Bodies.GetStellarTypes(self)  
      self.gases = self.InitGases()
      Designations.Init(self)
      self.GetNewData()

    self.systemScreen       = SystemScreen.SystemScreen(self, eventsclass)
    self.bodiesScreen       = BodiesScreen.BodiesScreen(self, eventsclass)
    self.economyScreen      = EconomyScreen.EconomyScreen(self, eventsclass)
    self.colonyDetailsScreen= ColonyDetailsScreen.ColonyDetailsScreen(self, eventsclass)
    self.coloniesScreen     = ColoniesScreen.ColoniesScreen(self, eventsclass)
    self.surveyScreen       = SurveyScreen.SurveyScreen(self, eventsclass)
    self.researchScreen     = ResearchScreen.ResearchScreen(self, eventsclass)
    self.terraformingScreen = TerraformingScreen.TerraformingScreen(self, eventsclass)
    self.galaxyScreen       = GalaxyScreen.GalaxyScreen(self, eventsclass)
    self.xenosScreen        = XenosScreen.XenosScreen(self, eventsclass)
    self.eventsScreen       = EventsScreen.EventsScreen(self, eventsclass)

    self.playList = []
    self.currentSong = 0
    self.music = True
    self.LoadOptions()
    self.LoadMP3Playlist('D:\\MP3\\Musik\\Stellaris OST\\')
    self.LoadImages(images_file_list)
    self.InitGUI()
    


  def InitGUI(self):
    idGUI = 1
    x = self.GUI_Top_Anchor[0]
    y = self.GUI_Top_Anchor[1]
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'System'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Bodies'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Colonies'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Economy'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Research'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Galaxy'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Survey'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Terraforming'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Xenos'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Events'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+50
    bb = (x,y,self.GUI_Top_Button_Size[1],self.GUI_Top_Button_Size[1])
    name = 'Music'
    gui_cl = self.MakeClickable(name, bb, self.ToggleMusic, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.music)
    self.GUI_Elements[idGUI].SetImages(self.images_GUI, 'music_enabled', 'music_disabled')

    idGUI += 1
    x += self.GUI_Top_Button_Size[1]+5
    bb = (x,y,self.GUI_Top_Button_Size[1],self.GUI_Top_Button_Size[1])
    name = 'Skip'
    gui_cl = self.MakeClickable(name, bb, self.PlayNextSong, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = True, latching=False)
    self.GUI_Elements[idGUI].SetImages(self.images_GUI, 'music_skip')

    idGUI += 1
    x += self.GUI_Top_Button_Size[1]+5
    y -= 5
    bb = (x,y,20,20)
    name = '+'
    gui_cl = self.MakeClickable(name, bb, self.IncreaseVolume, double_click_call_back=self.IncreaseVolume, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = True, latching=False, tooltip = 'Increase Volume')
    self.GUI_Elements[idGUI].SetImages(self.images_GUI, 'vol_up_small')

    idGUI += 1
    y += 20+5
    bb = (x,y,20,20)
    name = '-'
    gui_cl = self.MakeClickable(name, bb, self.DecreaseVolume, double_click_call_back=self.DecreaseVolume, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = True, latching=False, tooltip = 'Decrease Volume')
    self.GUI_Elements[idGUI].SetImages(self.images_GUI, 'vol_down_small')

    # because the screen switching logic relies on the top menu bar we add a non-clickable hidden button here
    idGUI += 1
    bb = (0,0,0,0)
    name = 'Colony'
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, None, 'Button', textButton = True, enabled = True if self.currentScreen == name else False, radioButton = True, radioGroup = 0)

    #from pygame import mixer  # Load the popular external library


  def SwitchScreens(self, value, parent = None, mousepos = None):
    thisGroup = None
    thisElement = None

    if type(value) is int:
      id = value
    else:
      id = -1
      for check_id in self.GUI_Elements:
        if (self.GUI_Elements[check_id].name == value):
          id = check_id
          break
    if (id in self.GUI_Elements):
      thisElement = self.GUI_Elements[id]
      if (thisElement.radioButton):
        thisGroup = thisElement.radioGroup
        if (not thisElement.enabled):
          thisElement.enabled = True
          self.reDraw = True
          self.reDraw_GUI = True
          self.currentScreen = thisElement.name
          self.SetRedrawFlag(self.currentScreen)
          for otherID in self.GUI_Elements:
            if (otherID != id):
              otherElement = self.GUI_Elements[otherID]
              if (otherElement.radioButton):
                if (otherElement.radioGroup == thisGroup):
                  otherElement.enabled = False
          

  def LoadStatistics(self):
    filename = 'statistics_pop_game_%d.json'%self.gameID
    try:
      with open(filename, 'r') as f:
        self.statisticsPopulation = json.load(f)
    except:
      print('File %s not found'%filename)

    filename = 'statistics_wealth_game_%d.json'%self.gameID
    try:
      with open(filename, 'r') as f:
        self.statisticsWealth = json.load(f)
    except:
      print('File %s not found'%filename)

    filename = 'statistics_stockpile_game_%d.json'%self.gameID
    try:
      with open(filename, 'r') as f:
        self.statisticsStockpile = json.load(f)
    except:
      print('File %s not found'%filename)

    filename = 'statistics_ships_game_%d.json'%self.gameID
    try:
      with open(filename, 'r') as f:
        self.statisticsShips = json.load(f)
    except:
      print('File %s not found'%filename)

    filename = 'statistics_units_game_%d.json'%self.gameID
    try:
      with open(filename, 'r') as f:
        self.statisticsGroundUnits = json.load(f)
    except:
      print('File %s not found'%filename)

    filename = 'statistics_stations_game_%d.json'%self.gameID
    try:
      with open(filename, 'r') as f:
        self.statisticsStations = json.load(f)
    except:
      print('File %s not found'%filename)


  def SaveStatistics(self):
    filename = 'statistics_pop_game_%d.json'%self.gameID
    try:
      with open(filename, 'w') as f:
        json.dump(self.statisticsPopulation, f, indent=2)
    except:
      print('File %s not writeable'%filename)

    filename = 'statistics_wealth_game_%d.json'%self.gameID
    try:
      with open(filename, 'w') as f:
        json.dump(self.statisticsWealth, f, indent=2)
    except:
      print('File %s not writeable'%filename)

    filename = 'statistics_stockpile_game_%d.json'%self.gameID
    try:
      with open(filename, 'w') as f:
        json.dump(self.statisticsStockpile, f, indent=2)
    except:
      print('File %s not writeable'%filename)

    filename = 'statistics_ships_game_%d.json'%self.gameID
    try:
      with open(filename, 'w') as f:
        json.dump(self.statisticsShips, f, indent=2)
    except:
      print('File %s not writeable'%filename)

    filename = 'statistics_units_game_%d.json'%self.gameID
    try:
      with open(filename, 'w') as f:
        json.dump(self.statisticsGroundUnits, f, indent=2)
    except:
      print('File %s not writeable'%filename)

    filename = 'statistics_stations_game_%d.json'%self.gameID
    try:
      with open(filename, 'w') as f:
        json.dump(self.statisticsStations, f, indent=2)
    except:
      print('File %s not writeable'%filename)


  def LoadOptions(self):
    filename = 'options.json'
    try:
      with open(filename, 'r') as f:
        self.options = json.load(f)
    except:
      print('File %s not found'%filename)
    self.music = self.options['Audio']['Music']
    pygame.mixer.music.set_volume(self.options['Audio']['Volume'])

    self.systemScreen.show_Planets = self.options['SystemScreen']['show_Planets']
    self.systemScreen.show_Asteroids = self.options['SystemScreen']['show_Asteroids']
    self.systemScreen.show_Comets = self.options['SystemScreen']['show_Comets']                    
    self.systemScreen.show_DwarfPlanets = self.options['SystemScreen']['show_DwarfPlanets']              
    self.systemScreen.show_FleetTraces = self.options['SystemScreen']['show_FleetTraces']               
    self.systemScreen.show_Moons = self.options['SystemScreen']['show_Moons']                     
    self.systemScreen.showArtifactsBodies = self.options['SystemScreen']['showArtifactsBodies']            
    self.systemScreen.showColonizedBodies = self.options['SystemScreen']['showColonizedBodies']            
    self.systemScreen.showCommercialFleets = self.options['SystemScreen']['showCommercialFleets']           
    self.systemScreen.showEmptyFleets = self.options['SystemScreen']['showEmptyFleets']                
    self.systemScreen.showEnemyBodies = self.options['SystemScreen']['showEnemyBodies']                
    self.systemScreen.showIndustrializedBodies = self.options['SystemScreen']['showIndustrializedBodies']       
    self.systemScreen.showLabels_Asteroids = self.options['SystemScreen']['showLabels_Asteroids']           
    self.systemScreen.showLabels_Comets = self.options['SystemScreen']['showLabels_Comets']              
    self.systemScreen.showLabels_DwarfPlanets = self.options['SystemScreen']['showLabels_DwarfPlanets']        
    self.systemScreen.showLabels_Moons = self.options['SystemScreen']['showLabels_Moons']               
    self.systemScreen.showLabels_Planets = self.options['SystemScreen']['showLabels_Planets']             
    self.systemScreen.showLabels_Stars = self.options['SystemScreen']['showLabels_Stars']               
    self.systemScreen.showMilitaryFleets = self.options['SystemScreen']['showMilitaryFleets']             
    self.systemScreen.showOrbits_DwarfPlanets = self.options['SystemScreen']['showOrbits_DwarfPlanets']        
    self.systemScreen.showOrbits_Comets = self.options['SystemScreen']['showOrbits_Comets']              
    self.systemScreen.showOrbits_DwarfPlanets = self.options['SystemScreen']['showOrbits_DwarfPlanets']        
    self.systemScreen.showOrbits_Moons = self.options['SystemScreen']['showOrbits_Moons']               
    self.systemScreen.showOrbits_Planets = self.options['SystemScreen']['showOrbits_Planets']             
    self.systemScreen.showOrbits_Stars = self.options['SystemScreen']['showOrbits_Stars']               
    self.systemScreen.showStationaryFleets = self.options['SystemScreen']['showStationaryFleets']           
    self.systemScreen.showSurveyedLocations = self.options['SystemScreen']['showSurveyedLocations']          
    self.systemScreen.showUnsurveyedBodies = self.options['SystemScreen']['showUnsurveyedBodies']           
    self.systemScreen.showUnsurveyedLocations = self.options['SystemScreen']['showUnsurveyedLocations']        
    self.systemScreen.showXenosBodies = self.options['SystemScreen']['showXenosBodies']                
    self.systemScreen.highlightColonizedBodies =  self.options['SystemScreen']['highlightColonizedBodies']       
    self.systemScreen.highlightIndustrializedBodies = self.options['SystemScreen']['highlightIndustrializedBodies']
    self.systemScreen.highlightUnsurveyedBodies = self.options['SystemScreen']['highlightUnsurveyedBodies']      
    self.systemScreen.highlightEnemyBodies = self.options['SystemScreen']['highlightEnemyBodies']           
    self.systemScreen.highlightResourcefulBodies =  self.options['SystemScreen']['highlightResourcefulBodies']     
    self.systemScreen.highlightXenosBodies =  self.options['SystemScreen']['highlightXenosBodies']           
    self.systemScreen.highlightArtifactsBodies = self.options['SystemScreen']['highlightArtifactsBodies']       


  def SaveOptions(self):
    self.options['Audio'] = {'Music':self.music, 'Volume':pygame.mixer.music.get_volume()}
    self.options['SystemScreen'] = {'show_Planets':self.systemScreen.show_Planets,
                                    'show_Asteroids':self.systemScreen.show_Asteroids,
                                    'show_Comets':self.systemScreen.show_Comets,
                                    'show_DwarfPlanets':self.systemScreen.show_DwarfPlanets,
                                    'show_FleetTraces':self.systemScreen.show_FleetTraces,
                                    'show_Moons':self.systemScreen.show_Moons,
                                    'showArtifactsBodies':self.systemScreen.showArtifactsBodies,
                                    'showColonizedBodies':self.systemScreen.showColonizedBodies,
                                    'showCommercialFleets':self.systemScreen.showCommercialFleets,
                                    'showEmptyFleets':self.systemScreen.showEmptyFleets,
                                    'showEnemyBodies':self.systemScreen.showEnemyBodies,
                                    'showIndustrializedBodies':self.systemScreen.showIndustrializedBodies,
                                    'showLabels_Asteroids':self.systemScreen.showLabels_Asteroids,
                                    'showLabels_Comets':self.systemScreen.showLabels_Comets,
                                    'showLabels_DwarfPlanets':self.systemScreen.showLabels_DwarfPlanets,
                                    'showLabels_Moons':self.systemScreen.showLabels_Moons,
                                    'showLabels_Planets':self.systemScreen.showLabels_Planets,
                                    'showLabels_Stars':self.systemScreen.showLabels_Stars,
                                    'showMilitaryFleets':self.systemScreen.showMilitaryFleets,
                                    'showOrbits_DwarfPlanets':self.systemScreen.showOrbits_DwarfPlanets,
                                    'showOrbits_Comets':self.systemScreen.showOrbits_Comets,
                                    'showOrbits_DwarfPlanets':self.systemScreen.showOrbits_DwarfPlanets,
                                    'showOrbits_Moons':self.systemScreen.showOrbits_Moons,
                                    'showOrbits_Planets':self.systemScreen.showOrbits_Planets,
                                    'showOrbits_Stars':self.systemScreen.showOrbits_Stars,
                                    'showStationaryFleets':self.systemScreen.showStationaryFleets,
                                    'showSurveyedLocations':self.systemScreen.showSurveyedLocations,
                                    'showUnsurveyedBodies':self.systemScreen.showUnsurveyedBodies,
                                    'showUnsurveyedLocations':self.systemScreen.showUnsurveyedLocations,
                                    'showXenosBodies':self.systemScreen.showXenosBodies,
                                    'highlightColonizedBodies':self.systemScreen.highlightColonizedBodies,
                                    'highlightIndustrializedBodies':self.systemScreen.highlightIndustrializedBodies,
                                    'highlightUnsurveyedBodies':self.systemScreen.highlightUnsurveyedBodies,
                                    'highlightEnemyBodies':self.systemScreen.highlightEnemyBodies,
                                    'highlightResourcefulBodies':self.systemScreen.highlightResourcefulBodies,
                                    'highlightXenosBodies':self.systemScreen.highlightXenosBodies,
                                    'highlightArtifactsBodies':self.systemScreen.highlightArtifactsBodies
                                    }
    filename = 'options.json'
    try:
      with open(filename, 'w') as f:
        json.dump(self.options, f, indent=2)
    except:
      print('File %s not writeable'%filename)
  

  def InitGases(self):
    gases = {}
    results = self.db.execute('''SELECT GasID, Name, Dangerous, DangerousLevel from DIM_Gases;''').fetchall()
    for result in results:
      gases[result[0]] = {'Name':result[1], 'DangerFactor':result[2], 'DangerousLevel':result[3]/1000}
    return gases


  def Draw(self):
    reblit = False
    self.reDraw_GUI |= self.DrawCurrentScreen()
    
    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    pygame.display.update()
    self.counter_FPS += 1

    currentTimestamp = pygame.time.get_ticks()
    deltaTime = currentTimestamp - self.timestampLastSecond
    if (deltaTime >= 1000):
      #self.FPS = 1000*self.counter_FPS / deltaTime
      self.FPS = self.counter_FPS 
      self.counter_FPS = 0
      self.timestampLastSecond = currentTimestamp
    Utils.DrawText2Screen(self.screen,'%d FPS'%(self.FPS),(5,5),18,Utils.WHITE, False)
    Utils.DrawText2Screen(self.screen,'Scale: %3.2f'%(self.systemScreen.systemScale),(5,25),18,Utils.WHITE, False)

    return


  def DrawGUI(self):
    if (self.reDraw_GUI):
      for GUI_ID in self.GUI_Elements:
        element = self.GUI_Elements[GUI_ID]
        if (element.visible):
          element.Draw(self.surface)
      for GUI_ID in self.GUI_Elements:
        element = self.GUI_Elements[GUI_ID]
        if (element.visible):
          element.DrawTooltip(self.surface)
      self.reDraw_GUI = False
      return True
    else:
      return False


  def DrawCurrentScreen(self):
    reblit = False
    if (self.lastScreen != self.currentScreen):
      self.Events.ClearClickables()
      if (self.lastScreen == 'Bodies'):
        self.bodiesScreen.ExitScreen()
    if (self.currentScreen == 'System'):
      if (self.lastScreen != self.currentScreen):
        self.systemScreen.InitGUI()
      reblit |= self.systemScreen.Draw()
    elif (self.currentScreen == 'Bodies'):
      if (self.lastScreen != self.currentScreen):
        self.bodiesScreen.ResetGUI()
      reblit |= self.bodiesScreen.Draw()
    elif (self.currentScreen == 'Economy'):
      if (self.lastScreen != self.currentScreen):
        self.economyScreen.ResetGUI()
        self.economyScreen.UpdateEconomyData()
      reblit |= self.economyScreen.Draw()
    elif (self.currentScreen == 'Colonies'):
      if (self.lastScreen != self.currentScreen):
        self.coloniesScreen.ResetGUI()
        #self.coloniesScreen.UpdateData()
      reblit |= self.coloniesScreen.Draw()
    elif (self.currentScreen == 'Colony'):
      if (self.lastScreen != self.currentScreen):
        self.colonyDetailsScreen.ResetGUI()
        #self.colonyDetailsScreen.UpdateData()
      reblit |= self.colonyDetailsScreen.Draw()
    elif (self.currentScreen == 'Xenos'):
      if (self.lastScreen != self.currentScreen):
        self.xenosScreen.ResetGUI()
        #self.xenosScreen.UpdateData()
      reblit |= self.xenosScreen.Draw()
    elif (self.currentScreen == 'Survey'):
      if (self.lastScreen != self.currentScreen):
        self.surveyScreen.ResetGUI()
        #self.surveyScreen.UpdateData()
      reblit |= self.surveyScreen.Draw()
    elif (self.currentScreen == 'Research'):
      if (self.lastScreen != self.currentScreen):
        self.researchScreen.ResetGUI()
        #self.researchScreen.UpdateData()
      reblit |= self.researchScreen.Draw()
    elif (self.currentScreen == 'Galaxy'):
      if (self.lastScreen != self.currentScreen):
        self.galaxyScreen.ResetGUI()
        #self.galaxyScreen.UpdateData()
      reblit |= self.galaxyScreen.Draw()
    elif (self.currentScreen == 'Terraforming'):
      if (self.lastScreen != self.currentScreen):
        self.terraformingScreen.ResetGUI()
        #self.terraformingScreen.UpdateData()
      reblit |= self.terraformingScreen.Draw()
    elif (self.currentScreen == 'Events'):
      if (self.lastScreen != self.currentScreen):
        self.eventsScreen.ResetGUI()
        #self.terraformingScreen.UpdateData()
      reblit |= self.eventsScreen.Draw()
    else:
      self.surface.fill(self.bg_color)
      reblit = True
      print('Draw screen %s'%self.currentScreen)
    self.lastScreen = self.currentScreen
    return reblit


  def SetRedrawFlag(self, screen_name):
    if (screen_name == 'System'):
      self.systemScreen.reDraw = True
    elif (screen_name == 'Bodies'):
      self.bodiesScreen.reDraw = True
    elif (screen_name == 'Economy'):
      self.economyScreen.reDraw = True
    elif (screen_name == 'Survey'):
      self.surveyScreen.reDraw = True
    elif (screen_name == 'Colony'):
      self.colonyDetailsScreen.reDraw = True
    elif (screen_name == 'Colonies'):
      self.coloniesScreen.reDraw = True
    elif (screen_name == 'Xenos'):
      self.xenosScreen.reDraw = True
    elif (screen_name == 'Research'):
      self.researchScreen.reDraw = True
    elif (screen_name == 'Terraforming'):
      self.terraformingScreen.reDraw = True
    elif (screen_name == 'Galaxy'):
      self.galaxyScreen.reDraw = True
    elif (screen_name == 'Events'):
      self.eventsScreen.reDraw = True


  def CheckForNewDBData(self):
    gameTime = self.db.execute('''SELECT GameTime from FCT_Game WHERE GameID = %d '''%(self.gameID)).fetchone()[0]
    if (gameTime != self.gameTime):
      self.lastGameTime = self.gameTime
      self.GetNewData()
      self.SetRedrawFlag(self.currentScreen)
      date_time = datetime.fromtimestamp(self.gameTime)
      print('New game data! %s'%date_time.strftime("%b %d %Y"))
      self.SaveGameLog()


  def GetNewData(self):
    self.gameTime = self.db.execute('''SELECT GameTime from FCT_Game WHERE GameID = %d '''%(self.gameID)).fetchone()[0]
    self.deltaTime = self.db.execute('''SELECT Length from FCT_Increments WHERE GameID = %d ORDER BY GameTime Desc;'''%(self.gameID)).fetchone()[0]
    self.starSystems = Systems.GetSystems(self)
    self.cc_cost_reduction = Colonies.GetCCreduction(self)
    self.fleets = Fleets.GetFleets(self)
    self.installations = Colonies.GetInstallationInfo(self)
    self.colonies = Colonies.GetColonies(self)
    self.GetWealthData()
    self.SaveStatistics()
    self.GetNewLocalData(self.currentSystem)


  def GetNewLocalData(self, currentSystem):
    self.surveyLocations = Systems.GetSurveyLocations(self, currentSystem)
    self.systemBodies = Bodies.GetSystemBodies(self, currentSystem)
    self.currentSystemJumpPoints = Systems.GetSystemJumpPoints(self, currentSystem)


  def LoadImages(self, list_of_image_files):
    for sub_folder, name, filename in list_of_image_files:
      if (sub_folder == 'Sol'):
        if (not sub_folder in self.images_Body):
          self.images_Body[sub_folder] = {}
        file_lower = name.lower()
        if (file_lower.endswith('.jpg')):
          hyphen = file_lower.find('-')
          if (hyphen > -1):
            body_name = file_lower[:hyphen].strip()
            self.images_Body[sub_folder][body_name] = pygame.image.load(filename)
            self.images_Body[sub_folder][body_name].set_colorkey(self.bg_color)
      elif (sub_folder == 'Planets'):
        #if (not sub_folder in self.images_Body):
        #  self.images_Body[sub_folder] = {}
        file_lower = name.lower()
        if (file_lower.endswith('.jpg')):
          planets_subcat = sub_folder+'_'+file_lower[0]
          if (not planets_subcat in self.images_Body):
            self.images_Body[planets_subcat] = []
          hyphen = file_lower.find('.')
          if (hyphen > -1):
            #body_name = file_lower[:hyphen].strip()
            self.images_Body[planets_subcat].append(pygame.image.load(filename))
            self.images_Body[planets_subcat][-1].set_colorkey(self.bg_color)
      elif (sub_folder == 'Stars'):
        if (not sub_folder in self.images_Body):
          self.images_Body[sub_folder] = {}
        file_lower = name.lower()
        if (file_lower.endswith('.jpg')):
          hyphen = file_lower.find('.')
          if (hyphen > -1):
            body_name = file_lower[:hyphen].strip().upper()
            self.images_Body[sub_folder][body_name] = pygame.image.load(filename)
            self.images_Body[sub_folder][body_name].set_colorkey(self.bg_color)
      elif (sub_folder == 'GUI'):
        file_lower = name.lower()
        if (file_lower.endswith('.png')):
          hyphen = file_lower.find('.')
          if (hyphen > -1):
            name = file_lower[:hyphen].strip().lower()
            self.images_GUI[name] = pygame.image.load(filename)
            self.images_GUI[name].set_colorkey(Utils.GREENSCREEN)
      elif (sub_folder == 'HiRes'):
        pass
      else:
        if (not sub_folder in self.images_Body):
          self.images_Body[sub_folder] = []
        file_lower = name.lower()
        if (file_lower.endswith('.jpg')):
          hyphen = file_lower.find('.')
          if (hyphen > -1):
            #body_name = file_lower[:hyphen].strip()
            self.images_Body[sub_folder].append(pygame.image.load(filename))
            self.images_Body[sub_folder][-1].set_colorkey(self.bg_color)
    
    self.LoadBodyImages()
    
    self.systemBodies = Bodies.GetSystemBodies(self, self.currentSystem)
    self.starSystems = Systems.GetSystems(self)

    if (self.myRacePicFilename):
      self.myRacePic = pygame.image.load(self.aurora_folder+'Races\\'+self.myRacePicFilename)
    if (self.myRaceStationPicFilename):
      self.myRaceStationPic = pygame.image.load(self.aurora_folder+'StationIcons\\'+self.myRaceStationPicFilename)
    if (self.myRaceHullPicFilename):
      self.myRaceHullPic = pygame.image.load(self.aurora_folder+'ShipIcons\\'+self.myRaceHullPicFilename)
    if (self.myRaceFlagPicFilename):
      self.myRaceFlagPic = pygame.image.load(self.aurora_folder+'Flags\\'+self.myRaceFlagPicFilename)


  def MakeClickable(self, name, bounding_box, left_click_call_back=None, right_click_call_back=None, double_click_call_back=None, par=None, color=None, parent = None, anchor = None, enabled = True, persistent = False):
    if (len(bounding_box) == 2):
      if (len(bounding_box[0]) == 2 and len(bounding_box[1]) == 2):
        bounding_box = (bounding_box[0][0],bounding_box[0][1],bounding_box[1][0],bounding_box[1][1])

    if (anchor is not None):
      bounding_box = (bounding_box[0]+anchor[0],bounding_box[1]+anchor[1],bounding_box[2],bounding_box[3])

    if (Utils.IsOnScreen(self.surface, bounding_box)):
      cl = Clickable.Clickable(self, name, bounding_box, parameter=par, 
                     LeftClickCallBack=left_click_call_back, 
                     RightClickCallBack=right_click_call_back, 
                     DoubleClickCallBack=double_click_call_back,
                     parent = parent,
                     enabled = enabled,
                     persistent = persistent)
      if (self.Events):
        self.Events.Bind(cl)
      return cl
    else:
      return None


  def CheckClickableNotBehindGUI(self, bb):
    rect = pygame.Rect(bb)
    if (     (self.systemScreen.window_info_rect.colliderect(rect)) 
         or ( self.systemScreen.window_map_rect.colliderect(rect) ) ):
      return False
    else:
      return True


  def DebugDrawClickables(self):
    if (self.Debug):
      if (self.Events):
        for clickable in self.Events.clickables:
          if (clickable.enabled):
            pygame.draw.rect(self.surface, Utils.RED, clickable.rect, 1)

  
  def GetMySpecies(self):
    self.myRaceSpecies = self.db.execute('''SELECT SpeciesID from FCT_Species WHERE GameID = %d AND SpecialNPRID = 0;'''%(self.gameID)).fetchone()[0]
    self.myRacePicFilename = self.db.execute('''SELECT RacePic from FCT_Species WHERE GameID = %d AND SpecialNPRID = 0;'''%(self.gameID)).fetchone()[0]


  def FollowEvent(self, parameters, parent, mousepos):
    # parents: ['Ship', 'Body', 'Fleet','Missile', 'Contact','Research', 'Xenos', 'System']
    [name, SystemID, Xcor, Ycor, IDType, ID] = parameters

    if (parent == 'Body'):
      if (SystemID != 0):
        self.currentSystem = SystemID
        self.GetNewLocalData(SystemID)
        #if (Xcor == Ycor):
        #  body = Bodies.GetBodyFromName(self, name)
        #  if (body):
        #    (Xcor,Ycor) = body['Pos']
        #self.systemScreen.ZoomTo((Xcor, Ycor), 409600)
        #self.SwitchScreens('System')
        self.colonyDetailsScreen.bodyID = ID
        self.colonyDetailsScreen.systemID = SystemID
        self.SwitchScreens('Colony')
    elif (parent == 'Fleet'):
      if (SystemID != 0):
        self.currentSystem = SystemID
        self.GetNewLocalData(SystemID)
        self.systemScreen.ZoomTo((Xcor, Ycor), 409600)
        self.SwitchScreens('System')
    elif (parent == 'Ship'):
      if (SystemID != 0):
        self.currentSystem = SystemID
        self.GetNewLocalData(SystemID)
        self.systemScreen.ZoomTo((Xcor, Ycor), 409600)
        self.SwitchScreens('System')
    elif (parent == 'Research'):
      self.SwitchScreens(parent)
    elif (parent == 'System'):
      if (SystemID != 0):
        self.currentSystem = SystemID
        self.GetNewLocalData(SystemID)
        self.systemScreen.ZoomTo((0, 0), 50)
        self.SwitchScreens('System')
    elif (parent == 'Xenos'):
      self.SwitchScreens(parent)
    elif (parent == 'Contact'):
      if (SystemID != 0):
        self.currentSystem = SystemID
        self.GetNewLocalData(SystemID)
        self.systemScreen.ZoomTo((Xcor, Ycor), 409600)
        self.SwitchScreens('System')
    elif (parent == 'Missile'):
      pass


  def LoadMP3Playlist(self, folder):
    pygame.mixer.init()
    for root, dirs, files in os.walk(folder, topdown=False):
      for name in files:
        if (name.endswith('.mp3')):
          self.playList.append(os.path.join(root, name))
    self.currentSong = random.randint(0,len(self.playList)-1)
    if (self.music):
      self.PlayNextSong(None, None, None)


  def ToggleMusic(self, parameters, parent, mousepos):
    self.music = not self.music
    self.GUI_Elements[parameters].enabled = self.music
    if (self.music):
      pygame.mixer.music.unpause()
    else:
      pygame.mixer.music.pause()


  def PlayNextSong(self, parameters, parent, mousepos):
    self.currentSong += 1
    if (self.currentSong >= len(self.playList)):
      self.currentSong = 0
    pygame.mixer.music.stop()
    pygame.mixer.music.load(self.playList[self.currentSong])
    pygame.mixer.music.play()


  def MusicTick(self):
    if (self.music):
      if (not pygame.mixer.music.get_busy()):
        self.PlayNextSong(None, None, None)


  def IncreaseVolume(self, parameters, parent, mousepos):
    pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()+0.1)
    print(pygame.mixer.music.get_volume())


  def DecreaseVolume(self, parameters, parent, mousepos):
    pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()-0.1)
    print(pygame.mixer.music.get_volume())


  def GetWealthData(self):
    results = self.db.execute('''SELECT IncrementTime, WealthAmount from FCT_WealthHistory WHERE GameID = %d and RaceID = %d ORDER BY IncrementTime Asc;'''%(self.gameID, self.myRaceID)).fetchall()
    #unsorted = []
    for tuple in results:
      #unsorted.append([int(tuple[0]), tuple[1]])
      value = tuple[1]
      ts = int(tuple[0])
      self.statisticsWealth[str(ts)] = value


  def LoadBodyImages(self):
    filename = 'body_images_game_%d.json'%self.gameID
    try:
      with open(filename, 'r') as f:
        self.assigned_body_images = json.load(f)
    except:
      print('File %s not found'%filename)


  def SaveBodyImages(self):
    filename = 'body_images_game_%d.json'%self.gameID
    try:
      with open(filename, 'w') as f:
        json.dump(self.assigned_body_images, f, indent=2)
    except Exception as e:
      print('File %s not found'%filename)
      print (e)


  def SaveGameLog(self):
    filename = 'log_game_%d.json'%self.gameID
    try:
      with open(filename, 'w') as f:
        json.dump({'lastGameTime':self.lastGameTime}, f, indent=2)
    except Exception as e:
      print('File %s not found'%filename)
      print (e)


  def LoadGameLog(self):
    filename = 'log_game_%d.json'%self.gameID
    try:
      with open(filename, 'r') as f:
        game_log = json.load(f)
        self.lastGameTime = game_log['lastGameTime']
    except Exception as e:
      print('File %s not found'%filename)
      print (e)