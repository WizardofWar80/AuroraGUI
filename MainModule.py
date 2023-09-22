import pygame
import sqlite3
import logger as lg
import Utils
import math

class Game():
  def __init__(self, size = (1800,1000), name = 'AuroraGUI'):
    self.logger = lg.Logger(logfile= 'logMain.txt', module='MainModule.py', log_level = 1)
    self.name = name
    self.bg_color = Utils.BLACK
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
    self.systemScale = 50
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

    # Options
    self.showEmptyFleets = False
    self.showStationaryFleets = False
    self.showUnsurveyedLocations = True
    self.showSurveyedLocations = False
    self.showFleetTraces = True
    self.showOrbits_Planets = True
    self.showOrbits_Stars = True
    
    # Colorscheme
    self.color_JP = Utils.ORANGE
    self.color_Jumpgate = Utils.ORANGE
    self.color_SurveyedLoc = Utils.TEAL
    self.color_UnsurveyedLoc = Utils.BLUE
    self.color_Fleet = Utils.CYAN
    self.color_Planet = Utils.GREEN
    self.color_PlanetLabel = Utils.WHITE
    self.color_Star = Utils.YELLOW
    self.color_Star_Label = Utils.WHITE
    self.color_Orbit = Utils.WHITE

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

      self.starSystems = self.GetSystems()
      self.currentSystemJumpPoints = self.GetSystemJumpPoints()
      self.surveyLocations = self.GetSurveyLocations(self.currentSystem)
      self.fleets = self.GetFleets()
      self.systemBodies = self.GetSystemBodies()


  def Draw(self):
    # clear screen
    self.surface.fill(self.bg_color)

    # draw mouse position and scale
    Utils.DrawTextAtPos(self.surface,'(%d,%d) Scale: %3.1f'%(self.mousePos[0], self.mousePos[1], self.systemScale),(5,5),18,Utils.WHITE)
    Utils.DrawTextAtPos(self.surface,'(%d,%d)'%(self.mouseDragged[0], self.mouseDragged[1]),(5,25),18,Utils.WHITE)
    
    self.DrawSystem()

    self.DrawMiniMap()

    self.DrawInfoWindow()

    self.DrawGUI()
    
    self.counter_FPS += 1

    currentTimestamp = pygame.time.get_ticks()
    deltaTime = currentTimestamp - self.timestampLastSecond
    if (deltaTime >= 1000):
      #self.FPS = 1000*self.counter_FPS / deltaTime
      self.FPS = self.counter_FPS 
      self.counter_FPS = 0
      self.timestampLastSecond = currentTimestamp
      print(self.FPS)
    
    Utils.DrawTextAtPos(self.surface,'%d FPS'%(self.FPS),(5,50),18,Utils.WHITE)
    
    self.screen.blit(self.surface,(0,0))
    pygame.display.update()
    
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
    print(dt1, dt2, dt3, dt4)


  def DrawSystemBodies(self):
    if self.currentSystem not in self.starSystems:
      return
    system = self.starSystems[self.currentSystem]

    #Draw system bodies
    for starID in system['Stars']:
      star = system['Stars'][starID]
      screen_star_pos = self.WorldPos2ScreenPos(star['Pos'])
      # draw star
      r = 1
      radius = (Utils.AU_INV*self.systemScale)*r*self.radius_Sun
      if (radius < self.minPixelSize_Star):
        radius = self.minPixelSize_Star
      pygame.draw.circle(self.surface,self.color_Star,screen_star_pos,radius,Utils.FILLED)
      Utils.DrawTextAtPos(self.surface,system['Name'],screen_star_pos,14,self.color_Star_Label)
      screen_parent_pos = self.WorldPos2ScreenPos(star['ParentPos'])
      # draw orbit
      if (self.showOrbits_Stars):
        pygame.draw.circle(self.surface,self.color_Orbit,screen_parent_pos,star['OrbitDistance']*self.systemScale,1)
    
    for bodyID in self.systemBodies:
      body = self.systemBodies[bodyID]
      E = body['Eccentricity']
      parentID = body['ParentID']
      radius_on_screen = (Utils.AU_INV*self.systemScale)*body['RadiusBody']
      if (radius_on_screen < self.minPixelSize_Planet):
        radius_on_screen = self.minPixelSize_Planet

      if parentID in system['Stars']:
        screen_star_pos = self.WorldPos2ScreenPos(system['Stars'][parentID]['Pos'])
      else:
        screen_star_pos = self.WorldPos2ScreenPos((0,0))
      screen_body_pos = self.WorldPos2ScreenPos(body['Pos'])
      if (self.showOrbits_Planets):
        # draw orbit
        if (E > 0):
          a = body['Orbit'] * self.systemScale
          b = a * math.sqrt(1-E*E)
          c = E * a
          x_offset = c * math.cos(body['EccentricityAngle']*math.pi/180)
          y_offset = c * math.sin(body['EccentricityAngle']*math.pi/180)
          offsetPos = Utils.AddTuples(screen_star_pos, (x_offset,y_offset))
          Utils.draw_ellipse_angle(self.surface,self.color_Orbit,(offsetPos,(2*a,2*b)),body['EccentricityAngle'],1)
        else:
          pygame.draw.circle(self.surface,self.color_Orbit,screen_star_pos,body['Orbit']*self.systemScale,1)
      # draw planet
      pygame.draw.circle(self.surface,self.color_Planet,screen_body_pos,radius_on_screen,Utils.FILLED)
      Utils.DrawTextAtPos(self.surface,body['Name'],screen_body_pos,14,self.color_PlanetLabel)

  def DrawSystemJumpPoints(self):
    for JP_ID in self.currentSystemJumpPoints:
      JP = self.currentSystemJumpPoints[JP_ID]
      screen_pos = self.WorldPos2ScreenPos(JP['Pos'])
      pygame.draw.circle(self.surface,self.color_JP,screen_pos,5,2)
      screen_pos_label = Utils.AddTuples(screen_pos,10)
      Utils.DrawTextAtPos(self.surface,JP['Destination'],screen_pos_label,14,self.color_JP)
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
          Utils.DrawTextAtPos(self.surface,str(SL['Number']),screen_pos_label,14,self.color_SurveyedLoc)
      else:
        if (self.showUnsurveyedLocations):
          pygame.draw.circle(self.surface,self.color_UnsurveyedLoc,screen_pos,5,1)
          Utils.DrawTextAtPos(self.surface,str(SL['Number']),screen_pos_label,14,self.color_UnsurveyedLoc)
 
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
            Utils.DrawTextAt2(self.surface,fleet['Name'],pos[0]+10,pos[1]-6,12,self.color_Fleet)

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
          component2ID[star[8]] = ID
          stars[ID]['Parent'] = parentComponent = star[9]
          if (stars[ID]['Parent'] == 0):
            stars[ID]['ParentPos'] = (0,0)
          else:
            stars[ID]['ParentPos'] = stars[component2ID[parentComponent]]['Pos']
          stars[ID]['Bearing'] = star[10]
          stars[ID]['OrbitDistance'] = star[13]
          stars[ID]['Pos'] = (star[6],star[7])
        system['Stars'] = stars
        systems[systemID] = system
    return systems

  def GetSystemBodies(self):
    systemBodies = {}
    body_table = [list(x) for x in self.db.execute('''SELECT SystemBodyID, Name, OrbitalDistance, ParentBodyID, Radius, Bearing, Xcor, Ycor, Eccentricity, EccentricityDirection from FCT_SystemBody WHERE GameID = %d AND SystemID = %d AND BodyClass = 1;'''%(self.gameID,self.currentSystem))]
    for body in body_table:
      a = body[2]
      r = body[4]
      d = body[2]
      angle = body[5]
      body_pos = (body[6], body[7])
      angle2 = body[9]
      E = body[8]
      systemBodies[body[0]]={'Name':body[1], 'Orbit':body[2], 'ParentID':body[3], 'RadiusBody':body[4], 'Bearing':body[5],
                            'Eccentricity':body[8],'EccentricityAngle':body[9], 'Pos':(body[6], body[7])}
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

    # FCT_RaceSurveyLocation - holds all surveyed surveylocations
    # RaceID	GameID	SystemID	LocationNumber
    #   418	    95	    8496	      15

    # FCT_RaceJumpPointSurvey - holds all Jumppoints weather discovered (charted) and explored or not
    # GameID	RaceID	WarpPointID	Explored	Charted	AlienUnits	Hide	MilitaryRestricted	IgnoreForDistance
    # 95      	418      	23417	0	0	0	0	0	0
    # 95      	418      	23418	1	1	0	0	0	0


  def WorldPos2ScreenPos(self, world_pos):
    scaled_world_pos = Utils.MulTuples(world_pos,(Utils.AU_INV*self.systemScale))

    return Utils.AddTuples(self.screenCenter ,scaled_world_pos)
