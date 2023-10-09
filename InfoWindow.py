import pygame
import Utils


def Draw(game):
  if (game.reDraw_InfoWindow):
    game.Events.ClearClickables(parent=game.window_info_identifier)
    line_height = 20
    pad_x = pad_y = 5
    lineNr = 0
    game.window_info.fill(Utils.SUPER_DARK_GRAY)
    color = Utils.WHITE
    if (game.highlighted_fleet_ID in game.fleets):
      fleet = game.fleets[game.highlighted_fleet_ID]
      label_pos = (pad_x,(pad_y+lineNr*line_height))
      label_pos, label_size = Utils.DrawText2Surface(game.window_info,fleet['Name'],label_pos,15,color)
    elif (game.highlighted_body_ID in game.starSystems[game.currentSystem]['Stars']):
      body = game.starSystems[game.currentSystem]['Stars'][game.highlighted_body_ID]
      #prefix = Utils.StarTypes[body['BodyClass']]+' '
      prefix = Utils.GetStarDescription(body) + ' '
      label_pos = (pad_x,(pad_y+lineNr*line_height))
      label_pos, label_size = Utils.DrawText2Surface(game.window_info,prefix+body['Name'],label_pos,15,color)
      lineNr+=1
      label_pos = (pad_x,(pad_y+lineNr*line_height))
      label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Radius:',label_pos,15,color)
      label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
      label_pos2, label_size = Utils.DrawText2Surface(game.window_info,str(body['Radius']),label_pos2,15,color)
      lineNr+=1
      label_pos = (pad_x,(pad_y+lineNr*line_height))
      label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Mass:',label_pos,15,color)
      label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
      label_pos2, label_size = Utils.DrawText2Surface(game.window_info,str(body['Mass']),label_pos2,15,color)
      lineNr+=1
      label_pos = (pad_x,(pad_y+lineNr*line_height))
      label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Temp:',label_pos,15,color)
      label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
      label_pos2, label_size = Utils.DrawText2Surface(game.window_info,str(body['Temp'])+'K',label_pos2,15,color)
      lineNr+=1
      label_pos = (pad_x,(pad_y+lineNr*line_height))
      label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Luminosity:',label_pos,15,color)
      label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
      label_pos2, label_size = Utils.DrawText2Surface(game.window_info,str(body['Luminosity'])+' Suns',label_pos2,15,color)
      lineNr+=1
      if (body['BodyClass'] in Utils.SpectralColors):
        col = Utils.SpectralColors[body['BodyClass']]
        label_pos = (pad_x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Color:',label_pos,15,color)
        label_pos2 = (pad_x+80,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,col,label_pos2,15,color)
    elif (game.highlighted_body_ID in game.systemBodies):
      body = game.systemBodies[game.highlighted_body_ID]
      label_pos = (pad_x,(pad_y+lineNr*line_height))
      if (body['Class'] == 'Asteroid' or body['Class'] == 'Comet' or body['Class'] == 'Moon'):
        name = body['Name']
        if (body['Class'] == 'Comet' and name.find('Comet') == -1):
          name = 'Comet '+name
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,name+(' (Unsurveyed)' if body['Unsurveyed'] else ''),label_pos,15,color)
      else:
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,body['Class']+' '+body['Name']+(' (Unsurveyed)' if body['Unsurveyed'] else ''),label_pos,15,color)
        
      # Physical body info
      lineNr+=1
      x = label_pos[0]
      label_pos = (x,(pad_y+lineNr*line_height))
      expRect = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
      game.MakeClickable(game.info_category_physical, expRect, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_physical, parent = game.window_info_identifier, anchor=game.window_info_anchor)
      label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
      label_pos, label_size = Utils.DrawText2Surface(game.window_info,game.info_category_physical,label_pos,15,color)
      if (game.info_cat_phys_expanded):
        lat_offs = 130
        lineNr+=1
        x = label_pos[0]+pad_x
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Type:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,body['Type'],label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Radius:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,str(body['RadiusBody'])+' km',label_pos2,15,color)
        lineNr+=1
        if (body['ColonyCost']):
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Colony Cost:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%2.3f'%body['ColonyCost'],label_pos2,15,color)
          lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Pop Capacity:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,f"{body['Population Capacity']:,} M",label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Gravity:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%s x Earth'%Utils.GetFormattedNumber(body['Gravity']),label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Mass:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%s x Earth'%Utils.GetFormattedNumber(body['Mass']),label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Orbit:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%s AU'%Utils.GetFormattedNumber(body['Orbit']),label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Year:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,Utils.GetTimeScale(body['HoursPerYear']),label_pos2,15,color)
        if (body['Class'] != 'Comet'):
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Day:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(game.window_info,Utils.GetTimeScale(body['HoursPerDay'])+(' - tidal locked' if body['Tidal locked'] else ''), label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Temperature:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%d C'%(int(body['Temperature'])),label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Atmosphere:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,('%s atm'%Utils.GetFormattedNumber(body['AtmosPressure'])) if body['AtmosPressure'] > 0 else '-',label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Hydrosphere:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,('%s'%Utils.GetFormattedNumber(body['Hydrosphere'])) if body['AtmosPressure'] > 0 else '-',label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Magnetic Field:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,('%s'%Utils.GetFormattedNumber(body['MagneticField'])) if body['MagneticField'] > 0 else '-',label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Density:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%s'%Utils.GetFormattedNumber(body['Density']),label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Escape Velocity:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%s m/s'%Utils.GetFormattedNumber(body['EscapeVelocity']),label_pos2,15,color)
        lineNr+=1
        label_pos = (x,(pad_y+lineNr*line_height))
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Greenhouse Factor:',label_pos,15,color)
        label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
        label_pos2, label_size = Utils.DrawText2Surface(game.window_info,('%s'%Utils.GetFormattedNumber(body['GHFactor'])) if body['AtmosPressure'] > 0 else '-',label_pos2,15,color)

      # Economical body info
      if (game.highlighted_body_ID in game.colonies):
        colony = game.colonies[game.highlighted_body_ID]
        lineNr+=1
        x = pad_x
        label_pos = (x,(pad_y+lineNr*line_height))
        expRect1 = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
        game.MakeClickable(game.info_category_economical, expRect1, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_economical, parent = game.window_info_identifier, anchor=game.window_info_anchor)
        label_pos = (expRect1[0]+expRect1[2]+5,label_pos[1])
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,game.info_category_economical,label_pos,15,color)
        if (game.info_cat_eco_expanded):
          lat_offs = 140
          lineNr+=1
          x = label_pos[0]+pad_x
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Population:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(game.window_info,str(colony['Pop']),label_pos2,15,color)
          lineNr+=1
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
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Population Supported:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(game.window_info,f"{round(supported_pop,2):,} M",label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Annual Growth:',label_pos,15,color)
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%1.2f%%'%(0),label_pos2,15,color)
          lineNr+=1
          label_pos = (x,(pad_y+lineNr*line_height))
          label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Protection:',label_pos,15,color)
          req = 0
          act = 0
          label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
          label_pos2, label_size = Utils.DrawText2Surface(game.window_info,'%d / %d'%(act,req),label_pos2,15,Utils.MED_GREEN if act >= req else Utils.RED)

          if (colony['Stockpile']['Sum'] > 0 or colony['Stockpile']['Sum of Minerals'] > 0):
            lineNr+=1
            x = expRect1[0]+expRect1[2]+5
            label_pos = (x,(pad_y+lineNr*line_height))
            #label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Stockpile',label_pos,15,color)
            expRect2 = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
            game.MakeClickable(game.info_category_stockpile, expRect2, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_stockpile, parent = game.window_info_identifier, anchor=game.window_info_anchor)
            label_pos = (expRect2[0]+expRect2[2]+5,label_pos[1])
            label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Stockpile',label_pos,15,color)
            if (game.info_cat_stock_expanded):
              lat_offs = 70
              x = expRect2[0]+expRect2[2]+5
              lineNr+=1
              if (colony['Stockpile']['Sum'] > 0):
                label_pos = (x,(pad_y+lineNr*line_height))
                label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Fuel:',label_pos,15,color)
                label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
                label_pos2, label_size = Utils.DrawText2Surface(game.window_info,f"{colony['Stockpile']['Fuel']:,}",label_pos2,15,color)
                lineNr+=1
                label_pos = (x,(pad_y+lineNr*line_height))
                label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Supplies:',label_pos,15,color)
                label_pos2 = (x+lat_offs,(pad_y+lineNr*line_height))
                label_pos2, label_size = Utils.DrawText2Surface(game.window_info,f"{colony['Stockpile']['Supplies']:,}",label_pos2,15,color)
                lineNr+=1
              if (colony['Stockpile']['Sum of Minerals'] > 0):
                lat_offs2 = 30
                for index in Utils.MineralNames:
                  mineral = Utils.MineralNames[index]
                  amount = colony['Stockpile'][mineral]
                  label_pos = (x,(pad_y+lineNr*line_height))
                  label_pos, label_size = Utils.DrawText2Surface(game.window_info,'%s:'%mineral[:2],label_pos,15,color)
                  label_pos2 = (x+lat_offs2,(pad_y+lineNr*line_height))
                  label_pos2, label_size = Utils.DrawText2Surface(game.window_info,f"{amount:,}",label_pos2,15,color)
                  lineNr+=1
                  if (index == 6):
                    lineNr -= 6
                    x += 100
          
          lineNr+=1
          # installations
          if (found_Installations):
            x = expRect1[0]+expRect1[2]+5
            label_pos = (x,(pad_y+lineNr*line_height))
            #label_pos, label_size = Utils.DrawText2Surface(game.window_info,'Stockpile',label_pos,15,color)
            expRect2 = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
            game.MakeClickable(game.info_category_installations, expRect2, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_installations, parent = game.window_info_identifier, anchor=game.window_info_anchor)
            label_pos = (expRect2[0]+expRect2[2]+5,label_pos[1])
            label_pos, label_size = Utils.DrawText2Surface(game.window_info,game.info_category_installations,label_pos,15,color)
            lineNr+=1
            if (game.info_cat_inst_expanded):
              x = expRect2[0]+expRect2[2]+5
              for InstallationID in colony['Installations']:
                installation = colony['Installations'][InstallationID]
                name = installation['Name']
                amount = installation['Amount']
                if (installation['Amount'] > 0):
                  lat_offs2 = 40
                  label_pos = (x,(pad_y+lineNr*line_height))
                  label_pos, label_size = Utils.DrawText2Surface(game.window_info,'%4d'%amount,label_pos,15,color)
                  label_pos2 = (x+lat_offs2,(pad_y+lineNr*line_height))
                  label_pos2, label_size = Utils.DrawText2Surface(game.window_info,name,label_pos2,15,color)
                  lineNr+=1
                  #if (index == 6):
                  #  lineNr -= 6
                  #  x += 100
        
      fleetsInOrbit = False
      for fleetID in game.fleets[game.currentSystem]:
        fleet = game.fleets[game.currentSystem][fleetID]
        if (fleet['Orbit']['Body'] == game.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
          fleetsInOrbit = True
          break
      if fleetsInOrbit:
        if (not game.info_cat_eco_expanded):
          lineNr+=1
        x = pad_x
        label_pos = (x,(pad_y+lineNr*line_height))
        expRect = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
        game.MakeClickable(game.info_category_orbit, expRect, left_click_call_back = game.ExpandBodyInfo, par=game.info_category_orbit, parent = game.window_info_identifier, anchor=game.window_info_anchor)
        label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
        label_pos, label_size = Utils.DrawText2Surface(game.window_info,game.info_category_orbit,label_pos,15,color)
        lineNr+=1
        orbitFleetTopRow = lineNr
        pygame.draw.line(game.window_info, Utils.WHITE, (x,(pad_y+lineNr*line_height-2)),((x+200,(pad_y+lineNr*line_height-2))),1)
        lineNr+=game.window_info_scoll_pos
        if (game.info_cat_orbit_expanded):
          x = label_pos[0] if label_pos else (expRect[0]+expRect[2]+5)
          # orbiting fleets
          for fleetID in game.fleets[game.currentSystem]:
            fleet = game.fleets[game.currentSystem][fleetID]
            if (fleet['Orbit']['Body'] == game.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
              if (lineNr >= orbitFleetTopRow):
                color = Utils.WHITE
                label_pos = (x,(pad_y+lineNr*line_height))
                if (fleet['Ships'] != []):
                  expRect = Utils.DrawExpander(game.window_info, (label_pos[0],label_pos[1]+3), 15, color)
                  game.MakeClickable(fleet['Name'], expRect, left_click_call_back = game.ExpandFleet, par=fleetID, parent = game.window_info_identifier, anchor=game.window_info_anchor)
                else:
                  expRect = pygame.draw.rect(game.window_info, color, (label_pos[0]+1,label_pos[1]+3+1, 15-2, 15-2), 1)
                label_pos = (expRect[0]+expRect[2]+5,label_pos[1])
                label_pos, label_size = Utils.DrawText2Surface(game.window_info,fleet['Name']+ ' - ',label_pos,15,color)
                if (label_pos):
                  game.MakeClickable(fleet['Name'], (label_pos[0],label_pos[1], label_size[0],label_size[1]), left_click_call_back = game.Select_Fleet, par=fleetID, parent = game.window_info_identifier, anchor=game.window_info_anchor)
                  p = 0
                  icon_pos = (label_pos[0]+label_size[0], label_pos[1])
                  if (fleet['Fuel Capacity'] > 0):
                    p = fleet['Fuel']/fleet['Fuel Capacity']

                  if ('fuel2' in game.images_GUI):
                    icon_rect = Utils.DrawPercentageFilledImage(game.window_info, 
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
                    icon_rect = Utils.DrawPercentageFilledImage(game.window_info, 
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

                if (fleetID in game.GUI_expanded_fleets2):
                  shipClasses = {}
                  for ship in fleet['Ships']:
                    if (ship['ClassName'] not in shipClasses):
                      shipClasses[ship['ClassName']] = 1
                    else:
                      shipClasses[ship['ClassName']] += 1
                  for shipClass in shipClasses:
                    label_pos = (expRect[0]+expRect[2]+5,(pad_y+lineNr*line_height))
                    label_pos, label_size = Utils.DrawText2Surface(game.window_info,'%dx%s'%(shipClasses[ship['ClassName']],shipClass),label_pos,15,color)
                    lineNr +=1
              else:
                lineNr +=1

    game.surface.blit(game.window_info,game.window_info_anchor)
    game.reDraw_InfoWindow = False
    return True
  else:
    return False


def CleanUp(game, parent):
  if (parent == game.window_fleet_info_identifier):
    game.GUI_expanded_fleets = []
  elif (parent == game.window_info_identifier):
    game.GUI_expanded_fleets2 = []

