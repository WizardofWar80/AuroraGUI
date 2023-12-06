import Utils
import pygame
import math
import random
import Systems

gameInstance = None

def SetGameInstance(game):
  global gameInstance
  gameInstance = game


def Select_Fleet(id, parent, mousepos=None):
  if (gameInstance.currentSystem in gameInstance.fleets):
    if (id in gameInstance.fleets[gameInstance.currentSystem]):
      #print(gameInstance.fleets[game.currentSystem][id])
      gameInstance.highlighted_fleet_ID = id
      gameInstance.highlighted_body_ID=-1
      gameInstance.systemScreen.reDraw = True
      #gameInstance.GetNewData()


def DrawSystemFleets(context):
  game = context.game
  if (game.currentSystem in game.fleets):
    for fleetID in game.fleets[game.currentSystem]:
      fleet = game.fleets[game.currentSystem][fleetID]
      col = context.color_Fleet
      if (game.highlighted_fleet_ID == fleetID):
        col = Utils.CYAN
      if (fleet['Ships'] != [] or context.showEmptyFleets or (game.highlighted_fleet_ID == fleetID)):
        pos = context.WorldPos2ScreenPos(fleet['Position'])
        if (fleet['Speed'] > 1 or context.showStationaryFleets or ((game.highlighted_fleet_ID == fleetID) and not fleet['Station'])):
          if (context.show_FleetTraces):
            prev_pos = context.WorldPos2ScreenPos(fleet['Position_prev'])
            pygame.draw.line(context.surface, col, prev_pos, pos,1)
          bb = Utils.DrawTriangle(context.surface,pos ,col, fleet['Heading'])
          if (game.CheckClickableNotBehindGUI(bb)):
            game.MakeClickable(fleet['Name'], bb, left_click_call_back = Select_Fleet, par=fleetID)
          if (game.highlighted_fleet_ID == fleetID):
            pygame.draw.rect(context.surface, col,(bb[0]-2,bb[1]-2,bb[2]+4,bb[3]+4),2)
          #pygame.draw.circle(game.surface,col,(pos_x,pos_y),5,Utils.FILLED)
          Utils.DrawText2Surface(context.surface,fleet['Name'],(pos[0]+10,pos[1]-6),12,col)
          if (game.drawShipImages):
            size = game.myRaceHullPic.get_size()
            if (size[0]>size[1]):
              ratio = size[1]/size[0]
              scale = (50, 50*ratio)
            else:
              ratio = size[0]/size[1]
              scale = (50, 50*ratio)
            scaledSurface = pygame.transform.smoothscale(game.myRaceHullPic,scale)
            image_offset = Utils.SubTuples(pos,scaledSurface.get_rect().center)
            context.surface.blit(scaledSurface,image_offset)

        if(fleet['Station']):
          orbitingBody = fleet['Orbit']['Body']
          orbitDistance = fleet['Orbit']['Distance']
          orbitBearing = fleet['Orbit']['Bearing']
          visible_orbit = 0
          if orbitingBody in game.starSystems[game.currentSystem]['Stars']:
            body = game.starSystems[game.currentSystem][orbitingBody]
            visible_orbit = body['Visible orbit']
          elif orbitingBody in game.systemBodies:
            body = game.systemBodies[orbitingBody]
            visible_orbit = body['Visible orbit']
            

          if (game.drawStationImages):
            if ('station' in game.images_GUI):
              size = game.images_GUI['station'].get_size()
              image_offset = Utils.SubTuples(pos,game.images_GUI['station'].get_rect().center)
              image_offset = (image_offset[0]+visible_orbit+size[0]/2, image_offset[1])
              context.surface.blit(game.images_GUI['station'],image_offset)
              Utils.DrawText2Surface(context.surface,fleet['Name'],(image_offset[0]+size[0],image_offset[1]+10),12,col)
              if (game.CheckClickableNotBehindGUI((image_offset, size))):
                game.MakeClickable(fleet['Name'], (image_offset, size), left_click_call_back = Select_Fleet, par=fleetID)
            #size = game.myRaceStationPic.get_size()
            #if (size[0]>size[1]):
            #  ratio = size[1]/size[0]
            #  scale = (50, 50*ratio)
            #else:
            #  ratio = size[0]/size[1]
            #  scale = (50, 50*ratio)
            #scaledSurface = pygame.transform.smoothscale(game.myRaceStationPic,scale)
            #image_offset = Utils.SubTuples(pos,scaledSurface.get_rect().center)
            #context.surface.blit(scaledSurface,image_offset)


def GetFleets(game):
  fleets = {}
  fleets_table = [list(x) for x in game.db.execute('''SELECT * from FCT_Fleet WHERE GameID = %d AND CivilianFunction = 0 AND RaceID = %d;'''%(game.gameID,game.myRaceID))]
  total_num_ships = 0
  total_num_stations = 0

  for item in fleets_table:
    fleetId = item[0]
    systemID = item[9]
    system_name = Systems.GetSystemName(game, systemID)
    if systemID not in fleets:
      fleets[systemID] = {}
    fleets[systemID][fleetId] = {}
    fleets[systemID][fleetId]['ID'] = fleetId
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
    if (game.deltaTime > 0 and fleets[systemID][fleetId]['LastMoveTime'] > 0):
      fleets[systemID][fleetId]['Speed'] = math.sqrt((Utils.Sqr(y-y_prev)+Utils.Sqr(x-x_prev)))/game.deltaTime
      
    # Add ships to fleet
    ships_table = [list(x) for x in game.db.execute('''SELECT * from FCT_Ship WHERE FleetID = %d;'''%fleetId)]
    fleets[systemID][fleetId]['Ships'] = []
    fleetFuel = 0
    fleetFuelCapacity = 0
    fleetSupplies = 0
    fleetSuppliesCapacity = 0
    fleetMagazineCapacity = 0
    fleetIsStation = True
    fleetHarvesters = 0
    fleetTerraformers = 0
    for ship in ships_table:
      name = ship[3]
      fuel = ship[16]
      supplies = ship[44]
      shipClassID = ship[33]
      morale = ship[10]

      shipClass = game.db.execute('''SELECT * from FCT_ShipClass WHERE ShipClassID = %d;'''%(shipClassID)).fetchall()[0]
      shipClassName = shipClass[1]
      fuelCapacity = shipClass[26]
      commercial = shipClass[25]
      size = shipClass[65]*50
      cost = shipClass[16]
      suppliesCapacity = shipClass[83]
      magazineCapacity = shipClass[37]
      plannedDeployment = shipClass[52]
      enginePower = shipClass[22]
      numTerraformers = shipClass[68]
      numHarvesters = shipClass[31]
      deploymentTime = (game.gameTime-ship[23])/3600/24/365.25*12
      maintenanceLife = (game.gameTime-ship[22])/3600/24/365.25
      components = GetShipComponents(game, shipClassID)
      avgMaintCost = GetAverageMaintCost(components)
      engSize = GetEngineeringSize(components)
      AFR = GetAFR(size, engSize)
      MSP = GetMSP(components, cost, size, engSize)
      oneYearMSPCost = GetMaintainanceForYears(1,AFR,avgMaintCost)
      fiveYearMSPCost = GetMaintainanceForYears(5,AFR,avgMaintCost)
      maintenanceLifeTime = GetMaintenanceLifetime(MSP, oneYearMSPCost)
      fleets[systemID][fleetId]['Ships'].append({'ID':ship[0], 'Name':name, 'ClassName':shipClassName, 'ClassID': shipClassID, 'Fuel':fuel, 'Fuel Capacity':fuelCapacity, 'Supplies':supplies, 'Supplies Capacity':suppliesCapacity, 'Magazine Capacity':magazineCapacity, 'Size':size, 'PlannedDeployment':plannedDeployment, 'DeploymentTime':deploymentTime, 'MaintenanceClock':maintenanceLife, 'Maintenance Life':maintenanceLifeTime, 'AFR':AFR, '1YR':oneYearMSPCost, 'Commercial':commercial, 'Military':not commercial, 'Station':True if enginePower==0 else False, 'Terraformers':numTerraformers, 'Harvesters':numHarvesters})
      fleetFuel += fuel
      fleetFuelCapacity += fuelCapacity
      fleetSupplies += supplies
      fleetSuppliesCapacity += suppliesCapacity
      fleetMagazineCapacity +=magazineCapacity
      if (enginePower > 0):
        total_num_ships += 1
      else:
        total_num_stations += 1
      fleetIsStation &= (enginePower==0)
      fleetHarvesters+=numHarvesters
      fleetTerraformers+=numTerraformers
    fleets[systemID][fleetId]['Fuel'] = fleetFuel
    fleets[systemID][fleetId]['Fuel Capacity'] = fleetFuelCapacity
    fleets[systemID][fleetId]['Supplies'] = fleetSupplies
    fleets[systemID][fleetId]['Supplies Capacity'] = fleetSuppliesCapacity
    fleets[systemID][fleetId]['Magazine Capacity'] = fleetMagazineCapacity
    fleets[systemID][fleetId]['Station'] = fleetIsStation
    fleets[systemID][fleetId]['Harvesters'] = fleetHarvesters
    fleets[systemID][fleetId]['Terraformers'] = fleetTerraformers

  game.statisticsShips[str(int(game.gameTime))] = total_num_ships
  game.statisticsStations[str(int(game.gameTime))] = total_num_stations

  return fleets


def DrawFleetInfoWindow(context):
  game = context.game
  if (context.reDraw_FleetInfoWindow):
    game.Events.ClearClickables(parent=context.window_fleet_info_identifier)
    line_height = 20
    pad_x = pad_y = 5
    lineNr = context.window_fleet_info_scoll_pos
    context.window_fleet_info.fill(Utils.SUPER_DARK_GRAY)
    #print(context.window_fleet_info_scoll_pos)
    if (game.currentSystem in game.fleets):
      for fleetID in game.fleets[game.currentSystem]:
        fleet = game.fleets[game.currentSystem][fleetID]
        if (fleet['Ships'] != [] or context.showEmptyFleets):
          color = Utils.WHITE
          if (game.highlighted_fleet_ID == fleetID):
            color = Utils.CYAN
          label_pos = (pad_x,(pad_y+lineNr*line_height))
          military = False
          commercial = False
          for ship in fleet['Ships']:
            if ship['Military']:
              military = True
            elif ship['Commercial']:
              commercial = True
            if (commercial and military):
              break
          if (military and context.showMilitaryFleets) or (commercial and context.showCommercialFleets):
            if (fleet['Ships'] != []):
              expRect = Utils.DrawExpander(context.window_fleet_info, (label_pos[0],label_pos[1]+3), 15, color)
              game.MakeClickable(fleet['Name'], expRect, left_click_call_back = game.systemScreen.ExpandFleet, par=fleetID, parent = context.window_fleet_info_identifier, anchor=context.window_fleet_info_anchor)
              label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
            label_pos, label_size = Utils.DrawText2Surface(context.window_fleet_info,fleet['Name']+ ' - ',label_pos,15,color)
            if (label_pos):
              game.MakeClickable(fleet['Name'], (label_pos[0],label_pos[1], label_size[0],label_size[1]), left_click_call_back = Select_Fleet, par=fleetID, parent = context.window_fleet_info_identifier, anchor=context.window_fleet_info_anchor)
            if (fleet['Speed'] > 1) and label_pos:
              speed = str(int(fleet['Speed'])) + 'km/s'

              speed_label_pos, speed_label_size = Utils.DrawText2Surface(context.window_fleet_info,speed,(label_pos[0]+label_size[0],
                                                                                                label_pos[1]),15,color)
              icon_pos = (speed_label_pos[0]+speed_label_size[0], speed_label_pos[1])
              p = 0
              if (fleet['Fuel Capacity'] > 0):
                p = fleet['Fuel']/fleet['Fuel Capacity']

              if ('fuel2' in game.images_GUI):
                icon_rect = Utils.DrawPercentageFilledImage(context.window_fleet_info, 
                                                            game.images_GUI['fuel2'], 
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

              if ('supplies' in game.images_GUI):
                icon_rect = Utils.DrawPercentageFilledImage(context.window_fleet_info, 
                                                            game.images_GUI['supplies'], 
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
            if (fleetID in context.GUI_expanded_fleets):
              shipClasses = {}
              for ship in fleet['Ships']:
                if (ship['ClassName'] not in shipClasses):
                  shipClasses[ship['ClassName']] = 1
                else:
                  shipClasses[ship['ClassName']] += 1
              for shipClass in shipClasses:
                label_pos = (expRect[0]+expRect[2]+5,(pad_y+lineNr*line_height))
                label_pos, label_size = Utils.DrawText2Surface(context.window_fleet_info,'%dx%s'%(shipClasses[ship['ClassName']],shipClass),label_pos,15,color)
                lineNr +=1

    context.surface.blit(context.window_fleet_info,context.window_fleet_info_anchor)
    context.reDraw_FleetInfoWindow = False
    return True
  else:
    return False


def GetShipComponents(game, shipID):
  results = {}
  components = [list(x) for x in game.db.execute('''SELECT * from FCT_ClassComponent WHERE ClassID = %d;'''%(shipID))]
  for comp in components:
    compID = comp[2]
    num = comp[3]
    compDesign = game.db.execute('''SELECT * from FCT_ShipDesignComponents WHERE SDComponentID = %d;'''%(compID)).fetchall()[0]
    name = compDesign[2]
    size = compDesign[8]
    cost = compDesign[9]
    typeID = compDesign[10]
    value = compDesign[11]
    results[compID] = {'ID':compID, 'Name':name, 'ComponentTypeID':typeID, 'Num':num, 'Cost':cost, 'Size':size, 'ComponentValue':value}
  return results


def GetAverageMaintCost(components):
  if(len(components) > 0):
    total_DAC = 0
    total_cost = 0
    for compID in components:
      comp = components[compID]
      if (comp['ComponentTypeID'] != 11 and comp['ComponentTypeID'] <= 70):
        DAC = max([1.0,comp['Size'] * comp['Num']])
        cost = DAC * comp['Cost']
        total_DAC += DAC
        total_cost += cost
    if (total_DAC > 0):
      return total_cost / total_DAC
    else:
      return 0
  else:
    return 0


def GetMaintainanceForYears(year, AFR, AMC):
  return year*(year+1) * AFR * round(AMC,2) / 2


def GetAFR(ShipSize, engSize):
  if (engSize > 0):
    return ShipSize*ShipSize*0.0004/(engSize*100)
  else:
    return ShipSize*0.2


def GetEngineeringSize(components):
  engSize = 0
  if (len(components)>0):
    for compID in components:
      comp = components[compID]
      if (comp['ComponentTypeID'] == 31):
        engSize += comp['Size']*50*comp['Num']
  return engSize


def GetMSP(components, shipCost, shipSize, engSize):
  if (len(components)>0):
    MSPStorage = 0
    for compID in components:
      comp = components[compID]
      if (comp['ComponentTypeID'] == 47):
        MSPStorage += comp['ComponentValue']*comp['Num']
  return MSPStorage + shipCost * 0.5 * engSize / shipSize / 0.04


def GetMaintenanceLifetime(MSP, oneYearMSPCost):
  return math.sqrt(0.25+2*MSP/oneYearMSPCost)-0.5


def GetOrders(game, fleetID):
  results = []
  orders = [list(x) for x in game.db.execute('''SELECT Description from FCT_MoveOrders WHERE FleetID = %d;'''%(fleetID))]
  for order in orders:
    results.append(order[0])
  return results


def GetCargo(game, fleet):
  #GameID	ShipID	CargoTypeID	CargoID	Amount	SpeciesID	StartingPop	Neutral
  #   92	47169      	2         	7	    0.8     	0	      11001     	0

  results = {}
  for ship in fleet['Ships']:
    cargoList = [list(x) for x in game.db.execute('''SELECT * from FCT_ShipCargo WHERE ShipID = %d;'''%(ship['ID']))]
    for cargo in cargoList:
      cargoID = cargo[3]
      cargoType = cargo[2]
      name = 'ID ' + str(cargoID)+', Type'+ str(cargo[2])
      if (cargoType == 3):
        if (cargoID in Utils.MineralNames):
          name = Utils.MineralNames[cargoID]
      elif (cargoType == 2):
        if (cargoID in game.installations):
          name = game.installations[cargoID]['Name']
      cargoAmount = cargo[4]
      if (cargoID not in results):
        results[cargoID] = {'Amount': cargoAmount, 'Name': name}
      else:
        results[cargoID]['Amount'] += cargoAmount
  return results


def GetIDsOfFleetsInOrbit(game, systemID, bodyID, type = 'Body'):
  fleetIDs = []
  fleetsInOrbit = False
  for fleetID in game.fleets[systemID]:
    fleet = game.fleets[systemID][fleetID]
    if (fleet['Orbit']['Body'] == bodyID and fleet['Orbit']['Distance'] == 0):
      fleetIDs.append(fleetID)
  
  return fleetIDs