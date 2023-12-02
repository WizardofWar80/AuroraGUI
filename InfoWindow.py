import pygame
import Utils
import math
import Fleets

cursorPos = (0,0)
pad_x = 5
pad_y = 5
lineNr = 0
line_height = 20
textColor = Utils.WHITE
textSize = 15
indentWidth = 17
unscrollableLineNr = 0
gameInstance = None

def SetGameInstance(game):
  global gameInstance
  gameInstance = game


def Clear(context):
  global cursorPos, pad_x, pad_y, lineNr, unscrollableLineNr
  cursorPos = (0,0)
  pad_x = 5
  pad_y = 5
  lineNr = context.window_info_scoll_pos
  unscrollableLineNr = 0
  gameInstance.Events.ClearClickables(parent=context.window_info_identifier)
  context.window_info.fill(Utils.SUPER_DARK_GRAY)


def Draw(context):
  game = context.game
  global lineNr, cursorPos
  if (context.reDraw_InfoWindow):
    Clear(context)
    _indentLevel = 0
    if (game.currentSystem in game.fleets):
      if (game.highlighted_fleet_ID in game.fleets[game.currentSystem]):
        fleet = game.fleets[game.currentSystem][game.highlighted_fleet_ID]
        DrawFleet(context, fleet, _indentLevel)
        #DrawLineOfText(context.window_info, fleet['Name'], 0, True)
      elif (game.highlighted_body_ID in game.starSystems[game.currentSystem]['Stars']):
        body = game.starSystems[game.currentSystem]['Stars'][game.highlighted_body_ID]
        prefix = Utils.GetStarDescription(body) + ' '
        DrawLineOfText(context.window_info, prefix+body['Name'], 0, True)
        DrawTextWithTabs(context.window_info, 'Radius:', 0, str(body['Radius']), 80, context.window_info_scoll_pos)
        DrawTextWithTabs(context.window_info, 'Mass:', 0, str(body['Mass']), 80, context.window_info_scoll_pos)
        DrawTextWithTabs(context.window_info, 'Temp:', 0, str(body['Temp']), 80, context.window_info_scoll_pos)
        DrawTextWithTabs(context.window_info, 'Mass:', 0, str(body['Mass'])+'K', 80, context.window_info_scoll_pos)
        DrawTextWithTabs(context.window_info, 'Luminosity:', 0, str(body['Luminosity']), 80, context.window_info_scoll_pos)
        if (body['BodyClass'] in Utils.SpectralColors):
          col = Utils.SpectralColors[body['BodyClass']]
          DrawTextWithTabs(context.window_info, 'Color:', 0, col, 80, context.window_info_scoll_pos)
      elif (game.highlighted_body_ID in game.systemBodies):
        body = game.systemBodies[game.highlighted_body_ID]
        if (body['Class'] == 'Asteroid' or body['Class'] == 'Comet' or body['Class'] == 'Moon'):
          name = body['Name']
          if (body['Class'] == 'Comet' and name.find('Comet') == -1):
            name = 'Comet '+name+(' (Unsurveyed)' if body['Unsurveyed'] else '')
        else:
          name = body['Class']+' '+body['Name']+(' (Unsurveyed)' if body['Unsurveyed'] else '')
        DrawLineOfText(context.window_info, name, 0, unscrollable = True)

        if ('Deposits' in body):
          # Mineral Deposits info
          expRect = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
          game.MakeClickable(context.info_category_deposits, expRect, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_deposits, parent = context.window_info_identifier, anchor=context.window_info_anchor)
          DrawLineOfText(context.window_info, context.info_category_deposits, _indentLevel+1, unscrollable = True)

          if (context.info_cat_deposits_expanded):
            for mineral in body['Deposits']:
              amount = int(round(body['Deposits'][mineral]['Amount'],0))
              acc = round(body['Deposits'][mineral]['Accessibility'],1)
              if (amount > 0):
                DrawTextWithTabs(context.window_info, mineral[:2]+':', _indentLevel+1, f"{amount:,}", 30, context.window_info_scoll_pos, text3 = '('+str(acc)+')', color3 = Utils.LIGHT_GREEN if acc >= 0.7 else Utils.RED if acc <= 0.3 else Utils.YELLOW, tab_dist2 = 110)
        

        # Physical body info
        expRect = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
        game.MakeClickable(context.info_category_physical, expRect, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_physical, parent = context.window_info_identifier, anchor=context.window_info_anchor)
        DrawLineOfText(context.window_info, context.info_category_physical, _indentLevel+1, unscrollable = True)

        if (context.info_cat_phys_expanded):
          DrawTextWithTabs(context.window_info, 'Type:', _indentLevel+1, str(body['Type']), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Radius:', _indentLevel+1, str(body['RadiusBody'])+' km', 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Type:', _indentLevel+1, str(body['Type']), 130, context.window_info_scoll_pos)
          if (body['ColonyCost']):
            DrawTextWithTabs(context.window_info, 'Colony Cost:', _indentLevel+1, '%2.3f'%body['ColonyCost'], 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Pop Capacity:', _indentLevel+1, f"{body['Population Capacity']:,} M", 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Gravity:', _indentLevel+1, '%s x Earth'%Utils.GetFormattedNumber(body['Gravity']), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Mass:', _indentLevel+1, '%s x Earth'%Utils.GetFormattedNumber(body['Mass']), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Orbit:', _indentLevel+1, '%s AU'%Utils.GetFormattedNumber(body['Orbit']), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Year:', _indentLevel+1, Utils.GetTimeScale(body['HoursPerYear']), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Day:', _indentLevel+1, Utils.GetTimeScale(body['HoursPerDay'])+(' - tidal locked' if body['Tidal locked'] else ''), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Orbit:', _indentLevel+1, '%s AU'%Utils.GetFormattedNumber(body['Orbit']), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Temperature:', _indentLevel+1, '%d C'%(int(body['Temperature'])), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Atmosphere:', _indentLevel+1, ('%s atm'%Utils.GetFormattedNumber(body['AtmosPressure'])) if body['AtmosPressure'] > 0 else '-', 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Hydrosphere:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['Hydrosphere'])) if body['AtmosPressure'] > 0 else '-', 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Magnetic Field:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['MagneticField'])) if body['MagneticField'] > 0 else '-',130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Density:', _indentLevel+1, '%s'%Utils.GetFormattedNumber(body['Density']), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Escape Velocity:', _indentLevel+1, '%s m/s'%Utils.GetFormattedNumber(body['EscapeVelocity']), 130, context.window_info_scoll_pos)
          DrawTextWithTabs(context.window_info, 'Greenhouse Factor:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['GHFactor'])) if body['AtmosPressure'] > 0 else '-', 130, context.window_info_scoll_pos)

        # Economical body info
        if (game.highlighted_body_ID in game.colonies):
          colony = game.colonies[game.highlighted_body_ID]

          expRect1 = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
          game.MakeClickable(context.info_category_economical, expRect1, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_economical, parent = context.window_info_identifier, anchor=context.window_info_anchor)
          DrawLineOfText(context.window_info, context.info_category_economical, _indentLevel+1, unscrollable = True)
          if (context.info_cat_eco_expanded):
            DrawTextWithTabs(context.window_info, 'Population:', _indentLevel+1, str(colony['Pop']), 130, context.window_info_scoll_pos)
            supported_pop = 0
            found_Installations = False
            for installationID in colony['Installations']:
              amountInstallations = colony['Installations'][installationID]['Amount']
              if (amountInstallations > 0):
                found_Installations = True
              if (colony['Installations'][installationID]['Name'] == 'Infrastructure'):
                colonyCost = colony['ColonyCost'] * (1-game.cc_cost_reduction)
                if (colonyCost == 0):
                  supported_pop = body['Population Capacity']
                else:
                  supported_pop = amountInstallations / colonyCost / 100
                if (found_Installations):
                  break
            DrawTextWithTabs(context.window_info, 'Popul. Supported:', _indentLevel+1, f"{round(supported_pop,2):,} M", 130, context.window_info_scoll_pos)
            #DrawTextWithTabs(context.window_info, 'Annual Growth:', _indentLevel+1, '%1.2f%%'%(0), 130)
            req = 0
            act = 0
            DrawTextWithTabs(context.window_info, 'Protection:', _indentLevel+1, '%d / %d'%(act,req), 130, context.window_info_scoll_pos, color2=(Utils.MED_GREEN if act >= req else Utils.RED))

            if (colony['Stockpile']['Sum'] > 0 or colony['Stockpile']['Sum of Minerals'] > 0):
              cursorPos = (cursorPos[0]+indentWidth, cursorPos[1])
              expRect2 = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
              game.MakeClickable(context.info_category_stockpile, expRect2, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_stockpile, parent = context.window_info_identifier, anchor=context.window_info_anchor)
              DrawLineOfText(context.window_info, 'Stockpile', _indentLevel+2, unscrollable = True)
              if (context.info_cat_stock_expanded):
                if (colony['Stockpile']['Sum'] > 0):
                  DrawTextWithTabs(context.window_info, 'Fuel:', _indentLevel+2, f"{colony['Stockpile']['Fuel']:,}", 70, context.window_info_scoll_pos)
                  DrawTextWithTabs(context.window_info, 'Supplies:', _indentLevel+2, f"{colony['Stockpile']['Supplies']:,}", 70, context.window_info_scoll_pos)
                if (colony['Stockpile']['Sum of Minerals'] > 0):
                  index = 1
                  while (index+1 in Utils.MineralNames):
                    mineral = Utils.MineralNames[index]
                    amount = colony['Stockpile'][mineral]
                    mineral2 = Utils.MineralNames[index+1]
                    amount2 = colony['Stockpile'][mineral]
                    DrawTextWithTabs(context.window_info, '%s:'%mineral[:2], _indentLevel+2, f"{amount:,}", 30, context.window_info_scoll_pos, text3 = '%s:'%mineral2[:2], tab_dist2 = 100, text4 = f"{amount2:,}")
                    index+=2
                  if (index in Utils.MineralNames):
                    mineral = Utils.MineralNames[index]
                    amount = colony['Stockpile'][mineral]
                    DrawTextWithTabs(context.window_info, '%s:'%mineral[:2], _indentLevel+2, f"{amount:,}", 30, context.window_info_scoll_pos)

            # installations
            if (found_Installations):
              cursorPos = (cursorPos[0]+indentWidth, cursorPos[1])
              expRect2 = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
              game.MakeClickable(context.info_category_installations, expRect2, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_installations, parent = context.window_info_identifier, anchor=context.window_info_anchor)
              DrawLineOfText(context.window_info, context.info_category_installations, _indentLevel+2, unscrollable = True)
              if (context.info_cat_inst_expanded):
                for InstallationID in colony['Installations']:
                  installation = colony['Installations'][InstallationID]
                  name = installation['Name']
                  amount = installation['Amount']
                  if (installation['Amount'] > 0):
                    DrawTextWithTabs(context.window_info, '%4d'%amount, _indentLevel+1, name, 40, context.window_info_scoll_pos)
        
        fleetsInOrbit = False
        for fleetID in game.fleets[game.currentSystem]:
          fleet = game.fleets[game.currentSystem][fleetID]
          if (fleet['Orbit']['Body'] == game.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
            fleetsInOrbit = True
            break
        if fleetsInOrbit:
          #if (not context.info_cat_eco_expanded):
          cursorPos = (cursorPos[0], cursorPos[1])
          expRect = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
          game.MakeClickable(context.info_category_orbit, expRect, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_orbit, parent = context.window_info_identifier, anchor=context.window_info_anchor)
          DrawLineOfText(context.window_info, context.info_category_orbit, _indentLevel+1, unscrollable = True)
          pygame.draw.line(context.window_info, Utils.WHITE, (cursorPos[0],cursorPos[1]-2),(cursorPos[0]+200,cursorPos[1]-2),1)
          if (context.info_cat_orbit_expanded):
            # orbiting fleets
            for fleetID in game.fleets[game.currentSystem]:
              fleet = game.fleets[game.currentSystem][fleetID]
              if (fleet['Orbit']['Body'] == game.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
                DrawFleet(context, fleet, _indentLevel)

    context.surface.blit(context.window_info, context.window_info_anchor)
    context.reDraw_InfoWindow = False
    return True
  else:
    return False


def DrawLineOfText(surface, line, indentLevel, offset = 0, color = textColor, unscrollable = False, window_info_scoll_pos = 0):
  global cursorPos, pad_x, pad_y, lineNr, unscrollableLineNr
  label_size = None

  if (unscrollable) and (lineNr < unscrollableLineNr):
    cursorPos = (pad_x+(indentLevel*indentWidth)+offset,(pad_y+unscrollableLineNr*line_height))
    unscrollableLineNr += 1
    cursorPos, label_size = Utils.DrawText2Surface(surface, line, cursorPos, textSize, color)
    lineNr += 1
    cursorPos = (pad_x,(pad_y+unscrollableLineNr*line_height))
  elif (lineNr >= unscrollableLineNr):
    cursorPos = (pad_x+(indentLevel*indentWidth)+offset,(pad_y+(lineNr)*line_height))
    cursorPos, label_size = Utils.DrawText2Surface(surface, line, cursorPos, textSize, color)
    lineNr += 1
    cursorPos = (pad_x,(pad_y+lineNr*line_height))
  else:
    lineNr += 1

  return label_size


def DrawTextWithTabs(surface, text1, indentLevel, text2, tab_distance, window_info_scoll_pos = 0, offset = 0, color1 = textColor, color2 = textColor, text3 = None, tab_dist2 = 0, text4 = None, color3 = textColor,color4 = textColor):
  global cursorPos, pad_x, pad_y, lineNr
  label_size = None
  
  if (lineNr >= unscrollableLineNr):
    cursorPos = (pad_x+(indentLevel*indentWidth),(pad_y+(lineNr)*line_height))
    cursorPos, label_size = Utils.DrawText2Surface(surface, text1, cursorPos, textSize, color1)
    if (cursorPos):
      cursorPos, label_size = Utils.DrawText2Surface(surface, text2, (cursorPos[0]+tab_distance,cursorPos[1]), textSize, color2)
  
    if (text3):
      cursorPos = (pad_x+(indentLevel*indentWidth)+offset+tab_dist2,(pad_y+lineNr*line_height))
      cursorPos, label_size = Utils.DrawText2Surface(surface, text3, cursorPos, textSize, color3)
      if (cursorPos) and (text4):
        cursorPos, label_size = Utils.DrawText2Surface(surface, text4, (cursorPos[0]+tab_distance,cursorPos[1]), textSize, color4)
    cursorPos = (pad_x,(pad_y+(lineNr+1)*line_height))
  lineNr += 1

  return label_size


def CleanUp(context, parent):
  if (parent == context.window_fleet_info_identifier):
    context.GUI_expanded_fleets = []
  elif (parent == context.window_info_identifier):
    context.GUI_expanded_fleets2 = []


def DrawFleet(context, fleet, indentLevel = 0):
  game = context.game
  global lineNr

  if (lineNr >= unscrollableLineNr):
    if (fleet['Ships'] != []):
      expRect = Utils.DrawExpander(context.window_info, (cursorPos[0]+indentWidth,cursorPos[1]+3), 15, textColor)
      game.MakeClickable(fleet['Name'], expRect, left_click_call_back = context.ExpandFleet, par=fleet['ID'], parent = context.window_info_identifier, anchor=context.window_info_anchor)
    else:
      expRect = pygame.draw.rect(context.window_info, textColor, (cursorPos[0]+indentWidth+1,cursorPos[1]+3+1, textSize-2, textSize-2), 1)
    label_size = DrawLineOfText(context.window_info, fleet['Name']+ ' - ', indentLevel+2)
    if label_size:
      # decrement line because we still need to draw some icons in this line
      lineNr -=1
      p = 0
      cursor_x_pos = 0
      icon_pos = (cursorPos[0]+label_size[0]+(indentLevel+2)*indentWidth, (pad_y+lineNr*line_height))
      if (fleet['Fuel Capacity'] > 0):
        p = fleet['Fuel']/fleet['Fuel Capacity']
        cursor_x_pos = DrawIcon(context.window_info, 'fuel2', icon_pos, p)+pad_x

      icon_pos = (icon_pos[0]+cursor_x_pos,  (pad_y+lineNr*line_height))
      p = 0
      if (fleet['Supplies Capacity'] > 0):
        p = fleet['Supplies']/fleet['Supplies Capacity']
        cursor_x_pos = DrawIcon(context.window_info, 'supplies', icon_pos, p)
      # increment line because decremented it before
      #print((pad_y+lineNr*line_height), fleet['Name'])
      lineNr +=1
      if (fleet['Station'] and fleet['Fuel Capacity'] > 0):
        capa = Utils.ConvertNumber2kMGT(fleet['Fuel Capacity'])
        fuel = Utils.ConvertNumber2kMGT(fleet['Fuel'])
        label_size = DrawLineOfText(context.window_info, 'Fuel (l): %s /  %s'%(fuel,capa), indentLevel+2)

    if (fleet['ID'] in context.GUI_expanded_fleets2):
      # Draw current order
      orders = Fleets.GetOrders(game, fleet['ID'])
      if(len(orders) > 0):
        label_size = DrawLineOfText(context.window_info, orders[0], indentLevel+2)
        label_size = DrawLineOfText(context.window_info, str(int(fleet['Speed'])) + 'km/s', indentLevel+2)
      cargo = Fleets.GetCargo(game, fleet)
      for cargoID in cargo:
        label_size = DrawLineOfText(context.window_info, cargo[cargoID]['Name'] + ': '+str(cargo[cargoID]['Amount']), indentLevel+2)
      # list ship classes
      shipClasses = {}
      for ship in fleet['Ships']:
        if (ship['ClassName'] not in shipClasses):
          shipClasses[ship['ClassName']] = {'Num':1, 'Commercial':ship['Commercial'], 'Military':ship['Military']}
        else:
          shipClasses[ship['ClassName']]['Num'] += 1
      for shipClass in shipClasses:
        expRect = Utils.DrawExpander(context.window_info, (cursorPos[0]+indentWidth,cursorPos[1]+3), 15, textColor)
        game.MakeClickable(shipClass, expRect, left_click_call_back = context.ExpandShipClasses, par=shipClass, parent = context.window_info_identifier, anchor=context.window_info_anchor)
        DrawLineOfText(context.window_info, '%dx %s'%(shipClasses[ship['ClassName']]['Num'],shipClass), indentLevel+2)
        #if (ship['Military']):
        #  DrawLineOfText(context.window_info, 'AFR: %d%%'%(int(round(ship['AFR']*100,0))), indentLevel+3)
        #  DrawLineOfText(context.window_info, '1YR: %d MSP'%int(round(ship['1YR'],0)), indentLevel+3)

      #if (shipClasses[ship['ClassName']] == 1):
        if(shipClass in context.GUI_expanded_fleets3):
          for ship in fleet['Ships']:
            label_size = DrawLineOfText(context.window_info, ship['Name'], indentLevel+3)
            if label_size:
              # decrement line because we still need to draw some icons in this line
              lineNr -=1
              p = 0
              cursor_x_pos = 0
              icon_pos = (cursorPos[0]+label_size[0]+(indentLevel+3)*indentWidth, (pad_y+lineNr*line_height))
              if (ship['Fuel Capacity'] > 0):
                p = ship['Fuel']/ship['Fuel Capacity']
                cursor_x_pos = DrawIcon(context.window_info, 'fuel2', icon_pos, p)+pad_x

              icon_pos = (icon_pos[0]+cursor_x_pos,  (pad_y+lineNr*line_height))
              p = 0
              if (ship['Supplies Capacity'] > 0):
                p = ship['Supplies']/ship['Supplies Capacity']
                cursor_x_pos = DrawIcon(context.window_info, 'supplies', icon_pos, p)+pad_x
              icon_pos = (icon_pos[0]+cursor_x_pos,  (pad_y+lineNr*line_height))
              p = 0
              if (ship['PlannedDeployment'] > 0):
                p = min(1,ship['DeploymentTime']/ship['PlannedDeployment'])
              cursor_x_pos = DrawIcon(context.window_info, 'clock', icon_pos, p, True)+pad_x
              icon_pos = (icon_pos[0]+cursor_x_pos,  (pad_y+lineNr*line_height))
              p = 0
              if (ship['Maintenance Life'] > 0):
                p = min(1,ship['MaintenanceClock']/ship['Maintenance Life'])
              cursor_x_pos = DrawIcon(context.window_info, 'clock', icon_pos, p, True)+pad_x
              # increment line because decremented it before
              #print((pad_y+lineNr*line_height), fleet['Name'])
              lineNr +=1

            #if (ship['DeploymentTime'] > 0):
            #  DrawLineOfText(context.window_info, 'Deployment: %3.2f (%d)'%(ship['DeploymentTime'], ship['PlannedDeployment']), indentLevel+4)
            #if (ship['Military']):
            #  DrawLineOfText(context.window_info, 'MaintClock: %3.2f (%3.2f)'%(ship['MaintenanceClock'],ship['Maintenance Life']), indentLevel+4)
  else:
    lineNr +=1


def DrawIcon(surface, image_name, icon_pos, perc, inverse = False):
  if (image_name in gameInstance.images_GUI):
    icon_rect = Utils.DrawPercentageFilledImage(surface, 
                                                gameInstance.images_GUI[image_name], 
                                                icon_pos, 
                                                perc, 
                                                color_unfilled = Utils.DARK_GRAY, 
                                                color = Utils.MED_YELLOW, 
                                                color_low = Utils.LIGHT_GREEN if inverse else Utils.RED, 
                                                perc_low = 0.3, 
                                                color_high = Utils.RED if inverse else Utils.LIGHT_GREEN, 
                                                perc_high = 0.7)
    return icon_rect[3]
  else:
    return 0
