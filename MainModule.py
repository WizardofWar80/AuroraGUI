import pygame
import sqlite3
import logger as lg
import Utils
import math
import random
import Clickable
import GUI
import Bodies

class Game():
  def __init__(self, eventsclass, size = (1800,1000), name = 'AuroraGUI'):
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
    self.minPixelSize_Star = 10
    self.minPixelSize_Planet = 6
    self.minPixelSize_Moon = 4
    self.minPixelSize_Small = 3
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
      self.homeSystemID = self.GetHomeSystemID()
      self.currentSystem = self.homeSystemID
      #self.currentSystem = 8497 # Alpha Centauri , knownsystem 1, component2ID 87, c2orbit 23
      #self.currentSystem = 8499 # Lalande
      #self.currentSystem = 8500
      #self.currentSystem = 8496 # EE (with Black Hole)
      self.stellarTypes = self.GetStellarTypes()
      self.gases = self.InitGases()
      self.installations = self.GetInstallationInfo()
      self.cc_cost_reduction = self.GetCCreduction()

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

    reblit |= self.DrawFleetInfoWindow()

    reblit |= self.DrawInfoWindow()

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
    #self.currentSystem = 8497 # Alpha Centauri
    #self.currentSystem = 8499
    t1 = pygame.time.get_ticks()
    self.DrawSystemBodies()
    t2 = pygame.time.get_ticks()
    dt1 = t2-t1
    t1=t2
    self.DrawSystemJumpPoints()
    t2 = pygame.time.get_ticks()
    dt2 = t2-t1
    t1=t2
    self.DrawSurveyLocations()
    t2 = pygame.time.get_ticks()
    dt3 = t2-t1
    t1=t2
    self.DrawSystemFleets()
    t2 = pygame.time.get_ticks()
    dt4 = t2-t1
    #print(dt1,dt2,dt3,dt4)
    return True


  def DrawSystemBodies(self):
    if self.currentSystem not in self.starSystems:
      return

    ###################
    # Draw Stars
    ###################
    Bodies.DrawStars(self)

    # Draw other bodies
    Bodies.DrawBodies(self)


  def DrawSystemJumpPoints(self):
    for JP_ID in self.currentSystemJumpPoints:
      JP = self.currentSystemJumpPoints[JP_ID]
      heading = math.atan2(JP['Pos'][1],JP['Pos'][0])
      screen_pos = self.WorldPos2ScreenPos(JP['Pos'])
      if (JP['Explored']):
        bb = Utils.DrawArrow(self.surface, screen_pos, Utils.GREEN,heading)
        if (self.CheckClickableNotBehindGUI(bb)):
          self.MakeClickable(JP['Destination'], bb, left_click_call_back = self.Follow_Jumppoint, par = JP['DestID'])

      pygame.draw.circle(self.surface,self.color_JP,screen_pos,5,2)
      screen_pos_label = Utils.AddTuples(screen_pos,10)
      Utils.DrawText2Surface(self.surface,JP['Destination'],screen_pos_label,14,self.color_JP)
      if (JP['Gate']):
        gate_pos = Utils.SubTuples(screen_pos,7)
        pygame.draw.rect(self.surface, self.color_Jumpgate, (gate_pos,(14,14)),1)


  def DrawSurveyLocations(self):
    for id in self.surveyLocations:
      SL = self.surveyLocations[id]
      screen_pos = self.WorldPos2ScreenPos(SL['Pos'])
      screen_pos_label = Utils.AddTuples(screen_pos,(0,10))
      if (SL['Surveyed']):
        if (self.showSurveyedLocations):
          pygame.draw.circle(self.surface,self.color_SurveyedLoc,screen_pos,5,1)
          Utils.DrawText2Surface(self.surface,str(SL['Number']),screen_pos_label,14,self.color_SurveyedLoc)
      else:
        if (self.showUnsurveyedLocations):
          pygame.draw.circle(self.surface,self.color_UnsurveyedLoc,screen_pos,5,1)
          Utils.DrawText2Surface(self.surface,str(SL['Number']),screen_pos_label,14,self.color_UnsurveyedLoc)
 

  def DrawSystemFleets(self):
    if (self.currentSystem in self.fleets):
      for fleetID in self.fleets[self.currentSystem]:
        fleet = self.fleets[self.currentSystem][fleetID]
        if (fleet['Ships'] != [] or self.showEmptyFleets or (self.highlighted_fleet_ID == fleetID)):
          if (fleet['Speed'] > 1 or self.showStationaryFleets or (self.highlighted_fleet_ID == fleetID)):
            pos = self.WorldPos2ScreenPos(fleet['Position'])
            col = self.color_Fleet
            if (self.highlighted_fleet_ID == fleetID):
              col = Utils.CYAN
            if (self.show_FleetTraces):
              prev_pos = self.WorldPos2ScreenPos(fleet['Position_prev'])
              pygame.draw.line(self.surface, col, prev_pos, pos,1)
            bb = Utils.DrawTriangle(self.surface,pos ,col, fleet['Heading'])
            if (self.CheckClickableNotBehindGUI(bb)):
              self.MakeClickable(fleet['Name'], bb, left_click_call_back = self.Select_Fleet, par=fleetID)
            if (self.highlighted_fleet_ID == fleetID):
              pygame.draw.rect(self.surface, col,(bb[0]-2,bb[1]-2,bb[2]+4,bb[3]+4),2)
            #pygame.draw.circle(self.surface,col,(pos_x,pos_y),5,Utils.FILLED)
            Utils.DrawText2Surface(self.surface,fleet['Name'],(pos[0]+10,pos[1]-6),12,col)


  def DrawFleetInfoWindow(self):
    if (self.reDraw_FleetInfoWindow):
      self.Events.ClearClickables(parent=self.window_fleet_info_identifier)
      line_height = 20
      pad_x = pad_y = 5
      lineNr = self.window_fleet_info_scoll_pos
      self.window_fleet_info.fill(Utils.SUPER_DARK_GRAY)
      #print(self.window_fleet_info_scoll_pos)
      if (self.currentSystem in self.fleets):
        for fleetID in self.fleets[self.currentSystem]:
          fleet = self.fleets[self.currentSystem][fleetID]
          if (fleet['Ships'] != [] or self.showEmptyFleets):
            color = Utils.WHITE
            if (self.highlighted_fleet_ID == fleetID):
              color = Utils.CYAN
            label_pos = (pad_x,(pad_y+lineNr*line_height))
            if (fleet['Ships'] != []):
              expRect = Utils.DrawExpander(self.window_fleet_info, (label_pos[0],label_pos[1]+3), 15, color)
              self.MakeClickable(fleet['Name'], expRect, left_click_call_back = self.ExpandFleet, par=fleetID, parent = self.window_fleet_info_identifier, anchor=self.window_fleet_info_anchor)
              label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
            label_pos, label_size = Utils.DrawText2Surface(self.window_fleet_info,fleet['Name']+ ' - ',label_pos,15,color)
            if (label_pos):
              self.MakeClickable(fleet['Name'], (label_pos[0],label_pos[1], label_size[0],label_size[1]), left_click_call_back = self.Select_Fleet, par=fleetID, parent = self.window_fleet_info_identifier, anchor=self.window_fleet_info_anchor)
            if (fleet['Speed'] > 1) and label_pos:
              speed = str(int(fleet['Speed'])) + 'km/s'

              speed_label_pos, speed_label_size = Utils.DrawText2Surface(self.window_fleet_info,speed,(label_pos[0]+label_size[0],
                                                                                                label_pos[1]),15,color)
              icon_pos = (speed_label_pos[0]+speed_label_size[0], speed_label_pos[1])
              p = 0
              if (fleet['Fuel Capacity'] > 0):
                p = fleet['Fuel']/fleet['Fuel Capacity']

              if ('fuel2' in self.images_GUI):
                icon_rect = Utils.DrawPercentageFilledImage(self.window_fleet_info, 
                                                            self.images_GUI['fuel2'], 
                                                            icon_pos, 
                                                            p, 
                                                            color_unfilled = Utils.DARK_GRAY, 
                                                            color = Utils.MED_YELLOW, 
                                                            color_low = Utils.RED, 
                                                            perc_low = 0.3, 
                                                            color_high = Utils.LIGHT_GREEN, 
                                                            perc_high = 0.7)

              icon_pos = (icon_rect[0]+icon_rect[3]+pad_x, icon_rect[1])
              p = 0
              if (fleet['Supplies Capacity'] > 0):
                p = fleet['Supplies']/fleet['Supplies Capacity']

              if ('supplies' in self.images_GUI):
                icon_rect = Utils.DrawPercentageFilledImage(self.window_fleet_info, 
                                                            self.images_GUI['supplies'], 
                                                            icon_pos, 
                                                            p, 
                                                            color_unfilled = Utils.DARK_GRAY, 
                                                            color = Utils.MED_YELLOW, 
                                                            color_low = Utils.RED, 
                                                            perc_low = 0.3, 
                                                            color_high = Utils.LIGHT_GREEN, 
                                                            perc_high = 0.7)

            #print((pad_y+lineNr*line_height), fleet['Name'])
            lineNr +=1
            if (fleetID in self.GUI_expanded_fleets):
              shipClasses = {}
              for ship in fleet['Ships']:
                if (ship['ClassName'] not in shipClasses):
                  shipClasses[ship['ClassName']] = 1
                else:
                  shipClasses[ship['ClassName']] += 1
              for shipClass in shipClasses:
                label_pos = (expRect[0]+expRect[2]+5,(pad_y+lineNr*line_height))
                label_pos, label_size = Utils.DrawText2Surface(self.window_fleet_info,'%dx%s'%(shipClasses[ship['ClassName']],shipClass),label_pos,15,color)
                lineNr +=1

      self.surface.blit(self.window_fleet_info,self.window_fleet_info_anchor)
      self.reDraw_FleetInfoWindow = False
      return True
    else:
      return False


  def DrawInfoWindow(self):
    if (self.reDraw_InfoWindow):
      self.Events.ClearClickables(parent=self.window_info_identifier)
      line_height = 20
      pad_x = pad_y = 5
      lineNr = 0
      self.window_info.fill(Utils.SUPER_DARK_GRAY)
      color = Utils.WHITE
      if (self.highlighted_fleet_ID in self.fleets):
        fleet = self.fleets[self.highlighted_fleet_ID]
        label_pos = (pad_x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(self.window_info,fleet['Name'],label_pos,15,color)
      elif (self.highlighted_body_ID in self.starSystems[self.currentSystem]['Stars']):
        body = self.starSystems[self.currentSystem]['Stars'][self.highlighted_body_ID]
        #prefix = Utils.StarTypes[body['BodyClass']]+' '
        prefix = Utils.GetStarDescription(body) + ' '
        label_pos = (pad_x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(self.window_info,prefix+body['Name'],label_pos,15,color)
        lineNr+=1
        label_pos = (pad_x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Radius:',label_pos,15,color)
        label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(self.window_info,str(body['Radius']),label_pos2,15,color)
        lineNr+=1
        label_pos = (pad_x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Mass:',label_pos,15,color)
        label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(self.window_info,str(body['Mass']),label_pos2,15,color)
        lineNr+=1
        label_pos = (pad_x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Temp:',label_pos,15,color)
        label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(self.window_info,str(body['Temp'])+'K',label_pos2,15,color)
        lineNr+=1
        label_pos = (pad_x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Luminosity:',label_pos,15,color)
        label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(self.window_info,str(body['Luminosity'])+' Suns',label_pos2,15,color)
        lineNr+=1
        if (body['BodyClass'] in Utils.SpectralColors):
          col = Utils.SpectralColors[body['BodyClass']]
          label_pos = (pad_x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Color:',label_pos,15,color)
          label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,col,label_pos2,15,color)
      elif (self.highlighted_body_ID in self.systemBodies):
        body = self.systemBodies[self.highlighted_body_ID]
        label_pos = (pad_x,(pad_y+lineNr*line_height))
        if (body['Class'] == 'Asteroid' or body['Class'] == 'Comet' or body['Class'] == 'Moon'):
          name = body['Name']
          if (body['Class'] == 'Comet' and name.find('Comet') == -1):
            name = 'Comet '+name
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,name+(' (Unsurveyed)' if body['Unsurveyed'] else ''),label_pos,15,color)
        else:
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,body['Class']+' '+body['Name']+(' (Unsurveyed)' if body['Unsurveyed'] else ''),label_pos,15,color)
        
        # Physical body info
        lineNr+=1
        x = label_pos[0]
        label_pos = (x,(pad_y+lineNr*line_height))
        expRect = Utils.DrawExpander(self.window_info, (label_pos[0],label_pos[1]+3), 15, color)
        self.MakeClickable(self.info_category_physical, expRect, left_click_call_back = self.ExpandBodyInfo, par=self.info_category_physical, parent = self.window_info_identifier, anchor=self.window_info_anchor)
        label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
        label_pos, label_size = Utils.DrawText2Surface(self.window_info,self.info_category_physical,label_pos,15,color)
        if (self.info_cat_phys_expanded):
          lat_offs = 130
          lineNr+=1
          x = label_pos[0]+pad_x
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Type:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,body['Type'],label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Radius:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,str(body['RadiusBody'])+' km',label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Colony Cost:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%2.3f'%body['ColonyCost'],label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Pop Capacity:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,f"{body['Population Capacity']:,} M",label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Gravity:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%s x Earth'%Utils.GetFormattedNumber(body['Gravity']),label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Mass:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%s x Earth'%Utils.GetFormattedNumber(body['Mass']),label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Orbit:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%s AU'%Utils.GetFormattedNumber(body['Orbit']),label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Year:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,Utils.GetTimeScale(body['HoursPerYear']),label_pos2,15,color)
          if (body['Class'] != 'Comet'):
            lineNr+=1
            label_pos = (x,(pad_y+lineNr*line_height))
            label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Day:',label_pos,15,color)
            label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
            label_pos2, label_size = Utils.DrawText2Surface(self.window_info,Utils.GetTimeScale(body['HoursPerDay'])+(' - tidal locked' if body['Tidal locked'] else ''), label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Temperature:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%d C'%(int(body['Temperature'])),label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Atmosphere:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,('%s atm'%Utils.GetFormattedNumber(body['AtmosPressure'])) if body['AtmosPressure'] > 0 else '-',label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Hydrosphere:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,('%s'%Utils.GetFormattedNumber(body['Hydrosphere'])) if body['AtmosPressure'] > 0 else '-',label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Magnetic Field:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,('%s'%Utils.GetFormattedNumber(body['MagneticField'])) if body['MagneticField'] > 0 else '-',label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Density:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%s'%Utils.GetFormattedNumber(body['Density']),label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Escape Velocity:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%s m/s'%Utils.GetFormattedNumber(body['EscapeVelocity']),label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Greenhouse Factor:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(self.window_info,('%s'%Utils.GetFormattedNumber(body['GHFactor'])) if body['AtmosPressure'] > 0 else '-',label_pos2,15,color)

        # Economical body info
        if (self.highlighted_body_ID in self.colonies):
          colony = self.colonies[self.highlighted_body_ID]
          lineNr+=1
          x = pad_x
          label_pos = (x,(pad_y+lineNr*line_height))
          expRect1 = Utils.DrawExpander(self.window_info, (label_pos[0],label_pos[1]+3), 15, color)
          self.MakeClickable(self.info_category_economical, expRect1, left_click_call_back = self.ExpandBodyInfo, par=self.info_category_economical, parent = self.window_info_identifier, anchor=self.window_info_anchor)
          label_pos = (expRect1[0]+expRect1[2]+5,label_pos[1])
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,self.info_category_economical,label_pos,15,color)
          if (self.info_cat_eco_expanded):
            lat_offs = 140
            lineNr+=1
            x = label_pos[0]+pad_x
            label_pos = (x,(pad_y+lineNr*line_height))
            label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Population:',label_pos,15,color)
            label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
            label_pos2, label_size = Utils.DrawText2Surface(self.window_info,str(colony['Pop']),label_pos2,15,color)
            lineNr+=1
            supported_pop = 0
            found_Installations = False
            for installationID in colony['Installations']:
              amountInstallations = colony['Installations'][installationID]['Amount']
              if (amountInstallations > 0):
                found_Installations = True
              if (colony['Installations'][installationID]['Name'] == 'Infrastructure'):
                colonyCost = colony['ColonyCost'] * (1-self.cc_cost_reduction)
                if (colonyCost == 0):
                  supported_pop = body['Population Capacity']
                else:
                  supported_pop = amountInstallations / colonyCost / 100
                if (found_Installations):
                  break
            label_pos = (x,(pad_y+lineNr*line_height))
            label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Population Supported:',label_pos,15,color)
            label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
            label_pos2, label_size = Utils.DrawText2Surface(self.window_info,f"{round(supported_pop,2):,} M",label_pos2,15,color)
            lineNr+=1
            label_pos = (x,(pad_y+lineNr*line_height))
            label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Annual Growth:',label_pos,15,color)
            label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
            label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%1.2f%%'%(0),label_pos2,15,color)
            lineNr+=1
            label_pos = (x,(pad_y+lineNr*line_height))
            label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Protection:',label_pos,15,color)
            req = 0
            act = 0
            label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
            label_pos2, label_size = Utils.DrawText2Surface(self.window_info,'%d / %d'%(act,req),label_pos2,15,Utils.MED_GREEN if act >= req else Utils.RED)

            if (colony['Stockpile']['Sum'] > 0 or colony['Stockpile']['Sum of Minerals'] > 0):
              lineNr+=1
              x = expRect1[0]+expRect1[2]+5
              label_pos = (x,(pad_y+lineNr*line_height))
              #label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Stockpile',label_pos,15,color)
              expRect2 = Utils.DrawExpander(self.window_info, (label_pos[0],label_pos[1]+3), 15, color)
              self.MakeClickable(self.info_category_stockpile, expRect2, left_click_call_back = self.ExpandBodyInfo, par=self.info_category_stockpile, parent = self.window_info_identifier, anchor=self.window_info_anchor)
              label_pos = (expRect2[0]+expRect2[2]+5,label_pos[1])
              label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Stockpile',label_pos,15,color)
              if (self.info_cat_stock_expanded):
                lat_offs = 70
                x = expRect2[0]+expRect2[2]+5
                lineNr+=1
                if (colony['Stockpile']['Sum'] > 0):
                  label_pos = (x,(pad_y+lineNr*line_height))
                  label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Fuel:',label_pos,15,color)
                  label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
                  label_pos2, label_size = Utils.DrawText2Surface(self.window_info,f"{colony['Stockpile']['Fuel']:,}",label_pos2,15,color)
                  lineNr+=1
                  label_pos = (x,(pad_y+lineNr*line_height))
                  label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Supplies:',label_pos,15,color)
                  label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
                  label_pos2, label_size = Utils.DrawText2Surface(self.window_info,f"{colony['Stockpile']['Supplies']:,}",label_pos2,15,color)
                  lineNr+=1
                if (colony['Stockpile']['Sum of Minerals'] > 0):
                  lat_offs2 = 30
                  for index in Utils.MineralNames:
                    mineral = Utils.MineralNames[index]
                    amount = colony['Stockpile'][mineral]
                    label_pos = (x,(pad_y+lineNr*line_height))
                    label_pos, label_size = Utils.DrawText2Surface(self.window_info,'%s:'%mineral[:2],label_pos,15,color)
                    label_pos2 = (x+lat_offs2,(pad_y+lineNr*line_height))
                    label_pos2, label_size = Utils.DrawText2Surface(self.window_info,f"{amount:,}",label_pos2,15,color)
                    lineNr+=1
                    if (index == 6):
                      lineNr -= 6
                      x += 100
          
            lineNr+=1
            # installations
            if (found_Installations):
              x = expRect1[0]+expRect1[2]+5
              label_pos = (x,(pad_y+lineNr*line_height))
              #label_pos, label_size = Utils.DrawText2Surface(self.window_info,'Stockpile',label_pos,15,color)
              expRect2 = Utils.DrawExpander(self.window_info, (label_pos[0],label_pos[1]+3), 15, color)
              self.MakeClickable(self.info_category_installations, expRect2, left_click_call_back = self.ExpandBodyInfo, par=self.info_category_installations, parent = self.window_info_identifier, anchor=self.window_info_anchor)
              label_pos = (expRect2[0]+expRect2[2]+5,label_pos[1])
              label_pos, label_size = Utils.DrawText2Surface(self.window_info,self.info_category_installations,label_pos,15,color)
              lineNr+=1
              if (self.info_cat_inst_expanded):
                x = expRect2[0]+expRect2[2]+5
                for InstallationID in colony['Installations']:
                  installation = colony['Installations'][InstallationID]
                  name = installation['Name']
                  amount = installation['Amount']
                  if (installation['Amount'] > 0):
                    lat_offs2 = 40
                    label_pos = (x,(pad_y+lineNr*line_height))
                    label_pos, label_size = Utils.DrawText2Surface(self.window_info,'%4d'%amount,label_pos,15,color)
                    label_pos2 = (x+lat_offs2,(pad_y+lineNr*line_height))
                    label_pos2, label_size = Utils.DrawText2Surface(self.window_info,name,label_pos2,15,color)
                    lineNr+=1
                    #if (index == 6):
                    #  lineNr -= 6
                    #  x += 100
        
        fleetsInOrbit = False
        for fleetID in self.fleets[self.currentSystem]:
          fleet = self.fleets[self.currentSystem][fleetID]
          if (fleet['Orbit']['Body'] == self.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
            fleetsInOrbit = True
            break
        if fleetsInOrbit:
          if (not self.info_cat_eco_expanded):
            lineNr+=1
          x = pad_x
          label_pos = (x,(pad_y+lineNr*line_height))
          expRect = Utils.DrawExpander(self.window_info, (label_pos[0],label_pos[1]+3), 15, color)
          self.MakeClickable(self.info_category_orbit, expRect, left_click_call_back = self.ExpandBodyInfo, par=self.info_category_orbit, parent = self.window_info_identifier, anchor=self.window_info_anchor)
          label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
          label_pos, label_size = Utils.DrawText2Surface(self.window_info,self.info_category_orbit,label_pos,15,color)
          lineNr+=1
          orbitFleetTopRow = lineNr
          pygame.draw.line(self.window_info, Utils.WHITE, (x,(pad_y+lineNr*line_height-2)),((x+200,(pad_y+lineNr*line_height-2))),1)
          lineNr+=self.window_info_scoll_pos
          if (self.info_cat_orbit_expanded):
            x = label_pos[0] if label_pos else (expRect[0]+expRect[2]+5)
            # orbiting fleets
            for fleetID in self.fleets[self.currentSystem]:
              fleet = self.fleets[self.currentSystem][fleetID]
              if (fleet['Orbit']['Body'] == self.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
                if (lineNr >= orbitFleetTopRow):
                  color = Utils.WHITE
                  label_pos = (x,(pad_y+lineNr*line_height))
                  if (fleet['Ships'] != []):
                    expRect = Utils.DrawExpander(self.window_info, (label_pos[0],label_pos[1]+3), 15, color)
                    self.MakeClickable(fleet['Name'], expRect, left_click_call_back = self.ExpandFleet, par=fleetID, parent = self.window_info_identifier, anchor=self.window_info_anchor)
                  else:
                    expRect = pygame.draw.rect(self.window_info, color, (label_pos[0]+1,label_pos[1]+3+1, 15-2, 15-2), 1)
                  label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
                  label_pos, label_size = Utils.DrawText2Surface(self.window_info,fleet['Name']+ ' - ',label_pos,15,color)
                  if (label_pos):
                    self.MakeClickable(fleet['Name'], (label_pos[0],label_pos[1], label_size[0],label_size[1]), left_click_call_back = self.Select_Fleet, par=fleetID, parent = self.window_info_identifier, anchor=self.window_info_anchor)
                    p = 0
                    icon_pos = (label_pos[0]+label_size[0], label_pos[1])
                    if (fleet['Fuel Capacity'] > 0):
                      p = fleet['Fuel']/fleet['Fuel Capacity']

                    if ('fuel2' in self.images_GUI):
                      icon_rect = Utils.DrawPercentageFilledImage(self.window_info, 
                                                                  self.images_GUI['fuel2'], 
                                                                  icon_pos, 
                                                                  p, 
                                                                  color_unfilled = Utils.DARK_GRAY, 
                                                                  color = Utils.MED_YELLOW, 
                                                                  color_low = Utils.RED, 
                                                                  perc_low = 0.3, 
                                                                  color_high = Utils.LIGHT_GREEN, 
                                                                  perc_high = 0.7)

                    icon_pos = (icon_rect[0]+icon_rect[3]+pad_x, icon_rect[1])
                    p = 0
                    if (fleet['Supplies Capacity'] > 0):
                      p = fleet['Supplies']/fleet['Supplies Capacity']

                    if ('supplies' in self.images_GUI):
                      icon_rect = Utils.DrawPercentageFilledImage(self.window_info, 
                                                                  self.images_GUI['supplies'], 
                                                                  icon_pos, 
                                                                  p, 
                                                                  color_unfilled = Utils.DARK_GRAY, 
                                                                  color = Utils.MED_YELLOW, 
                                                                  color_low = Utils.RED, 
                                                                  perc_low = 0.3, 
                                                                  color_high = Utils.LIGHT_GREEN, 
                                                                  perc_high = 0.7)

                  #print((pad_y+lineNr*line_height), fleet['Name'])
                  lineNr +=1

                  if (fleetID in self.GUI_expanded_fleets2):
                    shipClasses = {}
                    for ship in fleet['Ships']:
                      if (ship['ClassName'] not in shipClasses):
                        shipClasses[ship['ClassName']] = 1
                      else:
                        shipClasses[ship['ClassName']] += 1
                    for shipClass in shipClasses:
                      label_pos = (expRect[0]+expRect[2]+5,(pad_y+lineNr*line_height))
                      label_pos, label_size = Utils.DrawText2Surface(self.window_info,'%dx%s'%(shipClasses[ship['ClassName']],shipClass),label_pos,15,color)
                      lineNr +=1
                else:
                  lineNr +=1

      self.surface.blit(self.window_info,self.window_info_anchor)
      self.reDraw_InfoWindow = False
      return True
    else:
      return False


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


  def GetHomeSystemID(self):
    system_number = self.db.execute('''SELECT systemId from FCT_System WHERE GameID = %d AND SystemNumber = 0;'''%(self.gameID)).fetchone()[0]
        
    return system_number


  def GetSystemName(self, systemID):
    system_number = self.db.execute('''SELECT SystemNumber from FCT_System WHERE GameID = %d AND systemId = %d;'''%(self.gameID,systemID)).fetchone()[0]
    if (system_number > -1):
        system_name = self.db.execute('''SELECT ConstellationName from DIM_KnownSystems WHERE KnownSystemID = %d;'''%system_number).fetchone()[0].strip()
        if (not system_name):
          system_name = self.db.execute('''SELECT Name from DIM_KnownSystems WHERE KnownSystemID = %d;'''%system_number).fetchone()[0]
    else:
        system_name = 'Unknown'
    return system_name


  def GetSystems(self):
    systems = {}

    results = self.db.execute('''SELECT SystemID, SystemNumber from FCT_System WHERE GameID = %d;'''%(self.gameID)).fetchall()
    
    for (systemID, systemNumber) in results:
      if (systemNumber != -1):
        known_system = self.db.execute('''SELECT * from DIM_KnownSystems WHERE KnownSystemID = %d;'''%systemNumber).fetchone()
        system = {}
        system['Name'] = self.GetSystemName(systemID)
        system['Stars'] = None
        stars_table = self.db.execute('''SELECT * from FCT_Star WHERE GameID = %d AND SystemID = %d;'''%(self.gameID,systemID))
        stars = {}
        component2ID = {}
        num_stars = 0
        for x in stars_table:
          num_stars += 1
        # we moved the cursor so we have to run the query again
        stars_table = self.db.execute('''SELECT * from FCT_Star WHERE GameID = %d AND SystemID = %d;'''%(self.gameID,systemID))
        
        #8497 Alpha Centauri , knownsystem 1, component2ID 87, c2orbit 23
        star_index = 0
        for star in stars_table:
          ID = star[0]
          stars[ID] = {}
          stars[ID]['Name'] = system['Name']
          if (num_stars > 1):
            stars[ID]['Name'] += '-'+Utils.star_suffixes[star_index]

          stars[ID]['Component'] = star[8]
          stars[ID]['StellarTypeID']=star[3]
          stars[ID]['Radius']=self.stellarTypes[stars[ID]['StellarTypeID']]['Radius']
          stars[ID]['Mass'] = self.stellarTypes[stars[ID]['StellarTypeID']]['Mass']
          stars[ID]['Temp'] = self.stellarTypes[stars[ID]['StellarTypeID']]['Temperature']
          stars[ID]['Luminosity'] = self.stellarTypes[stars[ID]['StellarTypeID']]['Luminosity']
          stars[ID]['Black Hole']=False
          spectralClass = self.stellarTypes[stars[ID]['StellarTypeID']]['SpectralClass']
          spectralNumber = self.stellarTypes[stars[ID]['StellarTypeID']]['SpectralNumber']
          sizeText = self.stellarTypes[stars[ID]['StellarTypeID']]['SizeText']
          stars[ID]['Suffix'] = spectralClass + str(spectralNumber) +'-'+ sizeText
          if (spectralClass == 'BH'):
            # black holes should use Schwartzschildradius:
            # r = M * 0.000004246 sunradii
            m = self.stellarTypes[stars[ID]['StellarTypeID']]['Mass']
            stars[ID]['Radius'] = m * 0.000004246 * 6
            stars[ID]['Black Hole']=True
          component2ID[star[8]] = ID
          stars[ID]['Parent'] = parentComponent = star[9]
          if (stars[ID]['Parent'] == 0):
            stars[ID]['ParentPos'] = (0,0)
          else:
            stars[ID]['ParentPos'] = stars[component2ID[parentComponent]]['Pos']
          stars[ID]['Bearing'] = star[10]
          stars[ID]['OrbitDistance'] = star[13]
          stars[ID]['Eccentricity'] = star[15]
          stars[ID]['EccentricityAngle'] = star[16]
          stars[ID]['Pos'] = (star[6],star[7])
          stars[ID]['Image'] = None
          if (len(self.images_Body) > 0):
            if (spectralClass in self.images_Body['Stars']):
              stars[ID]['Image'] = self.images_Body['Stars'][spectralClass]
          star_index += 1
          stars[ID]['BodyClass']=spectralClass
          stars[ID]['BodyType']='Stellar'
        system['Stars'] = stars
        systems[systemID] = system
    return systems


  def GetStellarTypes(self):
    stellarTypes = {}

    results = self.db.execute('''SELECT StellarTypeID, SpectralClass, SpectralNumber, SizeText, SizeID, Luminosity, Mass, Temperature, Radius, Red, Green, Blue from DIM_StellarType;''').fetchall()
    
    for stellarType in results:
      #stellarType = results[stellarTypeID]
      stellarTypeID = stellarType[0]
      stellarTypes[stellarTypeID] = { 'SpectralClass':stellarType[1]
                                     ,'SpectralNumber':stellarType[2]
                                     ,'SizeText':stellarType[3]
                                     ,'SizeID':stellarType[4]
                                     ,'Luminosity':stellarType[5]
                                     ,'Mass':stellarType[6]
                                     ,'Temperature':stellarType[7]
                                     ,'Radius':stellarType[8]
                                     ,'RGB':(stellarType[9],stellarType[10],stellarType[11])
                                    }
        
    return stellarTypes


  def GetInstallationInfo(self):
    installations = {}

    results = self.db.execute('''SELECT PlanetaryInstallationID, Name from DIM_PlanetaryInstallation;''').fetchall()

    for installation in results:
      installationID = installation[0]
      installationName = installation[1]
      installations[installationID] = {'Name' : installationName}
        
    return installations


  def GetMineralDeposits(self, systemID):
    deposits = {}
    # GameID	MaterialID	SystemID	SystemBodyID	Amount	Accessibility	HalfOriginalAmount	OriginalAcc
    results = self.db.execute('''SELECT * from FCT_MineralDeposit WHERE GameID = %d and SystemID = %d;'''%(self.gameID, systemID)).fetchall()

    for deposit in results:
      systemBodyID = deposit[2]
      deposits[systemBodyID]={}
      if (deposit[0] in Utils.MineralNames):
        mineral = Utils.MineralNames[deposit[0]]
        deposits[systemBodyID][mineral] = {'Amount':deposit[4], 'Accessibility':deposit[5]}

    return deposits


  def GetSystemBodies(self):
    systemBodies = {}
    body_table = [list(x) for x in self.db.execute('''SELECT SystemBodyID, Name, PlanetNumber, OrbitNumber, OrbitalDistance, ParentBodyID, Radius, Bearing, Xcor, Ycor, Eccentricity, EccentricityDirection, BodyClass, BodyTypeID, SurfaceTemp, AtmosPress, HydroExt, Mass, SurfaceTemp, Year
, DayValue, TidalLock, MagneticField, EscapeVelocity, GHFactor, Density, Gravity from FCT_SystemBody WHERE GameID = %d AND SystemID = %d;'''%(self.gameID,self.currentSystem))]
    deposits = self.GetMineralDeposits(self.currentSystem)
            # Mass
        # Orbit
        # hours / day
        # day / year
        # Temperature
        # Atmospheric pressure
        # EscapeVelocity
        # Tidal locked

    for body in body_table:
      body_name = body[1]
      planetNumber = body[2]
      orbitNumber = body[3]
      parentID = body[5]
      bodyType = '?'
      bodyClass = '?'
      if (body[13] in Utils.BodyTypes):
        bodyType = Utils.BodyTypes[body[13]]
      if (body[12] in Utils.BodyClasses):
        bodyClass = Utils.BodyClasses[body[12]]

      if (body_name == ''):
        body_name = self.db.execute('''SELECT Name from FCT_SystemBodyName WHERE GameID = %d AND RaceID = %d AND SystemID = %d AND SystemBodyID = %d ;'''%(self.gameID,self.myRaceID, self.currentSystem, body[0])).fetchone()
        if (not body_name):
          if (parentID in systemBodies):
            parentName = systemBodies[parentID]['Name']
          elif(parentID in self.starSystems[self.currentSystem]['Stars']):
            parentName = self.starSystems[self.currentSystem]['Stars'][parentID]['Name']

          if (bodyClass == 'Moon'):
            hyphen_pos = parentName.rfind('-')
            if (hyphen_pos > -1):
              parentName = 'Moon ' + parentName[hyphen_pos+1:].replace(' ','-')
          else:
            parentName += ' ' + Utils.Int2Roman(planetNumber)
          body_name = parentName + ((' ' + str(orbitNumber)) if orbitNumber > 0 else '')

      a = d = orbit = body[4] 
      r = body[6]
      angle = body[7]
      body_pos = (body[8], body[9])
      angle2 = body[11]
      E = body[10]
      temp = body[14]-273
      atm = body[15]
      hydro = body[16]
      mass = body[17]
      surfaceTemp = body[18]
      hoursPerYear = body[19]
      hoursPerDay = body[20]
      tidalLock = body[21]
      magneticField = body[22]
      escapeVelocity = body[23]
      gHFactor = body[24]
      density = body[25]
      gravity = body[26]
      
      if (bodyType == 'Planet Gas Giant' or bodyType == 'Planet Super Jovian'):
        popCapacity = 0
      else:
        hydroMultiPlier = 1
        tidalMultiPlier = 1
        if (hydro > 75):
          hydroMultiPlier = -0.0396*hydro+3.97
        if (tidalLock and bodyClass == 'Planet'):
          tidalMultiPlier = .2
        surfaceArea = 4*r*r*math.pi
        surfAreaEarth =  511185932.52 
        popCapacity = 12000*surfaceArea/surfAreaEarth
        # todo: Add population desnsity multiplier from race

        popCapacity = popCapacity*hydroMultiPlier*tidalMultiPlier
        popCapacity = round(popCapacity,3) if popCapacity < 0.1 else round(popCapacity,1) if popCapacity < 10 else int(round(popCapacity,0))
        if (popCapacity < 0.05):
          popCapacity = 0.05

      colonyCost = self.CalculateColonyCost(body[0], temp, atm, hydro, gravity, tidalMultiPlier)

      if (bodyClass == 'Moon'):
        orbit = orbit * Utils.AU_INV
      image = None
      if (len(self.images_Body) > 0):
        if (body_name.lower() in self.images_Body['Sol']):
          image = self.images_Body['Sol'][body_name.lower()]
        else:
          if (bodyClass == 'Asteroid'):
            numImages = len(self.images_Body['Asteroids'])
            selectedImage = random.randint(0,numImages-1)
            image = self.images_Body['Asteroids'][selectedImage]
          elif (bodyClass == 'Planet') or (bodyClass == 'Moon'):
            if (bodyType == 'Planet Gas Giant' or bodyType == 'Planet Super Jovian'):
              numImages = len(self.images_Body['Gas Giants'])
              selectedImage = random.randint(0,numImages-1)
              image = self.images_Body['Gas Giants'][selectedImage]
            elif (bodyType == 'Planet Small' or bodyType == 'Moon Small'):
              numImages = len(self.images_Body['Small Bodies'])
              selectedImage = random.randint(0,numImages-1)
              image = self.images_Body['Small Bodies'][selectedImage]
            else:
              if (temp > 100):
                numImages = len(self.images_Body['Planets']['h'])
                selectedImage = random.randint(0,numImages-1)
                image = self.images_Body['Planets']['h'][selectedImage]
              elif (hydro > 80):
                numImages = len(self.images_Body['Planets']['o'])
                selectedImage = random.randint(0,numImages-1)
                image = self.images_Body['Planets']['o'][selectedImage]
              elif (hydro > 50):
                numImages = len(self.images_Body['Planets']['m'])
                selectedImage = random.randint(0,numImages-1)
                image = self.images_Body['Planets']['m'][selectedImage]
              elif (atm > 0.01):
                numImages = len(self.images_Body['Planets']['b'])
                selectedImage = random.randint(0,numImages-1)
                image = self.images_Body['Planets']['b'][selectedImage]
              else:
                numImages = len(self.images_Body['Planets']['a'])
                selectedImage = random.randint(0,numImages-1)
                image = self.images_Body['Planets']['a'][selectedImage]
          elif (bodyClass == 'Comet'):
            numImages = len(self.images_Body['Comets'])
            selectedImage = random.randint(0,numImages-1)
            image = self.images_Body['Comets'][selectedImage]
      
      resources = False
      enemies = False
      xenos = False
      artifacts = False

      #check for surveyed bodies
      unsurveyed = False
      result = self.db.execute('''SELECT SystemBodyID from FCT_SystemBodySurveys WHERE GameID = %d AND RaceID = %d AND SystemBodyID = %d;'''%(self.gameID, self.myRaceID, body[0])).fetchone()
      if (not result):
        unsurveyed = True

      colonized = False
      industrialized = False
      if (body[0] in self.colonies):
        colony = self.colonies[body[0]]
        if (colony['Pop'] > 0):
          colonized = True
        if (self.colonies[body[0]]['Installations']):
          industrialized = True
        if (body[0] in deposits):
          resources = True

      systemBodies[body[0]]={'ID':body[0],'Name':body_name, 'Type':bodyType, 'Class':bodyClass, 'Orbit':orbit, 'ParentID':body[5], 'RadiusBody':body[6], 'Bearing':body[7],
                              'Eccentricity':body[10],'EccentricityAngle':body[11], 'Pos':(body[8], body[9]), 'Mass':mass, 'Gravity':gravity, 'Temperature':temp, 'Population Capacity':popCapacity, 'AtmosPressure':atm, 'ColonyCost':colonyCost,
                              'Hydrosphere':hydro, 'HoursPerYear': hoursPerYear, 'HoursPerDay': hoursPerDay, 'GHFactor':gHFactor, 'Density':density, 'Tidal locked':tidalLock, 
                              'MagneticField':magneticField, 'EscapeVelocity':escapeVelocity, 'Image':image, 'Colonized':colonized, 'Resources':resources,
                              'Industrialized':industrialized, 'Xenos':xenos, 'Enemies':enemies, 'Unsurveyed':unsurveyed, 'Artifacts':artifacts}
    return systemBodies


  def GetFleets(self):
    fleets = {}
    fleets_table = [list(x) for x in self.db.execute('''SELECT * from FCT_Fleet WHERE GameID = %d AND CivilianFunction = 0 AND RaceID = %d;'''%(self.gameID,self.myRaceID))]
    for item in fleets_table:
      fleetId = item[0]
      systemID = item[9]
      system_name = self.GetSystemName(systemID)
      if systemID not in fleets:
        fleets[systemID] = {}
      fleets[systemID][fleetId] = {}
      fleets[systemID][fleetId]['Name'] = item[2]
      fleets[systemID][fleetId]['System_Name'] = system_name
      fleets[systemID][fleetId]['MaxSpeed'] = item[16]
      fleets[systemID][fleetId]['Position'] = (x,y) = (item[18],item[19])
      fleets[systemID][fleetId]['Position_prev'] = (x_prev,y_prev) = (item[23],item[24])
      fleets[systemID][fleetId]['LastMoveTime'] = item[22]
      fleets[systemID][fleetId]['Orbit'] = {}
      fleets[systemID][fleetId]['Orbit']['Body'] = item[5]
      fleets[systemID][fleetId]['Orbit']['Distance'] = item[6]
      fleets[systemID][fleetId]['Orbit']['Bearing'] = item[7]
      fleets[systemID][fleetId]['Heading'] = math.atan2((y-y_prev),(x-x_prev))/math.pi*180
      fleets[systemID][fleetId]['Speed'] = 0
      if (self.deltaTime > 0 and fleets[systemID][fleetId]['LastMoveTime'] > 0):
        fleets[systemID][fleetId]['Speed'] = math.sqrt((Utils.Sqr(y-y_prev)+Utils.Sqr(x-x_prev)))/self.deltaTime
      
      # Add ships to fleet
      ships_table = [list(x) for x in self.db.execute('''SELECT * from FCT_Ship WHERE FleetID = %d;'''%fleetId)]
      fleets[systemID][fleetId]['Ships'] = []
      fleetFuel = 0
      fleetFuelCapacity = 0
      fleetSupplies = 0
      fleetSuppliesCapacity = 0
      fleetMagazineCapacity = 0
      for ship in ships_table:
        name = ship[3]
        fuel = ship[16]
        supplies = ship[44]
        shipClassID = ship[33]
        shipClass = self.db.execute('''SELECT * from FCT_ShipClass WHERE ShipClassID = %d;'''%(shipClassID)).fetchall()[0]
        shipClassName = shipClass[1]
        fuelCapacity = shipClass[27]
        suppliesCapacity = shipClass[84]
        magazineCapacity = shipClass[38]
        fleets[systemID][fleetId]['Ships'].append({'Name':name, 'ClassName':shipClassName, 'ClassID': shipClassID, 'Fuel':fuel, 'Fuel Capacity':fuelCapacity, 'Supplies':supplies, 'Supplies Capacity':suppliesCapacity, 'Magazine Capacity':magazineCapacity})
        fleetFuel += fuel
        fleetFuelCapacity += fuelCapacity
        fleetSupplies += supplies
        fleetSuppliesCapacity += suppliesCapacity
        fleetMagazineCapacity +=magazineCapacity
      fleets[systemID][fleetId]['Fuel'] = fleetFuel
      fleets[systemID][fleetId]['Fuel Capacity'] = fleetFuelCapacity
      fleets[systemID][fleetId]['Supplies'] = fleetSupplies
      fleets[systemID][fleetId]['Supplies Capacity'] = fleetSuppliesCapacity
      fleets[systemID][fleetId]['Magazine Capacity'] = fleetMagazineCapacity


    return fleets
    #FleetID	GameID	FleetName	AssignedPopulationID	ParentCommandID	OrbitBodyID	OrbitDistance	OrbitBearing	RaceID	SystemID	TradeLocation	CivilianFunction	NPRHomeGuard	TFTraining	SpecialOrderID	SpecialOrderID2	Speed	MaxNebulaSpeed	Xcor	Ycor	LastXcor	LastYcor	LastMoveTime	IncrementStartX	IncrementStartY	EntryJPID	CycleMoves	JustDivided	AxisContactID	Distance	OffsetBearing	ConditionOne	ConditionTwo	ConditionalOrderOne	ConditionalOrderTwo	AvoidDanger	AvoidAlienSystems	NPROperationalGroupID	DisplaySensors	DisplayWeapons	AssignedFormationID	ShippingLine	UseMaximumSpeed	RedeployOrderGiven	MaxStandingOrderDistance	NoSurrender	SpecificThreatID	AnchorFleetID	AnchorFleetDistance	AnchorFleetBearingOffset	GuardNearestHostileContact	UseAnchorDestination	GuardNearestKnownWarship	AssumeJumpCapable	LastTransitTime
    #103154	95	CS-01 Arthur C. Clarke	11031	631	733035	0	0.0	418	8430	0	0	0		0	0	277	1	-127928691.574465	75822860.0936825	-127928691.574465	75822860.0936825	1352898000.0	-127928691.574465	75822860.0936825	23222	0	0	0	0	0	0	0	7	0	1	0	0	1	1	0	0	1	0	0	0	0	0	0.0	0.0	0	0	0	0	1336014000.0
    #ShipID	GameID	FleetID	ShipName	SubFleetID	ActiveSensorsOn	AssignedMSID	Autofire	BoardingCombatClock	Constructed	CrewMorale	CurrentCrew	CurrentShieldStrength	DamageControlID	Destroyed	FireDelay	Fuel	GradePoints	HoldTechData	KillTonnageCommercial	KillTonnageMilitary	LastLaunchTime	LastOverhaul	LastShoreLeave	LaunchMorale	MaintenanceState	MothershipID	RaceID	RefuelPriority	RefuelStatus	ScrapFlag	SensorDelay	ShieldsActive	ShipClassID	ShipFuelEfficiency	ShipNotes	ShippingLineID	SpeciesID	SyncFire	TFPoints	TransponderActive	OrdnanceTransferStatus	HangarLoadType	ResupplyPriority	CurrentMaintSupplies	AutomatedDamageControl	TractorTargetShipID	TractorTargetShipyardID	TractorParentShipID	OverhaulFactor	BioEnergy	LastMissileHitTime	LastBeamHitTime	LastDamageTime	LastPenetratingDamageTime	AssignedFormationID	DistanceTravelled	HullNumber	ParentSquadronID	AssignedSquadronID	LastTransitTime	LastFiringTime	ResupplyStatus
    #47291	95	103154	Arthur C. Clarke 001	0	0	0	0	0	270864000.0	1.0	140	0.0	0	0	0	100000.0	1000.0	0	0	0	0.0	2203468200.0	2203468200.0	0.0	0	0	418	0	0	0	0	0	28338		None	0	382	0	0.0	0	0	0	0	127.0	1	0	0	0	1.0	0.0	0.0	0.0	0.0	0.0	0	41088548759.1404	1	0	0	1336014000.0	0.0	0
    
  def GetSystemJumpPoints(self):
    jp_table = [list(x) for x in self.db.execute('''SELECT * from FCT_JumpPoint WHERE GameID = %d AND SystemID = %d;'''%(self.gameID, self.currentSystem))]
    JPs = {}
    index = 1
    for JP in jp_table:
      JP_ID = JP[0]
      JP_fromSystemID = JP[2]
      JP_toWP = JP[5]
      JP_explored = (0 if JP_toWP==0 else 1)
      JP_Gate = (0 if JP[8]==0 else 1)
      pos = (JP[6],JP[7])
      bearing = JP[4]
      JP_fromSystem = self.GetSystemName(JP_fromSystemID)
      if (JP_explored):
        JP_toSystemID = self.db.execute('''SELECT SystemID from FCT_JumpPoint WHERE GameID = %d AND WarpPointID = %d;'''%(self.gameID,JP_toWP)).fetchone()[0]
        JP_toSystem = self.GetSystemName(JP_toSystemID)
      else:
        JP_toSystemID = -1
        JP_toSystem = 'JP '+str(index)
        index+=1
      if (JP_fromSystem != 'Unknown'):
        JPs[JP_ID] = {'Destination': JP_toSystem, 'DestID': JP_toSystemID, 
                      'Explored':JP_explored, 'Gate':JP_Gate, 'Pos': pos, 'Bearing':bearing, 
                      'CurrentSystem':JP_fromSystem,'CurrentSystemID':JP_fromSystemID}
    return JPs


  def GetSurveyLocations(self, systemID):
    # FCT_RaceSurveyLocation - holds all surveyed surveylocations
    # RaceID	GameID	SystemID	LocationNumber
    #   418	    95	    8496	      15

    # FCT_RaceJumpPointSurvey - holds all Jumppoints weather discovered (charted) and explored or not
    # GameID	RaceID	WarpPointID	Explored	Charted	AlienUnits	Hide	MilitaryRestricted	IgnoreForDistance
    # 95      	418      	23417	0	0	0	0	0	0
    # 95      	418      	23418	1	1	0	0	0	0
    surveyLocations = {}
    # FCT_RaceSurveyLocation - holds all surveyed surveylocations
    # # RaceID	GameID	SystemID	LocationNumber
    #   418	    95	    8496	      15
    mySurveyedLocationsTable = [list(x) for x in self.db.execute('''SELECT LocationNumber from FCT_RaceSurveyLocation WHERE GameID = %d AND SystemID = %d AND RaceID = %d;'''%(self.gameID, systemID, self.myRaceID))]
    mySurveyedLocations = []
    for N in mySurveyedLocationsTable:
      mySurveyedLocations.append(N[0])

    # todo: check for single line returns
    surveyLocationTable = [list(x) for x in self.db.execute('''SELECT * from FCT_SurveyLocation WHERE GameID = %d AND SystemID = %d;'''%(self.gameID, systemID))]
    # FCT_SurveyLocation - holds all locations with their coordinates
    # SurveyLocationID	GameID	SystemID	LocationNumber	          Xcor             	Ycor
    #   244231           	90	   8144	        1	           -3.67381906146713e-07	-2000000000.0
    for location in surveyLocationTable:
      id = location[0]
      nr = location[3]
      pos = (location[4],location[5])
      surveyed = True if nr in mySurveyedLocations else False
      surveyLocations[id] = {'Number':nr, 'Pos':pos, 'Surveyed':surveyed}

    return surveyLocations


  def GetNewData(self):
    self.starSystems = self.GetSystems()
    self.currentSystemJumpPoints = self.GetSystemJumpPoints()
    self.surveyLocations = self.GetSurveyLocations(self.currentSystem)
    self.fleets = self.GetFleets()
    self.colonies = self.GetColonies()
    self.systemBodies = self.GetSystemBodies()
    self.reDraw = True
    self.reDraw_FleetInfoWindow = True
    self.reDraw_MapWindow = True


  def GetColonies(self):
    colonies = {}
    colonies_table = [list(x) for x in self.db.execute('''SELECT * from FCT_Population WHERE GameID = %d AND RaceID = %d ORDER BY Population DESC;'''%(self.gameID,self.myRaceID))]
    for colony in colonies_table:
        system_name = self.GetSystemName(colony[29])
        systemBodyID = colony[30]
        stockpile_sum = 0
        stockpile_minerals_sum = 0
        colonies[systemBodyID] = {'Name':colony[4],'Pop':round(colony[24],2), 'SystemID':colony[29],'System':system_name, 'ColonyCost':colony[17], 'Stockpile':{'Fuel':int(round(colony[13])),'Supplies':int(round(colony[18]))}}
        stockpile_sum = int(round(colony[13]) + round(colony[18]))
        for mineralID in Utils.MineralNames:
          amount = int(round(colony[34+mineralID-1],0))
          colonies[systemBodyID]['Stockpile'][Utils.MineralNames[mineralID]] = amount
          stockpile_minerals_sum += amount
        colonies[systemBodyID]['Stockpile']['Sum of Minerals'] = stockpile_minerals_sum
        colonies[systemBodyID]['Stockpile']['Sum'] = stockpile_sum

        colonies[systemBodyID]['Installations'] = {}
        industries_table = [list(x) for x in self.db.execute('''SELECT PlanetaryInstallationID, Amount from FCT_PopulationInstallations WHERE GameID = %d AND PopID = %d;'''%(self.gameID,colony[0]))]
        for installation in industries_table:
          id = installation[0]
          amount = installation[1]
          name = ''
          if (id in self.installations):
            name = self.installations[id]['Name']
          colonies[systemBodyID]['Installations'][id] = {'Name':name, 'Amount':amount}

    return colonies


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

    self.systemBodies = self.GetSystemBodies()
    self.starSystems = self.GetSystems()


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
      self.CleanUpInfoWindow(self.window_fleet_info_identifier)
      self.CleanUpInfoWindow(self.window_info_identifier)
      self.GetNewData()


  def Select_Fleet(self, id, parent):
    if (self.currentSystem in self.fleets):
      if (id in self.fleets[self.currentSystem]):
        #print(self.fleets[self.currentSystem][id])
        self.highlighted_fleet_ID = id
        self.highlighted_body_ID=-1
        self.reDraw = True
        #self.GetNewData()


  def Select_Body(self, id, parent):
    if (id in self.starSystems[self.currentSystem]['Stars']):
      #print(self.starSystems[self.currentSystem]['Stars'][id])
      self.highlighted_fleet_ID = -1
      self.highlighted_body_ID=id
      self.reDraw = True
    elif (id in self.systemBodies):
      #print(self.systemBodies[id])
      self.highlighted_fleet_ID = -1
      self.highlighted_body_ID=id
      self.reDraw = True


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


  def CleanUpInfoWindow(self, parent):
    if (parent == self.window_fleet_info_identifier):
      self.GUI_expanded_fleets = []
    elif (parent == self.window_info_identifier):
      self.GUI_expanded_fleets2 = []


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

    self.reDraw_InfoWindow = True


  def InitGases(self):
    gases = {}
    results = self.db.execute('''SELECT GasID, Name, Dangerous, DangerousLevel from DIM_Gases;''').fetchall()
    for result in results:
      gases[result[0]] = {'Name':result[1], 'DangerFactor':result[2], 'DangerousLevel':result[3]/1000}
    return gases


  def CalculateColonyCost(self, bodyID, currentTemp, atm, hydro, gravity, tidalMultiplier):
    tempFactor = 0
    breathFactor = 0
    dangerAtmFactor = 0
    atmFactor = 0
    waterFactor = 0
    
    # body data
    #currentTemp = body['Temperature'] # 630.880
    #atm = body['AtmosPressure'] #92.095
    #hydro = body['Hydrosphere']#0
    #oxygen atm and %
    breathAtm = 0
    breathAtmLevel = 0
    #gravity = body['Gravity']#.91


    # Species levels
    minTemp = -10
    maxTemp = 38
    breatheGas = 'Oxygen'
    breatheMinAtm = 0.1
    breatheMaxAtm = 0.3
    safeLevel = 30
    maxAtm = 4
    minGravity = 0.1
    maxGravity = 1.9
    
    if (gravity > maxGravity):
      return None

    # Gas Giants, Super Jovians and worlds with a gravity higher than species tolerance cannot be colonised and therefore have no colony cost. 

    # Temperature: If the temperature is outside of the species tolerance, the colony cost factor for temperature is equal to the number of degrees above or below the species tolerance divided by half the total species range. For example, if the species range is from 0C to 30C and the temperature is 75C, the colony cost factor would be 45 / 15 = 3.00. The colony cost factor for tide-locked planets is 20% of normal, so in the example given the colony cost factor would be reduced to 0.60.
    if (currentTemp > minTemp) and (currentTemp < maxTemp):
      tempFactor = 0
    else:
      speciesTempDelta = min(abs(minTemp-currentTemp), abs(maxTemp-currentTemp))
      tempFactor = speciesTempDelta / (maxTemp-minTemp) * 2 * tidalMultiplier
      

    # Hydrosphere Extent: If less than twenty percent of a body is covered with water (less than 20% Hydro Extent), the colony cost factor for hydro extent is (20 - Hydro Extent) / 10, which is a range from zero to 2.00.
    if (hydro >= 20):
      waterFactor = 0
    else:
      waterFactor = 2

    # Atmospheric Pressure: If the atmospheric pressure is above species tolerance, the colony cost factor for pressure is equal to pressure / species max pressure; with a minimum of 2.00. For example, if a species has a pressure tolerance of 4 atm and the pressure is 10 atm, the colony cost factor would be 2.50. If the pressure was 6 atm, the colony cost factor would be 2.00, as that is the minimum.
    atmFactor = max(2,atm/maxAtm) if (atm > maxAtm) else 0

    # Dangerous Gas: If a dangerous gas is present in the atmosphere and the concentration is above the danger level, the colony cost factor for dangerous gases will either be 2.00 or 3.00, depending on the gas. Different gases require different concentrations before becoming 'dangerous'. Halogens such as Chlorine, Bromine or Flourine are the most dangerous at 1 ppm, followed by Nitrogen Dioxide and Sulphur Dioxide at 5 ppm. Hydrogen Sulphide is 20 ppm, Carbon Monoxide and Ammonia are 50 ppm, Hydrogen, Methane (if an oxygen breather) and Oxygen (if a Methane breather) are at 500 ppm and Carbon Dioxide is at 5000 ppm (0.5% of atmosphere). Note that Carbon Dioxide was not classed as a dangerous gas in VB6 Aurora. These gases are not lethal at those concentrations but are dangerous enough that infrastructure would be required to avoid sustained exposure.
    bodyGases = self.db.execute('''SELECT AtmosGasID, AtmosGasAmount, GasAtm from FCT_AtmosphericGas WHERE GameID = %d AND SystemBodyID = %d;'''%(self.gameID, bodyID)).fetchall()
    # gases[results[0]] = {'Name':results[1], 'DangerFactor':results[2], 'DangerousLevel':results[3]/1000}
    dangerAtmFactor = 0
    for bodyGas in bodyGases:
      id = bodyGas[0]
      percentage = bodyGas[1]
      atm = bodyGas[2]

      if id in self.gases:
        if (self.gases[id]['DangerFactor'] > 0):
          if (atm > self.gases[id]['DangerousLevel']):
            dangerAtmFactor = max(self.gases[id]['DangerFactor'], dangerAtmFactor)
        if (self.gases[id]['Name'] == 'Oxygen'):
          breathAtm = atm
          breathAtmLevel = percentage

    # Breathable Gas: If the atmosphere does not have a sufficient amount of breathable gas, the colony cost factor for breathable gas is 2.00. If the gas is available in sufficient quantities but exceeds 30% of atmospheric pressure, the colony cost factor is also 2.00.
    if (breathAtm >= breatheMinAtm and breathAtm <= breatheMaxAtm and breathAtmLevel < safeLevel):
      breathFactor = 0
    else:
      breathFactor = 2

    cc = max([tempFactor, breathFactor, dangerAtmFactor, atmFactor, waterFactor])

    return cc


  def GetCCreduction(self):
    number = 0
    searchString = 'Colonization Cost Reduction'
    results = self.db.execute('''SELECT * from DIM_TechType;''').fetchall()
    techTypeID = -1
    for result in results:
      if (result[1] == searchString):
        techTypeID = result[0]
        break
    results = self.db.execute('''SELECT TechSystemID, Name from FCT_TechSystem WHERE TechTypeID = %d;'''%(techTypeID)).fetchall()
    for result in results:
      researchedTechs = self.db.execute('''SELECT * from FCT_RaceTech WHERE GameID = %d AND RaceID = %d AND TechID = %d;'''%(self.gameID, self.myRaceID, result[0])).fetchall()
      if (researchedTechs):
        percentage = result[1].replace(searchString,'')
        try:
          number = float(percentage[:-1])/100.
        except:
          number = 0
      else:
        break
    return number