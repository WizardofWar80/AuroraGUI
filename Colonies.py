import Utils
import pygame
import math
import Systems

def GetColonies(game):
  colonies = {}
  colonies_table = [list(x) for x in game.db.execute('''SELECT * from FCT_Population WHERE GameID = %d AND RaceID = %d ORDER BY Population DESC;'''%(game.gameID,game.myRaceID))]
  for colony in colonies_table:
      system_name = Systems.GetSystemName(game, colony[29])
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
      industries_table = [list(x) for x in game.db.execute('''SELECT PlanetaryInstallationID, Amount from FCT_PopulationInstallations WHERE GameID = %d AND PopID = %d;'''%(game.gameID,colony[0]))]
      for installation in industries_table:
        id = installation[0]
        amount = installation[1]
        name = ''
        if (id in game.installations):
          name = game.installations[id]['Name']
        colonies[systemBodyID]['Installations'][id] = {'Name':name, 'Amount':amount}

  return colonies


def GetInstallationInfo(game):
  installations = {}

  results = game.db.execute('''SELECT PlanetaryInstallationID, Name from DIM_PlanetaryInstallation;''').fetchall()

  for installation in results:
    installationID = installation[0]
    installationName = installation[1]
    installations[installationID] = {'Name' : installationName}
        
  return installations


def GetCCreduction(game):
  number = 0
  searchString = 'Colonization Cost Reduction'
  results = game.db.execute('''SELECT * from DIM_TechType;''').fetchall()
  techTypeID = -1
  for result in results:
    if (result[1] == searchString):
      techTypeID = result[0]
      break
  results = game.db.execute('''SELECT TechSystemID, Name from FCT_TechSystem WHERE TechTypeID = %d;'''%(techTypeID)).fetchall()
  for result in results:
    researchedTechs = game.db.execute('''SELECT * from FCT_RaceTech WHERE GameID = %d AND RaceID = %d AND TechID = %d;'''%(game.gameID, game.myRaceID, result[0])).fetchall()
    if (researchedTechs):
      percentage = result[1].replace(searchString,'')
      try:
        number = float(percentage[:-1])/100.
      except:
        number = 0
    else:
      break
  return number