import Utils
import pygame
import math
import random
import Fleets

gameInstance = None

def SetGameInstance(game):
  global gameInstance
  gameInstance = game


def Select(id, parent, mousepos = None):
  if (id in gameInstance.starSystems[gameInstance.currentSystem]['Stars']):
    #print(gameInstance.starSystems[gameInstance.currentSystem]['Stars'][id])
    gameInstance.highlighted_fleet_ID = -1
    gameInstance.highlighted_body_ID=id
    gameInstance.systemScreen.reDraw = True
  elif (id in gameInstance.systemBodies):
    #print(gameInstance.systemBodies[id])
    gameInstance.highlighted_fleet_ID = -1
    gameInstance.highlighted_body_ID=id
    gameInstance.systemScreen.reDraw = True
    print(gameInstance.systemBodies[id]['Name'], gameInstance.systemBodies[id]['Pos'])


def Draw(context):
  game = context.game
  if game.currentSystem not in game.starSystems:
    return

  ###################
  # Draw Stars
  ###################
  DrawStars(context)

  # Draw other bodies
  DrawBodies(context)


def DrawStars(context):
  game = context.game
  system = game.starSystems[game.currentSystem]

  for starID in system['Stars']:
    star = system['Stars'][starID]
    screen_star_pos = context.WorldPos2ScreenPos(star['Pos'])
    star_name = star['Name'] + ' ' + star['Suffix']
    star['Visible orbit'] = 0
    # draw star
      
    # draw orbit
    ############
    screen_parent_pos = context.WorldPos2ScreenPos(star['ParentPos'])
    if (context.showOrbits_Stars):
      orbitRadiusOnScreen = star['OrbitDistance']*context.systemScale
      if (orbitRadiusOnScreen > 0):
        Utils.DrawEllipticalOrbit(context.surface, context.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, star['Eccentricity'], star['EccentricityAngle'],star['Bearing'], 10)
        #if (orbitRadiusOnScreen < game.width):
        #  pygame.draw.circle(game.surface, game.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, 1)
        #else:
        #  if Utils.RectIntersectsRadius((0,0,game.width, game.height), screen_parent_pos, orbitRadiusOnScreen):
        #    min_angle, max_angle = Utils.GetAnglesEncompassingRectangle((0,0,game.width, game.height), screen_parent_pos)
        #    Utils.DrawArc(game.surface, game.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, min_angle, max_angle, 1)
      
    # draw Star, either as image or as simple filled circle
    ####################
    radius = (Utils.AU_INV*context.systemScale)*star['Radius']*context.radius_Sun
    star_color = game.stellarTypes[star['StellarTypeID']]['RGB']
    if (radius < context.minPixelSize_Star):
      radius = context.minPixelSize_Star
    star['Visible orbit'] = radius
    if (star['Image'] is not None):
      if (screen_star_pos[0]-radius < context.width and screen_star_pos[0]+radius > 0 and 
          screen_star_pos[1]-radius < context.height and screen_star_pos[1]+radius > 0 ):
        scale = (radius*2,radius*2)
        if (scale[0] > 2*context.width):
          #todo: fix bug where the scaled surface moves when zooming in too much
          scale = (2*context.width,2*context.width)
        scaledSurface = pygame.transform.smoothscale(star['Image'],scale)
        image_offset = Utils.SubTuples(screen_star_pos,scaledSurface.get_rect().center)
        context.surface.blit(scaledSurface,image_offset)
    else:
      if (not star['Black Hole']):
        pygame.draw.circle(context.surface,star_color,screen_star_pos,radius,Utils.FILLED)
      else:
        pygame.draw.circle(context.surface,Utils.RED,screen_star_pos,radius,5)
    bb = (screen_star_pos[0]-radius,screen_star_pos[1]-radius,2*radius,2*radius)
    if (game.CheckClickableNotBehindGUI(bb)):
      game.MakeClickable(star_name, bb, left_click_call_back = Select, par=starID)

    # Label Star
    ################
    if (game.highlighted_body_ID == starID):
      color = Utils.CYAN
    else:
      color = context.color_Label_Star
    labelPos = Utils.AddTuples(screen_star_pos, (0,radius))
    Utils.DrawText2Surface(context.surface,star_name,labelPos,14,color)


def DrawBodies(context):
  game = context.game
  system = game.starSystems[game.currentSystem]

  for bodyID in game.systemBodies:
    body = game.systemBodies[bodyID]
    body['Visible orbit'] = 0
    #screen_parent_size = 0
    body_draw_cond, draw_color_body, body_min_size, body_min_dist = GetDrawConditions(context, 'Body', body)
    if (body_draw_cond):
      screen_body_pos = context.WorldPos2ScreenPos(body['Pos'])
      radius_on_screen = Utils.AU_INV * context.systemScale * body['RadiusBody']
      if (radius_on_screen < body_min_size):
        radius_on_screen = body_min_size
      body['Visible orbit'] = radius_on_screen
      orbit_draw_cond, draw_color_orbit, void, min_orbit = GetDrawConditions(context, 'Orbit', body)
      orbitOnScreen = body['Orbit']*context.systemScale
      parentID = body['ParentID']

      if parentID in system['Stars']:
        screen_parent_pos = context.WorldPos2ScreenPos(system['Stars'][parentID]['Pos'])
        #screen_parent_size = 15
      elif parentID in game.systemBodies:
        screen_parent_pos = context.WorldPos2ScreenPos(game.systemBodies[parentID]['Pos'])
        #screen_parent_size = 9
      else:
        screen_parent_pos = context.WorldPos2ScreenPos((0,0))
        #screen_parent_size = 1

      if (orbit_draw_cond) and (orbitOnScreen > min_orbit) and (orbitOnScreen > body_min_dist):
        E = body['Eccentricity']
        
        Utils.DrawEllipticalOrbit(context.surface, draw_color_orbit, screen_parent_pos, orbitOnScreen, E, body['EccentricityAngle'],body['Bearing'], min_orbit)
        
      # check if we want to draw the object
      ################
      if (screen_body_pos[0] > -50 and screen_body_pos[1] > -50 and screen_body_pos[0] < context.width+50 and screen_body_pos[1] < context.height+50 ):
        pass
      else:
        body_draw_cond = False  
      if (body_draw_cond) and (orbitOnScreen > body_min_dist):
        #if (orbitOnScreen < screen_parent_size):
        #  screen_body_pos = Utils.SubTuples(screen_body_pos, screen_parent_size)

        # draw body
        if (body['Image'] is not None):
          if (screen_body_pos[0]-radius_on_screen < context.width and screen_body_pos[0]+radius_on_screen > 0 and 
              screen_body_pos[1]-radius_on_screen < context.height and screen_body_pos[1]+radius_on_screen > 0 ):
            scale = (radius_on_screen*2,radius_on_screen*2)
            if (scale[0] > 2*context.width):
              #todo: fix bug where the scaled surface moves when zooming in too much
              scale = (2*context.width,2*context.width)
            scaledSurface = pygame.transform.smoothscale(body['Image'],scale)
            image_offset = Utils.SubTuples(screen_body_pos,scaledSurface.get_rect().center)
            context.surface.blit(scaledSurface,image_offset)
        else:
          pygame.draw.circle(context.surface,draw_color_body,screen_body_pos,radius_on_screen,Utils.FILLED)

        HighlightBody(context, body, radius_on_screen*2)

        # Make object clickable
        bb = (screen_body_pos[0]-radius_on_screen,screen_body_pos[1]-radius_on_screen,2*radius_on_screen,2*radius_on_screen)
        if (game.CheckClickableNotBehindGUI(bb)):
          game.MakeClickable(body['Name'], bb, left_click_call_back = Select, par=bodyID)

        # Check if we want to draw the label
        draw_cond, draw_color_label, void, min_dist = GetDrawConditions(context, 'Label', body)
        if (draw_cond) and (orbitOnScreen > min_dist):
          labelPos = Utils.AddTuples(screen_body_pos, (0,radius_on_screen))

          if (game.highlighted_body_ID == bodyID):
            color = Utils.CYAN
          else:
            color = draw_color_label
          # draw the label
          Utils.DrawText2Surface(context.surface, body['Name'], labelPos, 14, color)


def GetDrawConditions(context, thing2Draw, body):
  draw = False
  color = (0,0,0)
  min_size = 5
  min_dist = 5
  if (body['Type'] == 'Stellar'):
    filter = False
  else:
    filter = (body['Colonized'] and context.showColonizedBodies) or (body['Resources'] and context.showResourcefulBodies) or (body['Industrialized'] and context.showIndustrializedBodies) or (body['Xenos'] and context.showXenosBodies)  or (body['Enemies'] and context.showEnemyBodies)  or (body['Unsurveyed'] and context.showUnsurveyedBodies) or (body['Artifacts'] and context.showArtifactsBodies)

  if (thing2Draw == 'Body'):
    if (body['Class'] == 'Moon'):
      if (context.show_Moons or filter):
        draw = True
        color = context.color_Moon
        min_size = context.minPixelSize_Moon
        min_dist = 0 if (body['Colonized'] and context.showColonizedBodies) else 15
    elif (body['Class']  == 'Comet'):
      if (context.show_Comets or filter):
        draw = True
        color = context.color_Comet
        min_size = context.minPixelSize_Small
        min_dist = 0 if (body['Colonized'] and context.showColonizedBodies) else 50
    elif (body['Class']  == 'Asteroid'):
      if (context.show_Asteroids or filter):
        draw = True
        color = context.color_Asteroid
        min_size = context.minPixelSize_Small
        min_dist = 0 if (body['Colonized'] and context.showColonizedBodies) else 50
    elif (body['Type'] == 'Planet Small'):
      if (context.show_DwarfPlanets or filter):
        draw = True
        color = context.color_DwarfPlanet
        min_size = context.minPixelSize_Planet
        min_dist = 0 if (body['Colonized'] and context.showColonizedBodies) else 50
    elif (body['Class'] == 'Planet' and body['Type'] != 'Planet Small' ):
      if (context.show_Planets or filter):
        draw = True
        color = context.color_Planet
        min_size = context.minPixelSize_Planet
        min_dist = 0 if (body['Colonized'] and context.showColonizedBodies) else 15
  elif (thing2Draw == 'Orbit'):
    if (body['Class'] == 'Moon'):
      if (context.showOrbits_Moons and (context.show_Moons or filter)):
        draw = True
        color = context.color_Orbit_Moon
        min_dist = 10
    elif (body['Class']  == 'Comet'):
      if (context.showOrbits_Comets and (context.show_Comets or filter)):
        draw = True
        color = context.color_Orbit_Comet
        min_dist = 10
    elif (body['Class']  == 'Asteroid'):
      if (context.showOrbits_Asteroids and (context.show_Asteroids or filter)):
        draw = True
        color = context.color_Orbit_Asteroid
        min_dist = 10
    elif (body['Type'] == 'Planet Small'):
      if (context.showOrbits_DwarfPlanets and (context.show_DwarfPlanets or filter)):
        draw = True
        color = context.color_Orbit_DwarfPlanet
        min_dist = 10
    elif (body['Class'] == 'Planet' and body['Type'] != 'Planet Small' ):
      if (context.showOrbits_Planets and (context.show_Planets or filter)):
        draw = True
        color = context.color_Orbit_Planet
        min_dist = 10
  elif (thing2Draw == 'Label'):
    if (body['Class'] == 'Moon'):
      if (context.showLabels_Moons and (context.show_Moons or filter)):
        draw = True
        color = context.color_Label_Moon
        min_dist = 50
    elif (body['Class']  == 'Comet'):
      if (context.showLabels_Comets and (context.show_Comets or filter)):
        draw = True
        color = context.color_Label_Comet
        min_dist = 200
    elif (body['Class']  == 'Asteroid'):
      if (context.showLabels_Asteroids and (context.show_Asteroids or filter)):
        draw = True
        color = context.color_Label_Asteroid
        min_dist = 200
    elif (body['Type'] == 'Planet Small'):
      if (context.showLabels_DwarfPlanets and (context.show_DwarfPlanets or filter)):
        draw = True
        color = context.color_Label_DwarfPlanet
        min_dist = 5
    elif (body['Class'] == 'Planet' and body['Type'] != 'Planet Small' ):
      if (context.showLabels_Planets and (context.show_Planets or filter)):
        draw = True
        color = context.color_Label_Planet
        min_dist = 5
  return draw, color, min_size, min_dist


def GetTidalMultiplier(body):
  t = 1

  if (body['Tidal locked'] == True and body['Class'] == 'Planet'):
    t = .2

  return t


def CalculateColonyCost(game, body):
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
    
  if (body['Gravity'] > maxGravity):
    return None, {}

  # Gas Giants, Super Jovians and worlds with a gravity higher than species tolerance cannot be colonised and therefore have no colony cost. 

  # Temperature: If the temperature is outside of the species tolerance, the colony cost factor for temperature is equal to the number of degrees above or below the species tolerance divided by half the total species range. For example, if the species range is from 0C to 30C and the temperature is 75C, the colony cost factor would be 45 / 15 = 3.00. The colony cost factor for tide-locked planets is 20% of normal, so in the example given the colony cost factor would be reduced to 0.60.
  if (body['Temperature'] > minTemp) and (body['Temperature'] < maxTemp):
    tempFactor = 0
  else:
    speciesTempDelta = min(abs(minTemp-body['Temperature']), abs(maxTemp-body['Temperature']))

    tidal_multiplier = GetTidalMultiplier(body)

    tempFactor = speciesTempDelta / (maxTemp-minTemp) * 2 * tidal_multiplier
      

  # Hydrosphere Extent: If less than twenty percent of a body is covered with water (less than 20% Hydro Extent), the colony cost factor for hydro extent is (20 - Hydro Extent) / 10, which is a range from zero to 2.00.
  if (body['Hydrosphere'] >= 20):
    waterFactor = 0
  else:
    waterFactor = 2

  # Atmospheric Pressure: If the atmospheric pressure is above species tolerance, the colony cost factor for pressure is equal to pressure / species max pressure; with a minimum of 2.00. For example, if a species has a pressure tolerance of 4 atm and the pressure is 10 atm, the colony cost factor would be 2.50. If the pressure was 6 atm, the colony cost factor would be 2.00, as that is the minimum.
  atmFactor = max(2,body['AtmosPressure']/maxAtm) if (body['AtmosPressure'] > maxAtm) else 0

  # Dangerous Gas: If a dangerous gas is present in the atmosphere and the concentration is above the danger level, the colony cost factor for dangerous gases will either be 2.00 or 3.00, depending on the gas. Different gases require different concentrations before becoming 'dangerous'. Halogens such as Chlorine, Bromine or Flourine are the most dangerous at 1 ppm, followed by Nitrogen Dioxide and Sulphur Dioxide at 5 ppm. Hydrogen Sulphide is 20 ppm, Carbon Monoxide and Ammonia are 50 ppm, Hydrogen, Methane (if an oxygen breather) and Oxygen (if a Methane breather) are at 500 ppm and Carbon Dioxide is at 5000 ppm (0.5% of atmosphere). Note that Carbon Dioxide was not classed as a dangerous gas in VB6 Aurora. These gases are not lethal at those concentrations but are dangerous enough that infrastructure would be required to avoid sustained exposure.
  bodyGases = game.db.execute('''SELECT AtmosGasID, AtmosGasAmount, GasAtm from FCT_AtmosphericGas WHERE GameID = %d AND SystemBodyID = %d;'''%(game.gameID, body['ID'])).fetchall()
  # gases[results[0]] = {'Name':results[1], 'DangerFactor':results[2], 'DangerousLevel':results[3]/1000}
  dangerAtmFactor = 0
  for bodyGas in bodyGases:
    id = bodyGas[0]
    percentage = bodyGas[1]
    atm = bodyGas[2]

    if id in game.gases:
      if (game.gases[id]['Name'] == 'Oxygen'):
        breathAtm = atm
        breathAtmLevel = percentage
      else:
        if (game.gases[id]['DangerFactor'] > 0):
          if (percentage > game.gases[id]['DangerousLevel']):
            dangerAtmFactor = max(game.gases[id]['DangerFactor'], dangerAtmFactor)

  # Breathable Gas: If the atmosphere does not have a sufficient amount of breathable gas, the colony cost factor for breathable gas is 2.00. If the gas is available in sufficient quantities but exceeds 30% of atmospheric pressure, the colony cost factor is also 2.00.
  if (breathAtm >= breatheMinAtm and breathAtm <= breatheMaxAtm and breathAtmLevel < safeLevel):
    breathFactor = 0
  else:
    breathFactor = 2

  cc = max([tempFactor, breathFactor, dangerAtmFactor, atmFactor, waterFactor])

  return cc * (1-game.cc_cost_reduction), {'tempFactor':tempFactor, 'breathFactor':breathFactor, 'dangerAtmFactor':dangerAtmFactor, 'atmFactor':atmFactor, 'waterFactor':waterFactor}


def GetPopulationCapacityAndColonyCost(game, body):
  popCapacity = 0
  colonyCost = float('inf')
  ccDetails = {}
  if (body['Type'] != 'Planet Gas Giant' and body['Type'] != 'Planet Super Jovian'):
    hydroMultiPlier = 1
    if (body['Hydrosphere'] > 75):
      hydroMultiPlier = -0.0396*body['Hydrosphere']+3.97

    tidalMultiPlier = GetTidalMultiplier(body)

    surfaceArea = 4*body['RadiusBody']*body['RadiusBody']*math.pi
    surfAreaEarth =  511185932.52 
    popCapacity = 12000*surfaceArea/surfAreaEarth
    # todo: Add population desnsity multiplier from race

    popCapacity = popCapacity*hydroMultiPlier*tidalMultiPlier
    popCapacity = Utils.Round(popCapacity,3) if popCapacity < 0.1 else round(popCapacity,1) if popCapacity < 10 else int(round(popCapacity,0))
    if (popCapacity < 0.05):
      popCapacity = 0.05

    colonyCost, ccDetails = CalculateColonyCost(game, body)

  return popCapacity, colonyCost, ccDetails


def GetSystemBodies(game, currentSystem):
  systemBodies = {}
  save_new_images_generated = False
  body_table = [list(x) for x in game.db.execute('''SELECT SystemBodyID, Name, PlanetNumber, OrbitNumber, OrbitalDistance, ParentBodyID, Radius, Bearing, Xcor, Ycor, Eccentricity, EccentricityDirection, BodyClass, BodyTypeID, SurfaceTemp, AtmosPress, HydroExt, Mass, SurfaceTemp, Year, DayValue, TidalLock, MagneticField, EscapeVelocity, GHFactor, Density, Gravity, AGHFactor, Albedo, TectonicActivity, RuinID, RuinRaceID, RadiationLevel, DustLevel, AbandonedFactories, DominantTerrain, GroundMineralSurvey from FCT_SystemBody WHERE GameID = %d AND SystemID = %d;'''%(game.gameID,currentSystem))]
  
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
      body_name = game.db.execute('''SELECT Name from FCT_SystemBodyName WHERE GameID = %d AND RaceID = %d AND SystemID = %d AND SystemBodyID = %d ;'''%(game.gameID,game.myRaceID, currentSystem, body[0])).fetchone()
      if (not body_name):
        if (parentID in systemBodies):
          parentName = systemBodies[parentID]['Name']
        elif(parentID in game.starSystems[currentSystem]['Stars']):
          parentName = game.starSystems[currentSystem]['Stars'][parentID]['Name']

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
    aGHFactor = body[27]
    albedo = body[28]
    tectonicActivity = body[29]
    ruinID = body[30]
    ruinRaceID = body[31]
    radiationLevel = body[32]
    dustLevel = body[33]
    abandonedFactories = body[34]
    dominantTerrain = body[35]
    groundMineralSurvey = body[36]

    dist2Center = math.sqrt(body[8]*body[8]+body[9]*body[9])*Utils.AU_INV
    
    if (bodyClass == 'Moon'):
      orbit = orbit * Utils.AU_INV
    image = None
    if (len(game.images_Body) > 0):
      if (body_name.lower() in game.images_Body['Sol']):
        image = game.images_Body['Sol'][body_name.lower()]
      else:
        image, new_images_generated = Utils.GetObjectImage(game, currentSystem, body[0], bodyClass, bodyType, temp, hydro, atm)
        save_new_images_generated |= new_images_generated
     
    resources = False
    enemies = False
    xenos = False
    artifacts = False

    #check for surveyed bodies
    unsurveyed = False
    result = game.db.execute('''SELECT SystemBodyID from FCT_SystemBodySurveys WHERE GameID = %d AND RaceID = %d AND SystemBodyID = %d;'''%(game.gameID, game.myRaceID, body[0])).fetchone()
    if (not result):
      unsurveyed = True

    colonized = False
    industrialized = False
    terraforming = {'Active':False}
    deposits, sum_minerals = GetMineralDeposits(game, currentSystem, body[0], unsurveyed)

    if (body[0] in game.colonies):
      colony = game.colonies[body[0]]
      if (colony['Pop'] > 0):
        colonized = True
      if (game.colonies[body[0]]['Installations']):
        industrialized = True
    if (sum_minerals > 0):
      resources = True
      terraforming = colony['Terraforming']

    numHarvesters = 0
    fleetIDs = Fleets.GetIDsOfFleetsInOrbit(gameInstance, currentSystem, body[0], type = 'Body')
    for fleetID in fleetIDs:
      numHarvesters += gameInstance.fleets[currentSystem][fleetID]['Harvesters']
          
    bodyStatus = 'C' if colonized else 'I' if industrialized else 'U' if unsurveyed else ''
    
    systemBodies[body[0]]={'ID':body[0],'Name':body_name, 'Type':bodyType, 'Class':bodyClass, 'Orbit':orbit, 'ParentID':body[5], 'RadiusBody':body[6], 
                           'Bearing':body[7], 'Eccentricity':body[10],'EccentricityAngle':body[11], 'Pos':(body[8], body[9]), 'Mass':mass, 'Gravity':gravity,
                           'Temperature':temp, 'AtmosPressure':atm, 'Tidal locked':tidalLock, 'Hydrosphere':hydro, 'Albedo':albedo, 'Density':density, 
                           'MagneticField':magneticField, 'EscapeVelocity':escapeVelocity, 'Distance2Center':dist2Center, 
                           'HoursPerYear': hoursPerYear, 'HoursPerDay': hoursPerDay, 'GHFactor':gHFactor, 'AGHFactor':aGHFactor, 'Image':image,
                           'Colonized':colonized,'Resources':resources, 'Industrialized':industrialized, 'Xenos':xenos, 'Enemies':enemies, 
                           'Unsurveyed':unsurveyed, 'Artifacts':artifacts, 'Visible orbit': 0, 'Status':bodyStatus, 'Terraforming':terraforming, 'Tectonic activity':tectonicActivity, 'RuinID':ruinID, 'RuinRaceID':ruinRaceID, 'RadiationLevel':radiationLevel, 'DustLevel':dustLevel, 'Abandoned Factories':abandonedFactories, 'Dominant Terrain':dominantTerrain, 'GroundMineralSurvey':groundMineralSurvey, 'Large Deposits':True if sum_minerals > 100000 else False, 'Harvesters':numHarvesters}
    systemBodies[body[0]]['Deposits'] = deposits

    popCapacity, colonyCost, ccDetails = GetPopulationCapacityAndColonyCost(game, systemBodies[body[0]])
    systemBodies[body[0]]['ColonyCost'] = colonyCost
    systemBodies[body[0]]['Population Capacity'] = popCapacity
    systemBodies[body[0]]['Colonizable'] = True if colonyCost < 10000 else False

    if (save_new_images_generated):
      game.SaveBodyImages()

  return systemBodies


def GetStellarTypes(game):
  stellarTypes = {}

  results = game.db.execute('''SELECT StellarTypeID, SpectralClass, SpectralNumber, SizeText, SizeID, Luminosity, Mass, Temperature, Radius, Red, Green, Blue from DIM_StellarType;''').fetchall()
    
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

  
def GetMineralDeposits(game, systemID, bodyID, unsurveyed):
  deposits = {}
  sum_deposits = 0
  # GameID	MaterialID	SystemID	SystemBodyID	Amount	Accessibility	HalfOriginalAmount	OriginalAcc
  results = game.db.execute('''SELECT * from FCT_MineralDeposit WHERE GameID = %d and SystemID = %d and SystemBodyID = %d;'''%(game.gameID, systemID, bodyID)).fetchall()
  for id in Utils.MineralNames:
    mineral = Utils.MineralNames[id]
    deposits[mineral] = {'Amount':0, 'Accessibility':0}

  if (not unsurveyed):
    for deposit in results:
      if (deposit[1] in Utils.MineralNames):
        mineral = Utils.MineralNames[deposit[1]]
        deposits[mineral] = {'Amount':deposit[4], 'Accessibility':deposit[5]}
        sum_deposits += deposit[4]

  return deposits, sum_deposits


def HighlightBody(game, body, bodySize):
  pos = game.WorldPos2ScreenPos(body['Pos'])

  if (game.highlightResourcefulBodies and body['Resources']):
    #calculate size and thickness we want to use
    pygame.draw.circle(game.surface, Utils.GRAY, pos, 0.5*bodySize+10, 2)
  if (game.highlightColonizedBodies and body['Colonized']):
    pygame.draw.circle(game.surface, Utils.TEAL, pos, 0.5*bodySize+13, 2)
    pass
  if (game.highlightIndustrializedBodies and body['Industrialized']):
    if (not body['Colonized']):
      pygame.draw.circle(game.surface, Utils.BLUE, pos, 0.5*bodySize+13, 2)
    pass
  if (game.highlightUnsurveyedBodies and body['Unsurveyed']):
    pygame.draw.circle(game.surface, Utils.PURPLE, pos, 0.5*bodySize+10, 2)
    pass
  if (game.highlightEnemyBodies and body['Enemies']):
    Utils.DrawSizedTriangle(game.surface, pos, Utils.RED, bodySize, 3)
  if (game.highlightXenosBodies and body['Xenos']):
    Utils.DrawSizedTriangle(game.surface, pos, Utils.YELLOW, bodySize, 2)
  if (game.highlightArtifactsBodies and body['Artifacts']):
    width = 2*(0.5*bodySize+15)
    pygame.draw.rect(game.surface, Utils.MED_GREEN,(pos[0]-0.5*width, pos[1]-0.5*width, width, width), 2)


def GetBodyFromName(game, name):
  for bodyID in game.systemBodies:
    body = game.systemBodies[bodyID]
    if (body['Name'] == name):
      return body
  return None