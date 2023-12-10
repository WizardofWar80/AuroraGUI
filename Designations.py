import json
#import Utils
#import pygame
#import math
#import random
#import Systems
#import Fleets

gameInstance = None

designations = {'Systems':{}, 'Fleets':{}}

system_designations = ['None', 'Empty', 'Home', 'Mining', 'Fuel Harvesting', 'Population Centre', 'Military', 'Capital', 'Sector Command', 'Research', 'Enemy']
fleet_designations = ['None', 'Defense', 'Mining', 'Fuel Harvesting', 'Terraforming', 'Exploration', 'Transport', 'Intelligence', 'Attack', 'Supply', 'Science',  'Salvaging', 'Rescue', 'Troop Transport']


def Init(game):
  SetGameInstance(game)
  Load()


def SetGameInstance(game):
  global gameInstance
  gameInstance = game


def Load():
  global designations
  if (gameInstance):
    filename = 'designations_game_%d.json'%gameInstance.gameID
    try:
      with open(filename, 'r') as f:
        designations = json.load(f)
    except:
      print('File %s not found'%filename)


def Save():
  if (gameInstance):
    filename = 'designations_game_%d.json'%gameInstance.gameID
    try:
      with open(filename, 'w') as f:
        json.dump(designations, f)
    except:
      print('File %s not writeable'%filename)


def GetIndexOfCurrentSystem():
  index = 0
  if (str(gameInstance.currentSystem) in designations['Systems']):
    desig = designations['Systems'][str(gameInstance.currentSystem)]
    index = system_designations.index(desig)
  return index


def Set(systemID, designationID):
  if (designationID < len(system_designations)):
    #if (systemID in designations['Systems']):
    designations['Systems'][str(systemID)] = system_designations[designationID]
    Save()