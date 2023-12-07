import Utils
import pygame
import math

def GetHomeSystemID(game):
  system_number = game.db.execute('''SELECT systemId from FCT_System WHERE GameID = %d AND SystemNumber = 0;'''%(game.gameID)).fetchone()[0]
        
  return system_number


def GetHomeWorldID(game):
  homeworld_id = game.db.execute('''SELECT HomeworldID from FCT_Species WHERE GameID = %d AND SpecialNPRID = 0;'''%(game.gameID)).fetchone()[0]
        
  return homeworld_id


def GetSystemName(game, systemID):
  system_number = game.db.execute('''SELECT SystemNumber from FCT_System WHERE GameID = %d AND systemId = %d;'''%(game.gameID,systemID)).fetchone()[0]
  if (system_number > -1):
      system_name = game.db.execute('''SELECT ConstellationName from DIM_KnownSystems WHERE KnownSystemID = %d;'''%system_number).fetchone()[0].strip()
      if (not system_name):
        system_name = game.db.execute('''SELECT Name from DIM_KnownSystems WHERE KnownSystemID = %d;'''%system_number).fetchone()[0]
  else:
      system_name = 'Unknown'
  return system_name


def GetSystems(game):
  systems = {}

  results = game.db.execute('''SELECT SystemID, SystemNumber from FCT_System WHERE GameID = %d;'''%(game.gameID)).fetchall()
    
  for (systemID, systemNumber) in results:
    if (systemNumber != -1):
      known_system = game.db.execute('''SELECT * from DIM_KnownSystems WHERE KnownSystemID = %d;'''%systemNumber).fetchone()
      system = {}
      system['Name'] = GetSystemName(game, systemID)
      system['Stars'] = None
      stars_table = game.db.execute('''SELECT * from FCT_Star WHERE GameID = %d AND SystemID = %d;'''%(game.gameID,systemID))
      stars = {}
      component2ID = {}
      num_stars = 0
      for x in stars_table:
        num_stars += 1
      # we moved the cursor so we have to run the query again
      stars_table = game.db.execute('''SELECT * from FCT_Star WHERE GameID = %d AND SystemID = %d;'''%(game.gameID,systemID))
        
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
        stars[ID]['Radius']=game.stellarTypes[stars[ID]['StellarTypeID']]['Radius']
        stars[ID]['Mass'] = game.stellarTypes[stars[ID]['StellarTypeID']]['Mass']
        stars[ID]['Temp'] = game.stellarTypes[stars[ID]['StellarTypeID']]['Temperature']
        stars[ID]['Luminosity'] = game.stellarTypes[stars[ID]['StellarTypeID']]['Luminosity']
        stars[ID]['Black Hole']=False
        spectralClass = game.stellarTypes[stars[ID]['StellarTypeID']]['SpectralClass']
        spectralNumber = game.stellarTypes[stars[ID]['StellarTypeID']]['SpectralNumber']
        sizeText = game.stellarTypes[stars[ID]['StellarTypeID']]['SizeText']
        stars[ID]['Suffix'] = spectralClass + str(spectralNumber) +'-'+ sizeText
        if (spectralClass == 'BH'):
          # black holes should use Schwartzschildradius:
          # r = M * 0.000004246 sunradii
          m = game.stellarTypes[stars[ID]['StellarTypeID']]['Mass']
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
        stars[ID]['Visible orbit'] = 0
        if (len(game.images_Body) > 0):
          if (spectralClass in game.images_Body['Stars']):
            stars[ID]['Image'] = game.images_Body['Stars'][spectralClass]
        star_index += 1
        stars[ID]['BodyClass']=spectralClass
        stars[ID]['BodyType']='Stellar'
      system['Stars'] = stars
      systems[systemID] = system
  return systems


def GetSystemJumpPoints(game, currentSystem):
  jp_table = [list(x) for x in game.db.execute('''SELECT * from FCT_RaceJumpPointSurvey WHERE GameID = %d AND RaceID = %d;'''%(game.gameID, game.myRaceID))]
  raceJPs = {}
  for JP in jp_table:
    raceJPs[JP[2]] = {'found':JP[4], 'explored':JP[3]}
  jp_table = [list(x) for x in game.db.execute('''SELECT * from FCT_JumpPoint WHERE GameID = %d AND SystemID = %d;'''%(game.gameID, currentSystem))]
  JPs = {}
  index = 1
  for JP in jp_table:
    JP_ID = JP[0]
    if (JP_ID in raceJPs):
      if (raceJPs[JP_ID]['found']):
        JP_fromSystemID = JP[2]
        JP_toWP = JP[5]
        JP_explored = raceJPs[JP_ID]['explored']
        JP_Gate = (0 if JP[8]==0 else 1)
        pos = (JP[6],JP[7])
        bearing = JP[4]
        JP_fromSystem = GetSystemName(game, JP_fromSystemID)
        if (JP_explored):
          JP_toSystemID = game.db.execute('''SELECT SystemID from FCT_JumpPoint WHERE GameID = %d AND WarpPointID = %d;'''%(game.gameID,JP_toWP)).fetchone()[0]
          JP_toSystem = GetSystemName(game, JP_toSystemID)
        else:
          JP_toSystemID = -1
          JP_toSystem = 'JP '+str(index)
          index+=1
        if (JP_fromSystem != 'Unknown'):
          JPs[JP_ID] = {'Destination': JP_toSystem, 'DestID': JP_toSystemID, 
                        'Explored':JP_explored, 'Gate':JP_Gate, 'Pos': pos, 'Bearing':bearing, 
                        'CurrentSystem':JP_fromSystem,'CurrentSystemID':JP_fromSystemID}
  return JPs


def GetSurveyLocations(game, systemID):
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
  mySurveyedLocationsTable = [list(x) for x in game.db.execute('''SELECT LocationNumber from FCT_RaceSurveyLocation WHERE GameID = %d AND SystemID = %d AND RaceID = %d;'''%(game.gameID, systemID, game.myRaceID))]
  mySurveyedLocations = []
  for N in mySurveyedLocationsTable:
    mySurveyedLocations.append(N[0])

  # todo: check for single line returns
  surveyLocationTable = [list(x) for x in game.db.execute('''SELECT * from FCT_SurveyLocation WHERE GameID = %d AND SystemID = %d;'''%(game.gameID, systemID))]
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


def DrawSystemJumpPoints(context):
  game = context.game
  for JP_ID in game.currentSystemJumpPoints:
    JP = game.currentSystemJumpPoints[JP_ID]
    heading = math.atan2(JP['Pos'][1],JP['Pos'][0])
    screen_pos = context.WorldPos2ScreenPos(JP['Pos'])
    if (JP['Explored']):
      bb = Utils.DrawArrow(context.surface, screen_pos, Utils.GREEN,heading)
      if (game.CheckClickableNotBehindGUI(bb)):
        game.MakeClickable(JP['Destination'], bb, left_click_call_back = context.Follow_Jumppoint, par = JP['DestID'])

    pygame.draw.circle(context.surface,context.color_JP,screen_pos,5,2)
    screen_pos_label = Utils.AddTuples(screen_pos,10)
    Utils.DrawText2Surface(context.surface,JP['Destination'],screen_pos_label,14,context.color_JP)
    if (JP['Gate']):
      gate_pos = Utils.SubTuples(screen_pos,7)
      pygame.draw.rect(context.surface, context.color_Jumpgate, (gate_pos,(14,14)),1)


def DrawSurveyLocations(context):
  for id in context.game.surveyLocations:
    SL = context.game.surveyLocations[id]
    screen_pos = context.WorldPos2ScreenPos(SL['Pos'])
    screen_pos_label = Utils.AddTuples(screen_pos,(0,10))
    if (SL['Surveyed']):
      if (context.showSurveyedLocations):
        pygame.draw.circle(context.surface,context.color_SurveyedLoc,screen_pos,5,1)
        Utils.DrawText2Surface(game.surface,str(SL['Number']),screen_pos_label,14,context.color_SurveyedLoc)
    else:
      if (context.showUnsurveyedLocations):
        pygame.draw.circle(context.surface,context.color_UnsurveyedLoc,screen_pos,5,1)
        Utils.DrawText2Surface(context.surface,str(SL['Number']),screen_pos_label,14,context.color_UnsurveyedLoc)
 

def GetKnownSystemNames(game):
  results = []
  for id in game.starSystems:
    if game.starSystems[id]['Name'] not in results:
      results.append(game.starSystems[id]['Name'])
  return results


def GetSystemIDByName(game, name):
  for id in game.starSystems:
    if game.starSystems[id]['Name'] == name:
      return id
  return None


def GetIndexOfCurrentSystem(game):
  results = []
  index = 0
  for id in game.starSystems:
    if id not in results:
      results.append(id)
      if (id == game.currentSystem):
        return index
      index += 1

  return None