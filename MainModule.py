import pygame
import sqlite3
import logger as lg
import Utils
import math
import random
import Clickable
import GUI
import Bodies
import InfoWindow
import Fleets
import Colonies
import Systems


class Game():
  def __init__(self, eventsclass, size = (1800,1000), name = 'AuroraGUI'):
    Bodies.SetGameInstance(self)
    Fleets.SetGameInstance(self)
    self.Events = eventsclass
    self.logger = lg.Logger(logfile= 'logMain.txt', module='MainModule.py', log_level = 1)
    self.name = name
    self.width = size[0]
    self.height = size[1]
    pygame.display.set_caption(name)
    self.screen = pygame.display.set_mode((self.width,self.height))
    self.surface = pygame.Surface((self.width,self.height), pygame.SRCALPHA,32)
    self.surface.set_colorkey(Utils.GREENSCREEN)
    self.Debug = False

    self.db = None
    self.gameID = -1
    self.myRaceID = -1
    self.gameTime = 0
    self.deltaTime = 0
    self.homeSystemID = -1
    self.currentSystem = -1
    self.cameraCenter = (self.width/2,self.height/2)
    self.screenCenter = (self.width/2,self.height/2)
    self.systemScaleStart = 50
    self.systemScale = self.systemScaleStart
    self.mousePos = (0,0)
    self.radius_Sun = 696000
    self.minPixelSize_Star = 15
    self.minPixelSize_Planet = 9
    self.minPixelSize_Moon = 5
    self.minPixelSize_Small = 5
    self.mouseDragged = (0,0)
    self.refreshData = True
    self.screenCenterBeforeDrag = self.screenCenter
    self.counter_FPS = 0
    self.timestampLastSecond = pygame.time.get_ticks()
    self.timestampLast = pygame.time.get_ticks()
    self.FPS = 0
    self.reDraw = True
    self.reDraw_GUI = True
    self.clickables = []

    # Options
    self.bg_color = Utils.BLACK
    self.showEmptyFleets = False
    self.showStationaryFleets = False
    self.showUnsurveyedLocations = True
    self.showSurveyedLocations = False
    self.show_FleetTraces = True
    self.show_Planets = True
    self.show_Moons = True
    self.show_DwarfPlanets = True
    self.show_Comets = True
    self.show_Asteroids = False

    self.showColonizedBodies = True
    self.showIndustrializedBodies = True
    self.showUnsurveyedBodies = True
    self.showEnemyBodies = True
    self.showResourcefulBodies = True
    self.showXenosBodies = True
    self.showArtifactsBodies = True

    self.showOrbits_Planets = True
    self.showOrbits_DwarfPlanets = True
    self.showOrbits_Moons = True
    self.showOrbits_Comets = False
    self.showOrbits_Asteroids = False
    self.showOrbits_Stars = True

    self.showLabels_Planets = True
    self.showLabels_DwarfPlanets = True
    self.showLabels_Moons = True
    self.showLabels_Comets = True
    self.showLabels_Asteroids = False
    self.showLabels_Stars = True
    self.minDist4Labels = 100
    
    # Colorscheme
    self.color_JP = Utils.ORANGE
    self.color_Jumpgate = Utils.ORANGE
    self.color_SurveyedLoc = Utils.TEAL
    self.color_UnsurveyedLoc = Utils.BLUE
    self.color_Fleet = Utils.GREEN

    # bodies
    self.color_Star = Utils.YELLOW
    self.color_Planet = Utils.MED_GREEN
    self.color_DwarfPlanet = Utils.MED_GREEN
    self.color_Moon = Utils.GREEN
    self.color_Asteroid = Utils.GRAY
    self.color_Comet = Utils.BLUE

    # body labels
    self.color_Label_Star = Utils.WHITE
    self.color_Label_Planet = Utils.WHITE
    self.color_Label_DwarfPlanet = Utils.WHITE
    self.color_Label_Moon = Utils.WHITE
    self.color_Label_Asteroid = Utils.WHITE
    self.color_Label_Comet = Utils.WHITE

    # body orbits
    self.color_Orbit_Star = Utils.YELLOW
    self.color_Orbit_Planet = Utils.DARK_GRAY
    self.color_Orbit_DwarfPlanet = Utils.DARK_GRAY
    self.color_Orbit_Moon = Utils.DARK_GRAY
    self.color_Orbit_Asteroid = Utils.SUPER_DARK_GRAY
    self.color_Orbit_Comet = Utils.SUPER_DARK_GRAY
    self.images_Body = {}

    self.window_fleet_info_identifier = 'Fleet Info Window'
    self.window_fleet_info_size = (300,600)
    self.window_map_size = (self.window_fleet_info_size[0],self.window_fleet_info_size[0])

    self.window_fleet_info_anchor = (5,self.height-self.window_map_size[1]-self.window_fleet_info_size[1]-2*5)#(self.width-self.window_fleet_info_size[0]-5,self.height-self.window_map_size[1]-self.window_fleet_info_size[1]-2*5)
    self.window_fleet_info = pygame.Surface(self.window_fleet_info_size, pygame.SRCALPHA,32)
    self.window_fleet_info_rect = pygame.Rect(self.window_fleet_info_anchor, self.window_fleet_info_size)
    self.window_fleet_info.set_colorkey(Utils.GREENSCREEN)
    self.reDraw_FleetInfoWindow = True;
    self.window_fleet_info_scoll_pos = 0
    self.highlighted_fleet_ID = -1
    self.highlighted_body_ID = -1


    self.window_info_identifier = 'Info Window'
    self.window_info_size = (300,600)
    self.window_info_anchor = (self.width-self.window_info_size[0]-5,self.height-self.window_fleet_info_size[1]-5)#(self.width-self.window_fleet_info_size[0]-5,self.height-self.window_map_size[1]-self.window_fleet_info_size[1]-2*5)
    self.window_info = pygame.Surface(self.window_info_size, pygame.SRCALPHA,32)
    self.window_info_rect = pygame.Rect(self.window_info_anchor, self.window_info_size)
    self.window_info.set_colorkey(Utils.GREENSCREEN)
    self.reDraw_InfoWindow = True;
    self.window_info_scoll_pos = 0
    self.info_category_physical = 'Physical Info'
    self.info_cat_phys_expanded = True
    self.info_category_economical = 'Economical Info'
    self.info_cat_eco_expanded = False
    self.info_category_orbit = 'Orbit Info'
    self.info_cat_orbit_expanded = False
    self.info_category_stockpile = 'Stockpile'
    self.info_cat_stock_expanded = True
    self.info_category_installations = 'Installations'
    self.info_cat_inst_expanded = True
    self.info_category_deposits = 'Mineral Deposits'
    self.info_cat_deposits_expanded = True

    self.window_map_anchor = (5,self.height-self.window_map_size[1]-5)#(self.width-self.window_map_size[0]-5,self.height-self.window_map_size[1]-5)
    self.window_map = pygame.Surface(self.window_map_size, pygame.SRCALPHA,32)
    self.window_map_rect = pygame.Rect(self.window_map_anchor, self.window_map_size)
    self.window_map.set_colorkey(Utils.GREENSCREEN)
    self.reDraw_MapWindow = True;

    self.GUI_identifier = 'GUI Elements'
    self.GUI_Elements = {}
    self.GUI_Bottom_Anchor = (500,self.height-50)
    self.images_GUI = {}
    self.GUI_expanded_fleets = []
    self.GUI_expanded_fleets2 = []
    self.InitGUI()
    self.systemBodies = {}

    db_filename = 'D:\\Spiele\\Aurora4x\\AuroraDB - Copy.db'
    try:
        db_connection = sqlite3.connect(db_filename)
        self.db = db_connection.cursor()
    except Exception as e:
        print(e)
        self.logger.write('Error connecting to DB (%s): %s'%(db_filename, repr(e)))

    if (self.db):
      game_table = self.db.execute('''SELECT * from FCT_Game''').fetchall()[-1]
      print(game_table[5],': ID', game_table[0])
      self.gameID = game_table[0]
      self.myRaceID = self.db.execute('''SELECT RaceID from FCT_Race WHERE GameID = %d AND NPR = 0;'''%(self.gameID)).fetchone()[0]
      self.gameTime = self.db.execute('''SELECT GameTime from FCT_Game WHERE GameID = %d '''%(self.gameID)).fetchone()[0]
      self.deltaTime = self.db.execute('''SELECT Length from FCT_Increments WHERE GameID = %d ORDER BY GameTime Desc;'''%(self.gameID)).fetchone()[0]
      self.homeSystemID = Systems.GetHomeSystemID(self)
      self.currentSystem = self.homeSystemID
      #self.currentSystem = 8497 # Alpha Centauri , knownsystem 1, component2ID 87, c2orbit 23
      #self.currentSystem = 8499 # Lalande
      #self.currentSystem = 8500
      #self.currentSystem = 8496 # EE (with Black Hole)
      self.stellarTypes = Bodies.GetStellarTypes(self)
      self.gases = self.InitGases()
      self.installations = Colonies.GetInstallationInfo(self)
      self.cc_cost_reduction = Colonies.GetCCreduction(self)

      self.colonies = None
      self.GetNewData()
      

  def InitGUI(self):
    idGUI = 1
    x = self.GUI_Bottom_Anchor[0]
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Show Bodies'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl)
    showBodiesGUI = self.GUI_Elements[idGUI]

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Planets'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showBodiesGUI.GetID(), enabled = self.show_Planets)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Moons'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showBodiesGUI.GetID(), enabled = self.show_Moons)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Asteroids'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, parent=showBodiesGUI.GetID(), enabled = self.show_Asteroids)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Comets'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showBodiesGUI.GetID(), enabled = self.show_Comets)
    showBodiesGUI.AddChildren(idGUI)

    # Second Column
    idGUI += 1
    x += size+5
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Show Orbits'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl)
    showOrbitsGUI = self.GUI_Elements[idGUI]

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Planet Orbits'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showOrbitsGUI.GetID(), enabled = self.showOrbits_Planets)
    showOrbitsGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Moon Orbits'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showOrbitsGUI.GetID(), enabled = self.showOrbits_Moons)
    showOrbitsGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Asteroid Orbits'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, parent=showOrbitsGUI.GetID(), enabled = self.showOrbits_Asteroids)
    showOrbitsGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Comet Orbits'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showOrbitsGUI.GetID(), enabled = self.showOrbits_Comets)
    showOrbitsGUI.AddChildren(idGUI)

    # Third Column
    idGUI += 1
    x += size+5
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Filter'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl)
    FilterBodiesGUI = self.GUI_Elements[idGUI]

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Colonies'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=FilterBodiesGUI.GetID(), enabled = self.showColonizedBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Resources'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=FilterBodiesGUI.GetID(), enabled = self.showResourcefulBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Installations'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=FilterBodiesGUI.GetID(), enabled = self.showIndustrializedBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Unsurveyed'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, parent=FilterBodiesGUI.GetID(), enabled = self.showUnsurveyedBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Enemies'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=FilterBodiesGUI.GetID(), enabled = self.showEnemyBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Xenos'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=FilterBodiesGUI.GetID(), enabled = self.showXenosBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Artifacts'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=FilterBodiesGUI.GetID(), enabled = self.showArtifactsBodies)
    FilterBodiesGUI.AddChildren(idGUI)


  def InitGases(self):
    gases = {}
    results = self.db.execute('''SELECT GasID, Name, Dangerous, DangerousLevel from DIM_Gases;''').fetchall()
    for result in results:
      gases[result[0]] = {'Name':result[1], 'DangerFactor':result[2], 'DangerousLevel':result[3]/1000}
    return gases


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      if (self.Events):
        self.Events.ClearClickables(exclude=self.GUI_identifier)
      self.reDraw_FleetInfoWindow = True
      self.reDraw_InfoWindow = True
      self.reDraw_MapWindow = True
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)

      reblit |= self.DrawSystem()

    reblit |= self.DrawMiniMap()

    reblit |= Fleets.DrawFleetInfoWindow(self)

    reblit |= InfoWindow.Draw(self)

    reblit |= self.DrawGUI()

    if (reblit):
      self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.counter_FPS += 1

    currentTimestamp = pygame.time.get_ticks()
    deltaTime = currentTimestamp - self.timestampLastSecond
    if (deltaTime >= 1000):
      #self.FPS = 1000*self.counter_FPS / deltaTime
      self.FPS = self.counter_FPS 
      self.counter_FPS = 0
      self.timestampLastSecond = currentTimestamp
    Utils.DrawText2Screen(self.screen,'%d FPS'%(self.FPS),(5,50),18,Utils.WHITE, False)
    # draw mouse position and scale
    Utils.DrawText2Screen(self.screen,'(%d,%d) Scale: %3.1f'%(self.mousePos[0], self.mousePos[1], self.systemScale),(5,5),18,Utils.WHITE, False)
    Utils.DrawText2Screen(self.screen,'(%d,%d)'%(self.mouseDragged[0], self.mouseDragged[1]),(5,25),18,Utils.WHITE, False)

    pygame.display.update()
    self.reDraw = False
    
    return


  def DrawSystem(self):
    Bodies.Draw(self)
    Systems.DrawSystemJumpPoints(self)
    Systems.DrawSurveyLocations(self)
    Fleets.DrawSystemFleets(self)
    return True


  def DrawMiniMap(self):
    if (self.reDraw_MapWindow):
      self.window_map.fill(Utils.SUPER_DARK_GRAY)

      self.surface.blit(self.window_map,self.window_map_anchor)
      self.reDraw_MapWindow = False
      return True
    else:
      return False


  def DrawGUI(self):
    if (self.reDraw_GUI):
      for GUI_ID in self.GUI_Elements:
        element = self.GUI_Elements[GUI_ID]
        if (element.visible):
          element.Draw(self.surface)
      self.reDraw_GUI = False
      return True
    else:
      return False


  def GetNewData(self):
    self.starSystems = Systems.GetSystems(self)
    self.currentSystemJumpPoints = Systems.GetSystemJumpPoints(self)
    self.surveyLocations = Systems.GetSurveyLocations(self, self.currentSystem)
    self.fleets = Fleets.GetFleets(self)
    self.colonies = Colonies.GetColonies(self)
    self.systemBodies = Bodies.GetSystemBodies(self)
    self.reDraw = True
    self.reDraw_FleetInfoWindow = True
    self.reDraw_MapWindow = True


  def WorldPos2ScreenPos(self, world_pos):
    scaled_world_pos = Utils.MulTuples(world_pos,(Utils.AU_INV*self.systemScale))

    return Utils.AddTuples(self.screenCenter ,scaled_world_pos)


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
        if (not sub_folder in self.images_Body):
          self.images_Body[sub_folder] = {}
        file_lower = name.lower()
        if (file_lower.endswith('.jpg')):
          if (not file_lower[0] in self.images_Body[sub_folder]):
            self.images_Body[sub_folder][file_lower[0]] = []
          hyphen = file_lower.find('.')
          if (hyphen > -1):
            body_name = file_lower[:hyphen].strip()
            self.images_Body[sub_folder][file_lower[0]].append(pygame.image.load(filename))
            self.images_Body[sub_folder][file_lower[0]][-1].set_colorkey(self.bg_color)
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
            body_name = file_lower[:hyphen].strip()
            self.images_Body[sub_folder].append(pygame.image.load(filename))
            self.images_Body[sub_folder][-1].set_colorkey(self.bg_color)

    self.systemBodies = Bodies.GetSystemBodies(self)
    self.starSystems = Systems.GetSystems(self)


  def MakeClickable(self, name, bounding_box, left_click_call_back=None, right_click_call_back=None, double_click_call_back=None, par=None, color=None, parent = None, anchor = None, enabled = True ):
    if (anchor is not None):
      bounding_box = (bounding_box[0]+anchor[0],bounding_box[1]+anchor[1],bounding_box[2],bounding_box[3])

    if (Utils.IsOnScreen(self.surface, bounding_box)):
      cl = Clickable.Clickable(self, name, bounding_box, parameter=par, 
                     LeftClickCallBack=left_click_call_back, 
                     RightClickCallBack=right_click_call_back, 
                     DoubleClickCallBack=double_click_call_back,
                     parent = parent,
                     enabled = enabled)
      if (self.Events):
        self.Events.Bind(cl)
      return cl
    else:
      return None


  def CheckClickableNotBehindGUI(self, bb):
    rect = pygame.Rect(bb)
    if (     (self.window_info_rect.colliderect(rect)) 
         or ( self.window_map_rect.colliderect(rect) ) ):
      return False
    else:
      return True


  def DebugDrawClickables(self):
    if (self.Debug):
      if (self.Events):
        for clickable in self.Events.clickables:
          if (clickable.enabled):
            pygame.draw.rect(self.surface, Utils.RED, clickable.rect, 1)


  def Follow_Jumppoint(self, id, parent):
    if (id in self.starSystems):
      self.currentSystem = id
      self.window_fleet_info_scoll_pos = 0
      InfoWindow.CleanUp(self, self.window_fleet_info_identifier)
      InfoWindow.CleanUp(self, self.window_info_identifier)
      self.GetNewData()


  def ToggleGUI(self, id, parent = None):

    if (id in self.GUI_Elements):
      self.reDraw = True
      element = self.GUI_Elements[id]
      #print('Click '+element.name)
      if (element.parent):
        element.enabled = not element.enabled
        self.ToggleGUI_Element_ByName(element.name)
        #element.clickable.enabled = not element.clickable.enabled
      else:
        if (not element.open):
          self.CloseMenus()
        element.open = not element.open

      for childID in element.children:
        if (childID not in self.GUI_Elements):
          print('Error, GUI child %d does not exist for parent %d (%s)'%(childID, id, element.name))
        else:
          child = self.GUI_Elements[childID]
          child.visible = element.open
          child.clickable.enabled = element.open


  def CloseMenus(self):
    for id in self.GUI_Elements:
      element = self.GUI_Elements[id]
      if (not element.parent):
        if (element.open):
          self.ToggleGUI(id)


  def ToggleGUI_Element_ByName(self, name):
    #self.showEmptyFleets = False
    #self.showStationaryFleets = False
    #self.showUnsurveyedLocations = True
    #self.showSurveyedLocations = False
    #self.showFleetTraces = True
    #self.showDwarfPlanets = True
    #self.showLabels_Planets = True
    #self.showLabels_DwarfPlanets = True
    #self.showLabels_Moons = True
    #self.showLabels_Comets = True
    #self.showLabels_Asteroids = False
    #self.showLabels_Stars = True

    if (name == 'Show Planets'):
      self.show_Planets = not self.show_Planets
      self.show_DwarfPlanets = self.show_Planets
    elif (name == 'Show Moons'):
      self.show_Moons = not self.show_Moons
    elif (name == 'Show Comets'):
      self.show_Comets = not self.show_Comets
    elif (name == 'Show Asteroids'):
      self.show_Asteroids = not self.show_Asteroids
    elif (name == 'Show Planet Orbits'):
      self.showOrbits_Planets = not self.showOrbits_Planets
      self.showOrbits_DwarfPlanets = self.showOrbits_Planets
    elif (name == 'Show Moon Orbits'):
      self.showOrbits_Moons = not self.showOrbits_Moons
    elif (name == 'Show Comet Orbits'):
      self.showOrbits_Comets = not self.showOrbits_Comets
    elif (name == 'Show Asteroid Orbits'):
      self.showOrbits_Asteroids = not self.showOrbits_Asteroids
    elif (name == 'Colonies'):
      self.showColonizedBodies = not self.showColonizedBodies
    elif (name == 'Resources'):
      self.showResourcefulBodies = not self.showResourcefulBodies
    elif (name == 'Installations'):
      self.showIndustrializedBodies = not self.showIndustrializedBodies
    elif (name == 'Unsurveyed'):
      self.showUnsurveyedBodies = not self.showUnsurveyedBodies
    elif (name == 'Enemies'):
      self.showEnemyBodies = not self.showEnemyBodies
    elif (name == 'Xenos'):
      self.showXenosBodies = not self.showXenosBodies
    elif (name == 'Artifacts'):
      self.showArtifactsBodies = not self.showArtifactsBodies


  def ExpandFleet(self, id, parent):
    if (id in self.fleets[self.currentSystem]):
      if (parent == self.window_fleet_info_identifier):
        if (id in self.GUI_expanded_fleets):
          self.GUI_expanded_fleets.remove(id)
        else:
          self.GUI_expanded_fleets.append(id)
        self.reDraw_FleetInfoWindow = True
      elif (parent == self.window_info_identifier):
        if (id in self.GUI_expanded_fleets2):
          self.GUI_expanded_fleets2.remove(id)
        else:
          self.GUI_expanded_fleets2.append(id)
        self.reDraw_InfoWindow = True


  def ExpandBodyInfo(self, category, parent):
    if (category == self.info_category_physical):
      self.info_cat_phys_expanded = not self.info_cat_phys_expanded
    elif (category == self.info_category_economical):
      self.info_cat_eco_expanded = not self.info_cat_eco_expanded
    elif (category == self.info_category_orbit):
      self.info_cat_orbit_expanded = not self.info_cat_orbit_expanded
    elif (category == self.info_category_stockpile):
      self.info_cat_stock_expanded = not self.info_cat_stock_expanded
    elif (category == self.info_category_installations):
      self.info_cat_inst_expanded = not self.info_cat_inst_expanded
    elif (category == self.info_category_deposits):
      self.info_cat_deposits_expanded = not self.info_cat_deposits_expanded

    self.reDraw_InfoWindow = True
