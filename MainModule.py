import pygame
import sqlite3
import logger as lg
import Utils
import math
import random
import Clickable
import GUI

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
    self.showFleetTraces = True
    self.showPlanets = True
    self.showMoons = True
    self.showDwarfPlanets = True
    self.showComets = True
    self.showAsteroids = False

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
    self.color_Fleet = Utils.CYAN
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

    self.window_info_identifier = 'Fleet Info Window'
    self.window_info_size = (300,600)
    self.window_map_size = (self.window_info_size[0],self.window_info_size[0])

    self.window_info_anchor = (5,self.height-self.window_map_size[1]-self.window_info_size[1]-2*5)#(self.width-self.window_info_size[0]-5,self.height-self.window_map_size[1]-self.window_info_size[1]-2*5)
    self.window_info = pygame.Surface(self.window_info_size, pygame.SRCALPHA,32)
    self.window_info_rect = pygame.Rect(self.window_info_anchor, self.window_info_size)
    self.window_info.set_colorkey(Utils.GREENSCREEN)
    self.reDraw_InfoWindow = True;
    self.window_info_scoll_pos = 0
    self.highlighted_fleet_ID = -1


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
    self.InitGUI()

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
      self.currentSystem = 8497 # Alpha Centauri , knownsystem 1, component2ID 87, c2orbit 23
      #self.currentSystem = 8499 # Lalande
      #self.currentSystem = 8500
      #self.currentSystem = 8496 # EE (with Black Hole)
      self.stellarTypes = self.GetStellarTypes()
      self.GetNewData()

  def InitGUI(self):
    idGUI = 1
    x = self.GUI_Bottom_Anchor[0]
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'ShowBodies'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl)
    showBodiesGUI = self.GUI_Elements[idGUI]

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Planets'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showBodiesGUI.GetID(), enabled = self.showPlanets)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Moons'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showBodiesGUI.GetID(), enabled = self.showMoons)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Asteroids'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, parent=showBodiesGUI.GetID(), enabled = self.showAsteroids)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Comets'
    gui_cl = self.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, parent=showBodiesGUI.GetID(), enabled = self.showComets)
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



  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      if (self.Events):
        self.Events.ClearClickables(exclude=self.GUI_identifier)
      self.reDraw_InfoWindow = True
      self.reDraw_MapWindow = True
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)

      reblit |= self.DrawSystem()

    reblit |= self.DrawMiniMap()

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

    #self.DrawInfoWindow()

    #self.DrawMiniMap()

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
    print(dt1,dt2,dt3,dt4)
    return True


  def DrawSystemBodies(self):
    if self.currentSystem not in self.starSystems:
      return
    system = self.starSystems[self.currentSystem]
    
    ###################
    # Draw Stars
    ###################
    for starID in system['Stars']:
      star = system['Stars'][starID]
      screen_star_pos = self.WorldPos2ScreenPos(star['Pos'])
      star_name = star['Name'] + ' ' + star['Suffix']
      # draw star
      
      # draw orbit
      ############
      screen_parent_pos = self.WorldPos2ScreenPos(star['ParentPos'])
      if (self.showOrbits_Stars):
        orbitRadiusOnScreen = star['OrbitDistance']*self.systemScale
        if (orbitRadiusOnScreen > 0):
          Utils.DrawEllipticalOrbit(self.surface, self.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, star['Eccentricity'], star['EccentricityAngle'],star['Bearing'], 10)
          #if (orbitRadiusOnScreen < self.width):
          #  pygame.draw.circle(self.surface, self.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, 1)
          #else:
          #  if Utils.RectIntersectsRadius((0,0,self.width, self.height), screen_parent_pos, orbitRadiusOnScreen):
          #    min_angle, max_angle = Utils.GetAnglesEncompassingRectangle((0,0,self.width, self.height), screen_parent_pos)
          #    Utils.DrawArc(self.surface, self.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, min_angle, max_angle, 1)
      
      # draw Star, either as image or as simple filled circle
      ####################
      radius = (Utils.AU_INV*self.systemScale)*star['Radius']*self.radius_Sun
      star_color = self.stellarTypes[star['StellarTypeID']]['RGB']
      if (radius < self.minPixelSize_Star):
        radius = self.minPixelSize_Star

      if (star['Image'] is not None):
        if (screen_star_pos[0]-radius < self.width and screen_star_pos[0]+radius > 0 and 
            screen_star_pos[1]-radius < self.height and screen_star_pos[1]+radius > 0 ):
          scale = (radius*2,radius*2)
          if (scale[0] > 2*self.width):
            #todo: fix bug where the scaled surface moves when zooming in too much
            scale = (2*self.width,2*self.width)
          scaledSurface = pygame.transform.smoothscale(star['Image'],scale)
          image_offset = Utils.SubTuples(screen_star_pos,scaledSurface.get_rect().center)
          self.surface.blit(scaledSurface,image_offset)
      else:
        if (not star['Black Hole']):
          pygame.draw.circle(self.surface,star_color,screen_star_pos,radius,Utils.FILLED)
        else:
          pygame.draw.circle(self.surface,Utils.RED,screen_star_pos,radius,5)
      bb = (screen_star_pos[0]-radius,screen_star_pos[1]-radius,2*radius,2*radius)
      if (self.CheckClickableNotBehindGUI(bb)):
        self.MakeClickable(star_name, bb, left_click_call_back = self.Select_Body, par=starID)

      # Label Star
      ################
      labelPos = Utils.AddTuples(screen_star_pos, (0,radius))
      Utils.DrawText2Surface(self.surface,star_name,labelPos,14,self.color_Label_Star)

    # Draw other bodies
    for bodyID in self.systemBodies:
      body = self.systemBodies[bodyID]
      #print(body['ID'],body['Name'])

      body_draw_cond, draw_color_body, body_min_size, body_min_dist = self.GetDrawConditions('Body', body['Class'], body['Type'])
      if (body_draw_cond):
        screen_body_pos = self.WorldPos2ScreenPos(body['Pos'])
        radius_on_screen = Utils.AU_INV * self.systemScale * body['RadiusBody']
        if (radius_on_screen < body_min_size):
          radius_on_screen = body_min_size

        orbit_draw_cond, draw_color_orbit, void, min_orbit = self.GetDrawConditions('Orbit', body['Class'], body['Type'])
        orbitOnScreen = body['Orbit']*self.systemScale

        if (orbit_draw_cond) and (orbitOnScreen > body_min_dist):
          E = body['Eccentricity']
          parentID = body['ParentID']

          if parentID in system['Stars']:
            screen_parent_pos = self.WorldPos2ScreenPos(system['Stars'][parentID]['Pos'])
          elif parentID in self.systemBodies:
            screen_parent_pos = self.WorldPos2ScreenPos(self.systemBodies[parentID]['Pos'])
          else:
            screen_parent_pos = self.WorldPos2ScreenPos((0,0))
          Utils.DrawEllipticalOrbit(self.surface, draw_color_orbit, screen_parent_pos, orbitOnScreen, E, body['EccentricityAngle'],body['Bearing'], min_orbit)
          ## draw orbit
          #if (E > 0):
          #  a = orbitOnScreen
          #  b = a * math.sqrt(1-E*E)
          #  #b = body['Orbit'] * self.systemScale
          #  #a = b*1/math.sqrt(1-E*E)
          #  c = E * a
          #  N = 60
          #  if (E > 0.9):
          #    N = 240
          #  x_offset = c * math.cos(body['EccentricityAngle']*Utils.DEGREES_TO_RADIANS)
          #  y_offset = c * math.sin(body['EccentricityAngle']*Utils.DEGREES_TO_RADIANS)
          #  offsetPos = Utils.AddTuples(screen_parent_pos, (x_offset,y_offset))
          #  #Utils.draw_ellipse_angle(self.surface,self.color_Orbit,(offsetPos,(2*a,2*b)),body['EccentricityAngle'],1)
          #  # 13 FPS
          #  #Utils.draw_ellipse_angle(self.surface,self.color_Orbit,(offsetPos,(2*a,2*b)),body['EccentricityAngle'],1)
          #  # 19 FPS @360 segments, 30 FPS at 60 segments
          #  Utils.MyDrawEllipse(self.surface, draw_color_orbit, offsetPos[0],offsetPos[1], a, b,body['EccentricityAngle'],body['Bearing'], N)
          #else:
          #  if (orbitOnScreen < 50000 and orbitOnScreen > min_orbit):
          #    pygame.draw.circle(self.surface,draw_color_orbit,screen_parent_pos,orbitOnScreen,1)
        
        # check if we want to draw the object
        ################
        if (screen_body_pos[0] > -50 and screen_body_pos[1] > -50 and screen_body_pos[0] < self.width+50 and screen_body_pos[1] < self.height+50 ):
          pass
        else:
          body_draw_cond = False  
        if (body_draw_cond) and (orbitOnScreen > body_min_dist):
          # draw body
          if (body['Image'] is not None):
            if (screen_body_pos[0]-radius_on_screen < self.width and screen_body_pos[0]+radius_on_screen > 0 and 
                screen_body_pos[1]-radius_on_screen < self.height and screen_body_pos[1]+radius_on_screen > 0 ):
              scale = (radius_on_screen*2,radius_on_screen*2)
              if (scale[0] > 2*self.width):
                #todo: fix bug where the scaled surface moves when zooming in too much
                scale = (2*self.width,2*self.width)
              scaledSurface = pygame.transform.smoothscale(body['Image'],scale)
              image_offset = Utils.SubTuples(screen_body_pos,scaledSurface.get_rect().center)
              self.surface.blit(scaledSurface,image_offset)
          else:
            pygame.draw.circle(self.surface,draw_color_body,screen_body_pos,radius_on_screen,Utils.FILLED)
          
          
          # Make object clickable
          bb = (screen_body_pos[0]-radius_on_screen,screen_body_pos[1]-radius_on_screen,2*radius_on_screen,2*radius_on_screen)
          if (self.CheckClickableNotBehindGUI(bb)):
            self.MakeClickable(body['Name'], bb, left_click_call_back = self.Select_Body, par=bodyID)

          # Check if we want to draw the label
          draw_cond, draw_color_label, void, min_dist = self.GetDrawConditions('Label', body['Class'], body['Type'])
          if (draw_cond) and (orbitOnScreen > min_dist):
            labelPos = Utils.AddTuples(screen_body_pos, (0,radius_on_screen))
            Utils.DrawText2Surface(self.surface,body['Name'],labelPos,14,draw_color_label)


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
            if (self.showFleetTraces):
              prev_pos = self.WorldPos2ScreenPos(fleet['Position_prev'])
              pygame.draw.line(self.surface, self.color_Fleet, prev_pos, pos,1)
            bb = Utils.DrawTriangle(self.surface,pos ,self.color_Fleet, fleet['Heading'])
            if (self.CheckClickableNotBehindGUI(bb)):
              self.MakeClickable(fleet['Name'], bb, left_click_call_back = self.Select_Fleet, par=fleetID)
            if (self.highlighted_fleet_ID == fleetID):
              pygame.draw.rect(self.surface, self.color_Fleet,(bb[0]-2,bb[1]-2,bb[2]+4,bb[3]+4),2)
            #pygame.draw.circle(self.surface,self.color_Fleet,(pos_x,pos_y),5,Utils.FILLED)
            Utils.DrawText2Surface(self.surface,fleet['Name'],(pos[0]+10,pos[1]-6),12,self.color_Fleet)


  def DrawInfoWindow(self):
    if (self.reDraw_InfoWindow):
      self.Events.ClearClickables(parent=self.window_info_identifier)
      line_height = 20
      pad_x = pad_y = 5
      lineNr = self.window_info_scoll_pos
      self.window_info.fill(Utils.SUPER_DARK_GRAY)
      #print(self.window_info_scoll_pos)
      if (self.currentSystem in self.fleets):
        for fleetID in self.fleets[self.currentSystem]:
          fleet = self.fleets[self.currentSystem][fleetID]
          if (fleet['Ships'] != [] or self.showEmptyFleets):
            color = Utils.WHITE
            if (self.highlighted_fleet_ID == fleetID):
              color = Utils.CYAN
            label_pos = (pad_x,(pad_y+lineNr*line_height))
            if (fleet['Ships'] != []):
              expRect = Utils.DrawExpander(self.window_info, (label_pos[0],label_pos[1]+3), 15, color)
              self.MakeClickable(fleet['Name'], expRect, left_click_call_back = self.ExpandFleet, par=fleetID, parent = self.window_info_identifier, anchor=self.window_info_anchor)
              label_pos = (expRect[2]+10,label_pos[1])
            label_pos, label_size = Utils.DrawText2Surface(self.window_info,fleet['Name']+ ' - ',label_pos,15,color)
            if (label_pos):
              self.MakeClickable(fleet['Name'], (label_pos[0],label_pos[1], label_size[0],label_size[1]), left_click_call_back = self.Select_Fleet, par=fleetID, parent = self.window_info_identifier, anchor=self.window_info_anchor)
            if (fleet['Speed'] > 1) and label_pos:
              speed = str(int(fleet['Speed'])) + 'km/s'

              speed_label_pos, speed_label_size = Utils.DrawText2Surface(self.window_info,speed,(label_pos[0]+label_size[0],
                                                                                                label_pos[1]),15,color)
              icon_pos = (speed_label_pos[0]+speed_label_size[0], speed_label_pos[1])
              p = 0
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
            if (fleetID in self.GUI_expanded_fleets):
              shipClasses = {}
              for ship in fleet['Ships']:
                if (ship['ClassName'] not in shipClasses):
                  shipClasses[ship['ClassName']] = 1
                else:
                  shipClasses[ship['ClassName']] += 1
              for shipClass in shipClasses:
                label_pos = (expRect[2]+10,(pad_y+lineNr*line_height))
                label_pos, label_size = Utils.DrawText2Surface(self.window_info,'%dx%s'%(shipClasses[ship['ClassName']],shipClass),label_pos,15,color)
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
        system['Stars'] = stars
        systems[systemID] = system
    return systems


  def GetStellarTypes(self):
    stellarTypes = {}

    results = self.db.execute('''SELECT StellarTypeID, SpectralClass, SpectralNumber, SizeText, SizeID, Mass, Temperature, Radius, Red, Green, Blue from DIM_StellarType;''').fetchall()
    
    for stellarType in results:
      #stellarType = results[stellarTypeID]
      stellarTypeID = stellarType[0]
      stellarTypes[stellarTypeID] = { 'SpectralClass':stellarType[1]
                                     ,'SpectralNumber':stellarType[2]
                                     ,'SizeText':stellarType[3]
                                     ,'SizeID':stellarType[4]
                                     ,'Mass':stellarType[5]
                                     ,'Temperature':stellarType[6]
                                     ,'Radius':stellarType[7]
                                     ,'RGB':(stellarType[8],stellarType[9],stellarType[10])
                                    }
        
    return stellarTypes


  def GetSystemBodies(self):
    systemBodies = {}
    body_table = [list(x) for x in self.db.execute('''SELECT SystemBodyID, Name, PlanetNumber, OrbitNumber, OrbitalDistance, ParentBodyID, Radius, Bearing, Xcor, Ycor, Eccentricity, EccentricityDirection, BodyClass, BodyTypeID, SurfaceTemp, AtmosPress, HydroExt from FCT_SystemBody WHERE GameID = %d AND SystemID = %d;'''%(self.gameID,self.currentSystem))]
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

      systemBodies[body[0]]={'ID':body[0],'Name':body_name, 'Type':bodyType, 'Class':bodyClass, 'Orbit':orbit, 'ParentID':body[5], 'RadiusBody':body[6], 'Bearing':body[7],
                            'Eccentricity':body[10],'EccentricityAngle':body[11], 'Pos':(body[8], body[9]), 'Image':image}
    return systemBodies


  def GetDrawConditions(self, thing2Draw, bodyClass, bodyType):
    draw = False
    color = (0,0,0)
    min_size = 5
    min_dist = 5
    if (thing2Draw == 'Body'):
      if (bodyClass == 'Moon' and self.showMoons):
        draw = True
        color = self.color_Moon
        min_size = self.minPixelSize_Moon
        min_dist = 10
      elif (bodyClass  == 'Comet' and self.showComets):
        draw = True
        color = self.color_Comet
        min_size = self.minPixelSize_Small
        min_dist = 10
      elif (bodyClass  == 'Asteroid' and self.showAsteroids):
        draw = True
        color = self.color_Asteroid
        min_size = self.minPixelSize_Small
        min_dist = 10
      elif (bodyType == 'Planet Small' and self.showDwarfPlanets):
        draw = True
        color = self.color_DwarfPlanet
        min_size = self.minPixelSize_Planet
        min_dist = 10
      elif (bodyClass == 'Planet' and self.showPlanets and bodyType != 'Planet Small' ):
        draw = True
        color = self.color_Planet
        min_size = self.minPixelSize_Planet
        min_dist = 10
    elif (thing2Draw == 'Orbit'):
      if (bodyClass == 'Moon' and self.showOrbits_Moons):
        draw = True
        color = self.color_Orbit_Moon
        min_dist = 10
      elif (bodyClass  == 'Comet' and self.showOrbits_Comets):
        draw = True
        color = self.color_Orbit_Comet
        min_dist = 10
      elif (bodyClass  == 'Asteroid' and self.showOrbits_Asteroids):
        draw = True
        color = self.color_Orbit_Asteroid
        min_dist = 10
      elif (bodyType == 'Planet Small' and self.showOrbits_DwarfPlanets):
        draw = True
        color = self.color_Orbit_DwarfPlanet
        min_dist = 10
      elif (bodyClass == 'Planet' and self.showOrbits_Planets and bodyType != 'Planet Small' ):
        draw = True
        color = self.color_Orbit_Planet
        min_dist = 10
    elif (thing2Draw == 'Label'):
      if (bodyClass == 'Moon' and self.showLabels_Moons):
        draw = True
        color = self.color_Label_Moon
        min_dist = 50
      elif (bodyClass  == 'Comet' and self.showLabels_Comets):
        draw = True
        color = self.color_Label_Comet
        min_dist = 200
      elif (bodyClass  == 'Asteroid' and self.showLabels_Asteroids):
        draw = True
        color = self.color_Label_Asteroid
        min_dist = 200
      elif (bodyType == 'Planet Small' and self.showLabels_DwarfPlanets):
        draw = True
        color = self.color_Label_DwarfPlanet
        min_dist = 5
      elif (bodyClass == 'Planet' and self.showLabels_Planets and bodyType != 'Planet Small' ):
        draw = True
        color = self.color_Label_Planet
        min_dist = 5
    return draw, color, min_size, min_dist


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
    self.systemBodies = self.GetSystemBodies()
    self.reDraw = True
    self.reDraw_InfoWindow = True
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


  def Follow_Jumppoint(self, id):
    if (id in self.starSystems):
      self.currentSystem = id
      self.window_info_scoll_pos = 0
      self.GetNewData()
      self.CleanUpInfoWindow()


  def Select_Fleet(self, id):
    if (self.currentSystem in self.fleets):
      if (id in self.fleets[self.currentSystem]):
        print(self.fleets[self.currentSystem][id])
        self.highlighted_fleet_ID = id
        self.GetNewData()


  def Select_Body(self, id):
    if (id in self.starSystems[self.currentSystem]['Stars']):
      # todo highlight body
      print(self.starSystems[self.currentSystem]['Stars'][id])
      self.highlighted_fleet_ID = -1
      self.GetNewData()
    elif (id in self.systemBodies):
      # todo highlight body
      print(self.systemBodies[id])
      self.highlighted_fleet_ID = -1
      self.GetNewData()


  def ToggleGUI(self, id):
    if (id in self.GUI_Elements):
      self.reDraw = True
      element = self.GUI_Elements[id]
      print('Click '+element.name)
      if (element.parent):
        element.enabled = not element.enabled
        self.ToggleGUI_Element_ByName(element.name)
        #element.clickable.enabled = not element.clickable.enabled
      else:
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
      self.showPlanets = not self.showPlanets
    elif (name == 'Show Moons'):
      self.showMoons = not self.showMoons
    elif (name == 'Show Comets'):
      self.showComets = not self.showComets
    elif (name == 'Show Asteroids'):
      self.showAsteroids = not self.showAsteroids
    elif (name == 'Show Planet Orbits'):
      self.showOrbits_Planets = not self.showOrbits_Planets
    elif (name == 'Show Moon Orbits'):
      self.showOrbits_Moons = not self.showOrbits_Moons
    elif (name == 'Show Comet Orbits'):
      self.showOrbits_Comets = not self.showOrbits_Comets
    elif (name == 'Show Asteroid Orbits'):
      self.showOrbits_Asteroids = not self.showOrbits_Asteroids


  def CleanUpInfoWindow(self):
    self.GUI_expanded_fleets = []


  def ExpandFleet(self, id):
    if (id in self.fleets[self.currentSystem]):
      if (id in self.GUI_expanded_fleets):
        self.GUI_expanded_fleets.remove(id)
      else:
        self.GUI_expanded_fleets.append(id)
      self.reDraw_InfoWindow = True

