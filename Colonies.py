import Utils
import pygame
import math
import Systems


def InitStockpile():
  stockpile = {'Fuel':0,'Supplies':0}
  for mineralID in Utils.MineralNames:
    stockpile[Utils.MineralNames[mineralID]] = 0
  return stockpile


def GetColonies(game):
  colonies = {}
  total_population = 0
  total_stockpile = InitStockpile()

  colonies_table = [list(x) for x in game.db.execute('''SELECT * from FCT_Population WHERE GameID = %d AND RaceID = %d ORDER BY Population DESC;'''%(game.gameID,game.myRaceID))]
  for colony in colonies_table:
    system_name = Systems.GetSystemName(game, colony[29])
    systemBodyID = colony[30]
    stockpile_sum = 0
    stockpile_minerals_sum = 0
    pop = colony[24]
    fuel = colony[13]
    supplies = colony[18]
    total_population += pop
    colonies[systemBodyID] = {'Name':colony[4],'Pop':round(pop,2), 'SystemID':colony[29],'System':system_name, 'ColonyCost':colony[17], 'Stockpile':{'Fuel':int(round(fuel)),'Supplies':int(round(supplies))}}
    total_stockpile['Fuel'] += fuel
    total_stockpile['Supplies'] += supplies
    stockpile_sum = int(round(colony[13]) + round(colony[18]))
    for mineralID in Utils.MineralNames:
      mineral = Utils.MineralNames[mineralID]
      amount = int(round(colony[34+mineralID-1],0))
      colonies[systemBodyID]['Stockpile'][mineral] = amount
      stockpile_minerals_sum += amount
      total_stockpile[mineral] += amount
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

    game.statisticsPopulation[str(int(game.gameTime))] = total_population
    for name in total_stockpile:
      if name not in game.statisticsStockpile:
        game.statisticsStockpile[name] = {}
      game.statisticsStockpile[name][str(int(game.gameTime))] = total_stockpile[name]

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