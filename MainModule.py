import pygame
import sqlite3
import logger as lg
import Utils
import math
import random

class Game():
  def __init__(self, size = (1800,1000), name = 'AuroraGUI'):
    self.logger = lg.Logger(logfile= 'logMain.txt', module='MainModule.py', log_level = 1)
    self.name = name
    self.width = size[0]
    self.height = size[1]
    pygame.display.set_caption(name)
    self.screen = pygame.display.set_mode((self.width,self.height))
    self.surface = pygame.Surface((self.width,self.height), pygame.SRCALPHA,32)
    self.surface.set_colorkey(Utils.GREENSCREEN)
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
    self.reDraw = True;

    # Options
    self.bg_color = Utils.BLACK
    self.showEmptyFleets = False
    self.showStationaryFleets = False
    self.showUnsurveyedLocations = True
    self.showSurveyedLocations = False
    self.showFleetTraces = True
    self.showOrbits_Planets = True
    self.showOrbits_DwarfPlanets = True
    self.showOrbits_Moons = True
    self.showOrbits_Comets = True
    self.showOrbits_Asteroids = False
    self.showOrbits_Stars = True
    self.showPlanets = True
    self.showMoons = True
    self.showDwarfPlanets = True
    self.showComets = True
    self.showAsteroids = False
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
    self.color_Orbit_Asteroid = Utils.DARK_GRAY
    self.color_Orbit_Comet = Utils.DARK_GRAY
    self.images_Body = {}

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
      #self.currentSystem = 8497 # Alpha Centauri
      #self.currentSystem = 8499
      #self.currentSystem = 8496 # EE (with Black Hole)
      self.stellarTypes = self.GetStellarTypes()
      self.GetNewData()

  def Draw(self):
    # clear screen
    if (self.reDraw):
      self.surface.fill(self.bg_color)

      self.DrawSystem()

      self.DrawMiniMap()

      self.DrawInfoWindow()

      self.DrawGUI()

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


  def DrawSystemBodies(self):
    if self.currentSystem not in self.starSystems:
      return
    system = self.starSystems[self.currentSystem]

    # Draw Stars
    for starID in system['Stars']:
      star = system['Stars'][starID]
      screen_star_pos = self.WorldPos2ScreenPos(star['Pos'])
      # draw star
      r = star['Radius']
      radius = (Utils.AU_INV*self.systemScale)*r*self.radius_Sun
      star_color = self.stellarTypes[star['StellarTypeID']]['RGB']
      if (radius < self.minPixelSize_Star):
        radius = self.minPixelSize_Star

      # draw Star
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

      #pygame.draw.rect(self.surface,Utils.RED, (screen_star_pos,(1,1)), 0)
      # Label Star
      labelPos = Utils.AddTuples(screen_star_pos, (0,radius))
      Utils.DrawText2Surface(self.surface,system['Name'],labelPos,14,self.color_Label_Star)
      screen_parent_pos = self.WorldPos2ScreenPos(star['ParentPos'])
      # draw orbit
      if (self.showOrbits_Stars):
        pygame.draw.circle(self.surface,self.color_Orbit_Star,screen_parent_pos,star['OrbitDistance']*self.systemScale,1)
    
    # Draw other bodies
    for bodyID in self.systemBodies:
      body = self.systemBodies[bodyID]
      #print(body['ID'],body['Name'])

      draw_cond, draw_color_body, body_min_size, body_min_dist = self.GetDrawConditions('Body', body['Class'], body['Type'])
      if (draw_cond):
        screen_body_pos = self.WorldPos2ScreenPos(body['Pos'])
        radius_on_screen = Utils.AU_INV * self.systemScale * body['RadiusBody']
        if (radius_on_screen < body_min_size):
          radius_on_screen = body_min_size

        if (screen_body_pos[0] > -50 and screen_body_pos[1] > -50 and screen_body_pos[0] < self.width+50 and screen_body_pos[1] < self.height+50 ):
          draw_cond, draw_color_orbit, void, min_orbit = self.GetDrawConditions('Orbit', body['Class'], body['Type'])
          orbitOnScreen = body['Orbit']*self.systemScale

          if (draw_cond) and (orbitOnScreen > body_min_dist):
            E = body['Eccentricity']
            parentID = body['ParentID']

            if parentID in system['Stars']:
              screen_parent_pos = self.WorldPos2ScreenPos(system['Stars'][parentID]['Pos'])
            elif parentID in self.systemBodies:
              screen_parent_pos = self.WorldPos2ScreenPos(self.systemBodies[parentID]['Pos'])
            else:
              screen_parent_pos = self.WorldPos2ScreenPos((0,0))
            # draw orbit
            if (E > 0):
              a = orbitOnScreen
              b = a * math.sqrt(1-E*E)
              #b = body['Orbit'] * self.systemScale
              #a = b*1/math.sqrt(1-E*E)
              c = E * a
              x_offset = c * math.cos(body['EccentricityAngle']*Utils.DEGREES_TO_RADIANS)
              y_offset = c * math.sin(body['EccentricityAngle']*Utils.DEGREES_TO_RADIANS)
              offsetPos = Utils.AddTuples(screen_parent_pos, (x_offset,y_offset))
              #Utils.draw_ellipse_angle(self.surface,self.color_Orbit,(offsetPos,(2*a,2*b)),body['EccentricityAngle'],1)
              # 13 FPS
              #Utils.draw_ellipse_angle(self.surface,self.color_Orbit,(offsetPos,(2*a,2*b)),body['EccentricityAngle'],1)
              # 19 FPS @360 segments, 30 FPS at 60 segments
              Utils.MyDrawEllipse(self.surface, draw_color_orbit, offsetPos[0],offsetPos[1], a, b,body['EccentricityAngle'],body['Bearing'])
            else:
              if (orbitOnScreen < 50000 and orbitOnScreen > min_orbit):
                pygame.draw.circle(self.surface,draw_color_orbit,screen_parent_pos,orbitOnScreen,1)
          
          if (orbitOnScreen > body_min_dist):
            # draw body

            if (body['Image'] is not None):
              
              if (screen_body_pos[0]-radius < self.width and screen_body_pos[0]+radius > 0 and 
                  screen_body_pos[1]-radius < self.height and screen_body_pos[1]+radius > 0 ):
                scale = (radius_on_screen*2,radius_on_screen*2)
                if (scale[0] > 2*self.width):
                  #todo: fix bug where the scaled surface moves when zooming in too much
                  scale = (2*self.width,2*self.width)
                scaledSurface = pygame.transform.smoothscale(body['Image'],scale)
                image_offset = Utils.SubTuples(screen_body_pos,scaledSurface.get_rect().center)
                self.surface.blit(scaledSurface,image_offset)
            else:
              pygame.draw.circle(self.surface,draw_color_body,screen_body_pos,radius_on_screen,Utils.FILLED)

            # Check if we want to draw the label
            draw_cond, draw_color_label, void, min_dist = self.GetDrawConditions('Label', body['Class'], body['Type'])
            if (draw_cond) and (orbitOnScreen > min_dist):
              labelPos = Utils.AddTuples(screen_body_pos, (0,radius_on_screen))
              Utils.DrawText2Surface(self.surface,body['Name'],labelPos,14,draw_color_label)


  def DrawSystemJumpPoints(self):
    for JP_ID in self.currentSystemJumpPoints:
      JP = self.currentSystemJumpPoints[JP_ID]
      screen_pos = self.WorldPos2ScreenPos(JP['Pos'])
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
        if (fleet['Ships'] != [] or self.showEmptyFleets):
          if (fleet['Speed'] > 1 or self.showStationaryFleets):
            pos = self.WorldPos2ScreenPos(fleet['Position'])
            if (self.showFleetTraces):
              prev_pos = self.WorldPos2ScreenPos(fleet['Position_prev'])
              pygame.draw.line(self.surface, self.color_Fleet, prev_pos, pos,1)
            Utils.DrawTriangle(self.surface,pos ,self.color_Fleet, fleet['Heading'])
          
            #pygame.draw.circle(self.surface,self.color_Fleet,(pos_x,pos_y),5,Utils.FILLED)
            Utils.DrawText2Surface(self.surface,fleet['Name'],(pos[0]+10,pos[1]-6),12,self.color_Fleet)


  def DrawMiniMap(self):
    pass


  def DrawInfoWindow(self):
    pass


  def DrawGUI(self):
    pass


  def GetHomeSystemID(self):
    system_number = self.db.execute('''SELECT systemId from FCT_System WHERE GameID = %d AND SystemNumber = 0;'''%(self.gameID)).fetchone()[0]
        
    return system_number


  def GetSystemName(self, systemID):
    system_number = self.db.execute('''SELECT SystemNumber from FCT_System WHERE GameID = %d AND systemId = %d;'''%(self.gameID,systemID)).fetchone()[0]
    if (system_number > -1):
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
        system['Name'] = known_system[1]
        system['Stars'] = None
        stars_table = self.db.execute('''SELECT * from FCT_Star WHERE GameID = %d AND SystemID = %d;'''%(self.gameID,systemID))
        stars = {}
        component2ID = {}
        for star in stars_table:
          ID = star[0]
          stars[ID] = {}
          stars[ID]['Component'] = star[8]
          stars[ID]['StellarTypeID']=star[3]
          stars[ID]['Radius']=self.stellarTypes[stars[ID]['StellarTypeID']]['Radius']
          stars[ID]['Black Hole']=False
          spectralClass = self.stellarTypes[stars[ID]['StellarTypeID']]['SpectralClass']
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
          stars[ID]['Pos'] = (star[6],star[7])
          stars[ID]['Image'] = None
          if (len(self.images_Body) > 0):
            if (spectralClass in self.images_Body['Stars']):
              stars[ID]['Image'] = self.images_Body['Stars'][spectralClass]
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
    body_table = [list(x) for x in self.db.execute('''SELECT SystemBodyID, Name, OrbitalDistance, ParentBodyID, Radius, Bearing, Xcor, Ycor, Eccentricity, EccentricityDirection, BodyClass, BodyTypeID, SurfaceTemp, AtmosPress, HydroExt from FCT_SystemBody WHERE GameID = %d AND SystemID = %d;'''%(self.gameID,self.currentSystem))]
    for body in body_table:
      body_name = body[1]
      orbit = body[2] 
      a = body[2]
      r = body[4]
      d = body[2]
      angle = body[5]
      body_pos = (body[6], body[7])
      angle2 = body[9]
      E = body[8]
      bodyType = '?'
      bodyClass = '?'
      temp = body[12]-273
      atm = body[13]
      hydro = body[14]
      if (body[11] in Utils.BodyTypes):
        bodyType = Utils.BodyTypes[body[11]]
      if (body[10] in Utils.BodyClasses):
        bodyClass = Utils.BodyClasses[body[10]]
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
            if (bodyType == 'Planet Gas Giant' or 'Planet Super Jovian'):
              numImages = len(self.images_Body['Gas Giants'])
              selectedImage = random.randint(0,numImages-1)
              image = self.images_Body['Gas Giants'][selectedImage]
            elif (bodyType == 'Planet Small' or 'Moon Small'):
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

      systemBodies[body[0]]={'ID':body[0],'Name':body[1], 'Type':bodyType, 'Class':bodyClass, 'Orbit':orbit, 'ParentID':body[3], 'RadiusBody':body[4], 'Bearing':body[5],
                            'Eccentricity':body[8],'EccentricityAngle':body[9], 'Pos':(body[6], body[7]), 'Image':image}
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
      elif (bodyClass  == 'Comets' and self.showComets):
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
      elif (bodyClass  == 'Comets' and self.showOrbits_Comets):
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
      elif (bodyClass  == 'Comets' and self.showLabels_Comets):
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
      ships_table = [list(x) for x in self.db.execute('''SELECT * from FCT_Ship WHERE GameID = %d AND FleetID = %d;'''%(self.gameID,fleetId))]
      fleets[systemID][fleetId]['Ships'] = []
      for ship in ships_table:
        fleets[systemID][fleetId]['Ships'].append(ship[3])

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