import pygame
import Utils

cursorPos = (0,0)
pad_x = 5
pad_y = 5
lineNr = 0
line_height = 20
textColor = Utils.WHITE
textSize = 15
indentWidth = 17

def Clear(game):
  global cursorPos, pad_x, pad_y, lineNr
  cursorPos = (0,0)
  pad_x = 5
  pad_y = 5
  lineNr = 0
  game.Events.ClearClickables(parent=game.window_info_identifier)
  game.window_info.fill(Utils.SUPER_DARK_GRAY)


def Draw(game):
  if (game.reDraw_InfoWindow):
    Clear(game)
    _indentLevel = 0
    if (game.highlighted_fleet_ID in game.fleets[game.currentSystem]):
      fleet = game.fleets[game.currentSystem][game.highlighted_fleet_ID]
      DrawLineOfText(game.window_info, fleet['Name'], 0)
    elif (game.highlighted_body_ID in game.starSystems[game.currentSystem]['Stars']):
      body = game.starSystems[game.currentSystem]['Stars'][game.highlighted_body_ID]
      prefix = Utils.GetStarDescription(body) + ' '
      DrawLineOfText(game.window_info, prefix+body['Name'], 0)
      DrawTextWithTabs(game.window_info, 'Radius:', 0, str(body['Radius']), 80)
      DrawTextWithTabs(game.window_info, 'Mass:', 0, str(body['Mass']), 80)
      DrawTextWithTabs(game.window_info, 'Temp:', 0, str(body['Temp']), 80)
      DrawTextWithTabs(game.window_info, 'Mass:', 0, str(body['Mass'])+'K', 80)
      DrawTextWithTabs(game.window_info, 'Luminosity:', 0, str(body['Luminosity']), 80)
      if (body['BodyClass'] in Utils.SpectralColors):
        col = Utils.SpectralColors[body['BodyClass']]
        DrawTextWithTabs(game.window_info, 'Color:', 0, col, 80)
    elif (game.highlighted_body_ID in game.systemBodies):
      body = game.systemBodies[game.highlighted_body_ID]
      if (body['Class'] == 'Asteroid' or body['Class'] == 'Comet' or body['Class'] == 'Moon'):
        name = body['Name']
        if (body['Class'] == 'Comet' and name.find('Comet') == -1):
          name = 'Comet '+name+(' (Unsurveyed)' if body['Unsurveyed'] else '')
      else:
        name = body['Class']+' '+body['Name']+(' (Unsurveyed)' if body['Unsurveyed'] else '')
      DrawLineOfText(game.window_info, name, 0)

      # Physical body info
      expRect = Utils.DrawExpander(game.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
      game.MakeClickable(game.info_category_physical, expRect, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_physical, parent = game.window_info_identifier, anchor=game.window_info_anchor)
      DrawLineOfText(game.window_info, game.info_category_physical, _indentLevel+1)

      if (game.info_cat_phys_expanded):
        DrawTextWithTabs(game.window_info, 'Type:', _indentLevel+1, str(body['Type']), 130)
        DrawTextWithTabs(game.window_info, 'Radius:', _indentLevel+1, str(body['RadiusBody'])+' km', 130)
        DrawTextWithTabs(game.window_info, 'Type:', _indentLevel+1, str(body['Type']), 130)
        if (body['ColonyCost']):
          DrawTextWithTabs(game.window_info, 'Colony Cost:', _indentLevel+1, '%2.3f'%body['ColonyCost'], 130)
        DrawTextWithTabs(game.window_info, 'Pop Capacity:', _indentLevel+1, f"{body['Population Capacity']:,} M", 130)
        DrawTextWithTabs(game.window_info, 'Gravity:', _indentLevel+1, '%s x Earth'%Utils.GetFormattedNumber(body['Gravity']), 130)
        DrawTextWithTabs(game.window_info, 'Mass:', _indentLevel+1, '%s x Earth'%Utils.GetFormattedNumber(body['Mass']), 130)
        DrawTextWithTabs(game.window_info, 'Orbit:', _indentLevel+1, '%s AU'%Utils.GetFormattedNumber(body['Orbit']), 130)
        DrawTextWithTabs(game.window_info, 'Year:', _indentLevel+1, Utils.GetTimeScale(body['HoursPerYear']), 130)
        DrawTextWithTabs(game.window_info, 'Day:', _indentLevel+1, Utils.GetTimeScale(body['HoursPerDay'])+(' - tidal locked' if body['Tidal locked'] else ''), 130)
        DrawTextWithTabs(game.window_info, 'Orbit:', _indentLevel+1, '%s AU'%Utils.GetFormattedNumber(body['Orbit']), 130)
        DrawTextWithTabs(game.window_info, 'Temperature:', _indentLevel+1, '%d C'%(int(body['Temperature'])), 130)
        DrawTextWithTabs(game.window_info, 'Atmosphere:', _indentLevel+1, ('%s atm'%Utils.GetFormattedNumber(body['AtmosPressure'])) if body['AtmosPressure'] > 0 else '-', 130)
        DrawTextWithTabs(game.window_info, 'Hydrosphere:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['Hydrosphere'])) if body['AtmosPressure'] > 0 else '-', 130)
        DrawTextWithTabs(game.window_info, 'Magnetic Field:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['MagneticField'])) if body['MagneticField'] > 0 else '-',130)
        DrawTextWithTabs(game.window_info, 'Density:', _indentLevel+1, '%s'%Utils.GetFormattedNumber(body['Density']), 130)
        DrawTextWithTabs(game.window_info, 'Escape Velocity:', _indentLevel+1, '%s m/s'%Utils.GetFormattedNumber(body['EscapeVelocity']), 130)
        DrawTextWithTabs(game.window_info, 'Greenhouse Factor:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['GHFactor'])) if body['AtmosPressure'] > 0 else '-', 130)

      # Economical body info
      if (game.highlighted_body_ID in game.colonies):
        colony = game.colonies[game.highlighted_body_ID]

        expRect1 = Utils.DrawExpander(game.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
        game.MakeClickable(game.info_category_economical, expRect1, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_economical, parent = game.window_info_identifier, anchor=game.window_info_anchor)
        DrawLineOfText(game.window_info, game.info_category_economical, _indentLevel+1)
        if (game.info_cat_eco_expanded):
          DrawTextWithTabs(game.window_info, 'Population:', _indentLevel+1, str(colony['Pop']), 130)
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

          DrawTextWithTabs(game.window_info, 'Popul. Supported:', _indentLevel+1, f"{round(supported_pop,2):,} M", 130)
          #DrawTextWithTabs(game.window_info, 'Annual Growth:', _indentLevel+1, '%1.2f%%'%(0), 130)
          req = 0
          act = 0
          DrawTextWithTabs(game.window_info, 'Protection:', _indentLevel+1, '%d / %d'%(act,req), 130,color2=(Utils.MED_GREEN if act >= req else Utils.RED))

      #    label_pos = (x,(pad_y+lineNr*line_height))
      #    label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Protection:',label_pos,15,color)
      #    req = 0
      #    act = 0
      #    label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
      #    label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%d / %d'%(act,req),label_pos2,15)

      #    if (colony['Stockpile']['Sum'] > 0 or colony['Stockpile']['Sum of Minerals'] > 0):
      #      lineNr+=1
      #      x = expRect1[0]+expRect1[2]+5
      #      label_pos = (x,(pad_y+lineNr*line_height))
      #      #label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Stockpile',label_pos,15,color)
      #      expRect2 = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
      #      game.MakeClickable(game.info_category_stockpile, expRect2, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_stockpile, parent = game.window_info_identifier, anchor=game.window_info_anchor)
      #      label_pos = (expRect2[0]+expRect2[2]+5,label_pos[1])
      #      label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Stockpile',label_pos,15,color)
      #      if (game.info_cat_stock_expanded):
      #        lat_offs = 70
      #        x = expRect2[0]+expRect2[2]+5
      #        lineNr+=1
      #        if (colony['Stockpile']['Sum'] > 0):
      #          label_pos = (x,(pad_y+lineNr*line_height))
      #          label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Fuel:',label_pos,15,color)
      #          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
      #          label_pos2, label_size = Utils.DrawText2Surface(game.window_info,f"{colony['Stockpile']['Fuel']:,}",label_pos2,15,color)
      #          lineNr+=1
      #          label_pos = (x,(pad_y+lineNr*line_height))
      #          label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Supplies:',label_pos,15,color)
      #          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
      #          label_pos2, label_size = Utils.DrawText2Surface(game.window_info,f"{colony['Stockpile']['Supplies']:,}",label_pos2,15,color)
      #          lineNr+=1
      #        if (colony['Stockpile']['Sum of Minerals'] > 0):
      #          lat_offs2 = 30
      #          for index in Utils.MineralNames:
      #            mineral = Utils.MineralNames[index]
      #            amount = colony['Stockpile'][mineral]
      #            label_pos = (x,(pad_y+lineNr*line_height))
      #            label_pos, label_size = Utils.DrawText2Surface(game.window_info,'%s:'%mineral[:2],label_pos,15,color)
      #            label_pos2 = (x+lat_offs2,(pad_y+lineNr*line_height))
      #            label_pos2, label_size = Utils.DrawText2Surface(game.window_info,f"{amount:,}",label_pos2,15,color)
      #            lineNr+=1
      #            if (index == 6):
      #              lineNr -= 6
      #              x += 100
          
      #    lineNr+=1
      #    # installations
      #    if (found_Installations):
      #      x = expRect1[0]+expRect1[2]+5
      #      label_pos = (x,(pad_y+lineNr*line_height))
      #      #label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Stockpile',label_pos,15,color)
      #      expRect2 = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
      #      game.MakeClickable(game.info_category_installations, expRect2, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_installations, parent = game.window_info_identifier, anchor=game.window_info_anchor)
      #      label_pos = (expRect2[0]+expRect2[2]+5,label_pos[1])
      #      label_pos, label_size = Utils.DrawText2Surface(game.window_info,game.info_category_installations,label_pos,15,color)
      #      lineNr+=1
      #      if (game.info_cat_inst_expanded):
      #        x = expRect2[0]+expRect2[2]+5
      #        for InstallationID in colony['Installations']:
      #          installation = colony['Installations'][InstallationID]
      #          name = installation['Name']
      #          amount = installation['Amount']
      #          if (installation['Amount'] > 0):
      #            lat_offs2 = 40
      #            label_pos = (x,(pad_y+lineNr*line_height))
      #            label_pos, label_size = Utils.DrawText2Surface(game.window_info,'%4d'%amount,label_pos,15,color)
      #            label_pos2 = (x+lat_offs2,(pad_y+lineNr*line_height))
      #            label_pos2, label_size = Utils.DrawText2Surface(game.window_info,name,label_pos2,15,color)
      #            lineNr+=1
      #            #if (index == 6):
      #            #  lineNr -= 6
      #            #  x += 100
        
      #fleetsInOrbit = False
      #for fleetID in game.fleets[game.currentSystem]:
      #  fleet = game.fleets[game.currentSystem][fleetID]
      #  if (fleet['Orbit']['Body'] == game.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
      #    fleetsInOrbit = True
      #    break
      #if fleetsInOrbit:
      #  if (not game.info_cat_eco_expanded):
      #    lineNr+=1
      #  x = pad_x
      #  label_pos = (x,(pad_y+lineNr*line_height))
      #  expRect = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
      #  game.MakeClickable(game.info_category_orbit, expRect, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_orbit, parent = game.window_info_identifier, anchor=game.window_info_anchor)
      #  label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
      #  label_pos, label_size = Utils.DrawText2Surface(game.window_info,game.info_category_orbit,label_pos,15,color)
      #  lineNr+=1
      #  orbitFleetTopRow = lineNr
      #  pygame.draw.line(game.window_info, Utils.WHITE, (x,(pad_y+lineNr*line_height-2)),((x+200,(pad_y+lineNr*line_height-2))),1)
      #  lineNr+=game.window_info_scoll_pos
      #  if (game.info_cat_orbit_expanded):
      #    x = label_pos[0] if label_pos else (expRect[0]+expRect[2]+5)
      #    # orbiting fleets
      #    for fleetID in game.fleets[game.currentSystem]:
      #      fleet = game.fleets[game.currentSystem][fleetID]
      #      if (fleet['Orbit']['Body'] == game.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
      #        if (lineNr >= orbitFleetTopRow):
      #          color = Utils.WHITE
      #          label_pos = (x,(pad_y+lineNr*line_height))
      #          if (fleet['Ships'] != []):
      #            expRect = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
      #            game.MakeClickable(fleet['Name'], expRect, left_click_call_back = game.ExpandFleet, par=fleetID, parent = game.window_info_identifier, anchor=game.window_info_anchor)
      #          else:
      #            expRect = pygame.draw.rect(game.window_info, color, (label_pos[0]+1,label_pos[1]+3+1, 15-2, 15-2), 1)
      #          label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
      #          label_pos, label_size = Utils.DrawText2Surface(game.window_info,fleet['Name']+ ' - ',label_pos,15,color)
      #          if (label_pos):
      #            game.MakeClickable(fleet['Name'], (label_pos[0],label_pos[1], label_size[0],label_size[1]), left_click_call_back = game.Select_Fleet, par=fleetID, parent = game.window_info_identifier, anchor=game.window_info_anchor)
      #            p = 0
      #            icon_pos = (label_pos[0]+label_size[0], label_pos[1])
      #            if (fleet['Fuel Capacity'] > 0):
      #              p = fleet['Fuel']/fleet['Fuel Capacity']

      #            if ('fuel2' in game.images_GUI):
      #              icon_rect = Utils.DrawPercentageFilledImage(game.window_info, 
      #                                                          game.images_GUI['fuel2'], 
      #                                                          icon_pos, 
      #                                                          p, 
      #                                                          color_unfilled = Utils.DARK_GRAY, 
      #                                                          color = Utils.MED_YELLOW, 
      #                                                          color_low = Utils.RED, 
      #                                                          perc_low = 0.3, 
      #                                                          color_high = Utils.LIGHT_GREEN, 
      #                                                          perc_high = 0.7)

      #            icon_pos = (icon_rect[0]+icon_rect[3]+pad_x, icon_rect[1])
      #            p = 0
      #            if (fleet['Supplies Capacity'] > 0):
      #              p = fleet['Supplies']/fleet['Supplies Capacity']

      #            if ('supplies' in game.images_GUI):
      #              icon_rect = Utils.DrawPercentageFilledImage(game.window_info, 
      #                                                          game.images_GUI['supplies'], 
      #                                                          icon_pos, 
      #                                                          p, 
      #                                                          color_unfilled = Utils.DARK_GRAY, 
      #                                                          color = Utils.MED_YELLOW, 
      #                                                          color_low = Utils.RED, 
      #                                                          perc_low = 0.3, 
      #                                                          color_high = Utils.LIGHT_GREEN, 
      #                                                          perc_high = 0.7)

      #          #print((pad_y+lineNr*line_height), fleet['Name'])
      #          lineNr +=1

      #          if (fleetID in game.GUI_expanded_fleets2):
      #            shipClasses = {}
      #            for ship in fleet['Ships']:
      #              if (ship['ClassName'] not in shipClasses):
      #                shipClasses[ship['ClassName']] = 1
      #              else:
      #                shipClasses[ship['ClassName']] += 1
      #            for shipClass in shipClasses:
      #              label_pos = (expRect[0]+expRect[2]+5,(pad_y+lineNr*line_height))
      #              label_pos, label_size = Utils.DrawText2Surface(game.window_info,'%dx%s'%(shipClasses[ship['ClassName']],shipClass),label_pos,15,color)
      #              lineNr +=1
      #        else:
      #          lineNr +=1

    game.surface.blit(game.window_info,game.window_info_anchor)
    game.reDraw_InfoWindow = False
    return True
  else:
    return False


def DrawLineOfText(surface, line, indentLevel):
  global cursorPos, pad_x, pad_y, lineNr

  cursorPos = (pad_x+(indentLevel*indentWidth),(pad_y+lineNr*line_height))
  cursorPos, label_size = Utils.DrawText2Surface(surface, line, cursorPos, textSize, textColor)
  lineNr += 1
  cursorPos = (pad_x,(pad_y+lineNr*line_height))


def DrawTextWithTabs(surface, text1, indentLevel, text2, tab_distance, color1 = textColor, color2 = textColor):
  global cursorPos, pad_x, pad_y, lineNr

  cursorPos = (pad_x+(indentLevel*indentWidth),(pad_y+lineNr*line_height))
  cursorPos, label_size = Utils.DrawText2Surface(surface, text1, cursorPos, textSize, textColor)
  cursorPos, label_size = Utils.DrawText2Surface(surface, text2, (cursorPos[0]+tab_distance,cursorPos[1]), textSize, textColor)
  lineNr += 1
  cursorPos = (pad_x,(pad_y+lineNr*line_height))


def CleanUp(game, parent):
  if (parent == game.window_fleet_info_identifier):
    game.GUI_expanded_fleets = []
  elif (parent == game.window_info_identifier):
    game.GUI_expanded_fleets2 = []

