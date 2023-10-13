import Utils
import pygame
import math
import random
import Systems

gameInstance = None

def SetGameInstance(game):
  global gameInstance
  gameInstance = game


def Select_Fleet(id, parent):
  if (gameInstance.currentSystem in gameInstance.fleets):
    if (id in gameInstance.fleets[gameInstance.currentSystem]):
      #print(gameInstance.fleets[game.currentSystem][id])
      gameInstance.highlighted_fleet_ID = id
      gameInstance.highlighted_body_ID=-1
      gameInstance.reDraw = True
      #gameInstance.GetNewData()


def DrawSystemFleets(game):
  if (game.currentSystem in game.fleets):
    for fleetID in game.fleets[game.currentSystem]:
      fleet = game.fleets[game.currentSystem][fleetID]
      if (fleet['Ships'] != [] or game.showEmptyFleets or (game.highlighted_fleet_ID == fleetID)):
        if (fleet['Speed'] > 1 or game.showStationaryFleets or (game.highlighted_fleet_ID == fleetID)):
          pos = game.WorldPos2ScreenPos(fleet['Position'])
          col = game.color_Fleet
          if (game.highlighted_fleet_ID == fleetID):
            col = Utils.CYAN
          if (game.show_FleetTraces):
            prev_pos = game.WorldPos2ScreenPos(fleet['Position_prev'])
            pygame.draw.line(game.surface, col, prev_pos, pos,1)
          bb = Utils.DrawTriangle(game.surface,pos ,col, fleet['Heading'])
          if (game.CheckClickableNotBehindGUI(bb)):
            game.MakeClickable(fleet['Name'], bb, left_click_call_back = Select_Fleet, par=fleetID)
          if (game.highlighted_fleet_ID == fleetID):
            pygame.draw.rect(game.surface, col,(bb[0]-2,bb[1]-2,bb[2]+4,bb[3]+4),2)
          #pygame.draw.circle(game.surface,col,(pos_x,pos_y),5,Utils.FILLED)
          Utils.DrawText2Surface(game.surface,fleet['Name'],(pos[0]+10,pos[1]-6),12,col)


def GetFleets(game):
  fleets = {}
  fleets_table = [list(x) for x in game.db.execute('''SELECT * from FCT_Fleet WHERE GameID = %d AND CivilianFunction = 0 AND RaceID = %d;'''%(game.gameID,game.myRaceID))]
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
    for ship in ships_table:
      name = ship[3]
      fuel = ship[16]
      supplies = ship[44]
      shipClassID = ship[33]
      morale = ship[10]

      shipClass = game.db.execute('''SELECT * from FCT_ShipClass WHERE ShipClassID = %d;'''%(shipClassID)).fetchall()[0]
      shipClassName = shipClass[1]
      fuelCapacity = shipClass[27]
      size = shipClass[66]*50
      suppliesCapacity = shipClass[84]
      magazineCapacity = shipClass[38]
      plannedDeployment = shipClass[53]
      deploymentTime = (game.gameTime-ship[23])/3600/24/365.25*12
      maintenanceLife = (game.gameTime-ship[22])/3600/24/365.25
      components = GetShipComponents(game, shipClassID)
      avgMaintCost = GetAverageMaintCost(components)
      AFR = GetAFR(size, components)
      maintenanceLifeTime = GetMaintainanceLifetime(maintenanceLife, AFR, avgMaintCost)/12
      fleets[systemID][fleetId]['Ships'].append({'Name':name, 'ClassName':shipClassName, 'ClassID': shipClassID, 'Fuel':fuel, 'Fuel Capacity':fuelCapacity, 'Supplies':supplies, 'Supplies Capacity':suppliesCapacity, 'Magazine Capacity':magazineCapacity, 'Size':size, 'PlannedDeployment':plannedDeployment, 'DeploymentTime':deploymentTime, 'MaintenanceClock':maintenanceLife, 'Maintenance Life':maintenanceLifeTime, 'AFR':AFR, '1YR':avgMaintCost})
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


def DrawFleetInfoWindow(game):
  if (game.reDraw_FleetInfoWindow):
    game.Events.ClearClickables(parent=game.window_fleet_info_identifier)
    line_height = 20
    pad_x = pad_y = 5
    lineNr = game.window_fleet_info_scoll_pos
    game.window_fleet_info.fill(Utils.SUPER_DARK_GRAY)
    #print(game.window_fleet_info_scoll_pos)
    if (game.currentSystem in game.fleets):
      for fleetID in game.fleets[game.currentSystem]:
        fleet = game.fleets[game.currentSystem][fleetID]
        if (fleet['Ships'] != [] or game.showEmptyFleets):
          color = Utils.WHITE
          if (game.highlighted_fleet_ID == fleetID):
            color = Utils.CYAN
          label_pos = (pad_x,(pad_y+lineNr*line_height))
          if (fleet['Ships'] != []):
            expRect = Utils.DrawExpander(game.window_fleet_info, (label_pos[0],label_pos[1]+3), 15, color)
            game.MakeClickable(fleet['Name'], expRect, left_click_call_back = game.ExpandFleet, par=fleetID, parent = game.window_fleet_info_identifier, anchor=game.window_fleet_info_anchor)
            label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
          label_pos, label_size = Utils.DrawText2Surface(game.window_fleet_info,fleet['Name']+ ' - ',label_pos,15,color)
          if (label_pos):
            game.MakeClickable(fleet['Name'], (label_pos[0],label_pos[1], label_size[0],label_size[1]), left_click_call_back = Select_Fleet, par=fleetID, parent = game.window_fleet_info_identifier, anchor=game.window_fleet_info_anchor)
          if (fleet['Speed'] > 1) and label_pos:
            speed = str(int(fleet['Speed'])) + 'km/s'

            speed_label_pos, speed_label_size = Utils.DrawText2Surface(game.window_fleet_info,speed,(label_pos[0]+label_size[0],
                                                                                              label_pos[1]),15,color)
            icon_pos = (speed_label_pos[0]+speed_label_size[0], speed_label_pos[1])
            p = 0
            if (fleet['Fuel Capacity'] > 0):
              p = fleet['Fuel']/fleet['Fuel Capacity']

            if ('fuel2' in game.images_GUI):
              icon_rect = Utils.DrawPercentageFilledImage(game.window_fleet_info, 
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
              icon_rect = Utils.DrawPercentageFilledImage(game.window_fleet_info, 
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
          if (fleetID in game.GUI_expanded_fleets):
            shipClasses = {}
            for ship in fleet['Ships']:
              if (ship['ClassName'] not in shipClasses):
                shipClasses[ship['ClassName']] = 1
              else:
                shipClasses[ship['ClassName']] += 1
            for shipClass in shipClasses:
              label_pos = (expRect[0]+expRect[2]+5,(pad_y+lineNr*line_height))
              label_pos, label_size = Utils.DrawText2Surface(game.window_fleet_info,'%dx%s'%(shipClasses[ship['ClassName']],shipClass),label_pos,15,color)
              lineNr +=1

    game.surface.blit(game.window_fleet_info,game.window_fleet_info_anchor)
    game.reDraw_FleetInfoWindow = False
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
    results[compID] = {'ID':compID, 'Name':name, 'ComponentTypeID':typeID, 'Num':num, 'Cost':cost, 'Size':size}
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


def GetMaintainanceLifetime(year, AFR, AMC):
  return year*(year+1) * AFR * AMC / (2*100)


def GetAFR(ShipSize, components):
  if (len(components)>0):
    engSize = 0
    for compID in components:
      comp = components[compID]
      if (comp['ComponentTypeID'] == 47):
        engSize += comp['Size']
    if (engSize > 0):
      return ShipSize*ShipSize*0.0004/(engSize*100)
    else:
      return ShipSize*0.2
