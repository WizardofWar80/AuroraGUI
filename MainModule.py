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
import SystemScreen

class Game():
  def __init__(self, eventsclass, size = (1800,1000), name = 'AuroraGUI'):
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
    #self.radius_Sun = 696000
    #self.minPixelSize_Star = 15
    #self.minPixelSize_Planet = 9
    #self.minPixelSize_Moon = 5
    #self.minPixelSize_Small = 5
    #self.mouseDragged = (0,0)
    self.refreshData = True
    self.screenCenterBeforeDrag = self.screenCenter
    self.counter_FPS = 0
    self.timestampLastSecond = pygame.time.get_ticks()
    self.timestampLast = pygame.time.get_ticks()
    self.FPS = 0
    self.reDraw = True
    self.reDraw_GUI = True
    self.clickables = []
    self.currentSceen = 'System'
    self.GUI_identifier = 'Global GUI'
    self.GUI_Elements = {}
    self.GUI_Top_Anchor = (300,10)
    self.GUI_Top_Button_Size = (130,30)

    ## Options
    self.bg_color = Utils.BLACK

    self.images_Body = {}

    self.highlighted_fleet_ID = -1
    self.highlighted_body_ID = -1

    self.images_GUI = {}
    self.systemBodies = {}

    #db_filename = 'D:\\Spiele\\Aurora4x\\AuroraDB - Copy.db'
    db_filename = 'D:\\Spiele\\Aurora4x\\AuroraDB.db'
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

    self.systemScreen = SystemScreen.SystemScreen(self, eventsclass)
    self.InitGUI()


  def InitGUI(self):
    idGUI = 1
    x = self.GUI_Top_Anchor[0]
    y = self.GUI_Top_Anchor[1]
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'System'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Bodies'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, enabled = False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Colonies'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, enabled = False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Economy'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, enabled = False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Research'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, enabled = False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Galaxy'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, enabled = False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Survey'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, enabled = False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Terraforming'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, enabled = False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Top_Button_Size[0]+5
    bb = (x,y,self.GUI_Top_Button_Size[0],self.GUI_Top_Button_Size[1])
    name = 'Xenos'
    gui_cl = self.MakeClickable(name, bb, self.SwitchScreens, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, textButton = True, enabled = False, radioButton = True, radioGroup = 0)


  def SwitchScreens(self, id, parent = None):
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
          self.currentSceen = thisElement.name
          self.SetRedrawFlag(self.currentSceen)
          for otherID in self.GUI_Elements:
            if (otherID != id):
              otherElement = self.GUI_Elements[otherID]
              if (otherElement.radioButton):
                if (otherElement.radioGroup == thisGroup):
                  otherElement.enabled = False
          

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

    return


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


  def DrawCurrentScreen(self):
    reblit = False
    if (self.currentSceen == 'System'):
      reblit |= self.systemScreen.Draw()
    else:
      self.surface.fill(self.bg_color)
      reblit = True
      print('Draw screen %s'%self.currentSceen)
    return reblit


  def SetRedrawFlag(self, screen_name):
    if (screen_name == 'System'):
      self.systemScreen.reDraw = True


  def GetNewData(self):
    self.starSystems = Systems.GetSystems(self)
    self.currentSystemJumpPoints = Systems.GetSystemJumpPoints(self)
    self.surveyLocations = Systems.GetSurveyLocations(self, self.currentSystem)
    self.fleets = Fleets.GetFleets(self)
    self.colonies = Colonies.GetColonies(self)
    self.systemBodies = Bodies.GetSystemBodies(self)


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

