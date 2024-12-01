import Table
import pygame
import Utils
import Events
import GUI
import Systems
from Screen import Screen
from operator import itemgetter

class ColonyDetailsScreen(Screen):
  def __init__(self, game, events, name):
    self.reDraw = True
    self.reDraw_GUI = True
    self.name = name
    self.game = game
    self.width = game.width
    self.height = game.height
    self.surface = game.surface
    self.screenCenterBeforeDrag = self.game.screenCenter
    self.FPS = 0
    self.counter_FPS = 0
    self.timestampLastSecond = pygame.time.get_ticks()
    self.timestampLast = pygame.time.get_ticks()
    
    self.cameraCenter = (self.width/2,self.height/2)
    self.screenCenter = (self.width/2,self.height/2)

    self.mouseDragged = (0,0)
    # Options
    self.Events = events
    self.surface = game.surface
    self.screen = game.screen
    self.bg_color = game.bg_color

    self.GUI_Elements = {}
    self.images_GUI = {}
    self.systemID = 12222
    #self.colonyID = None
    self.bodyID = 1095632

    self.cursorPos = (100,100)
    self.pad_x = 5
    self.pad_y = 5
    self.lineNr = 0
    self.unscrollableLineNr = 0
    self.indentWidth = 17
    self.line_height = 20
    self.textSize = 14
    self.anchor = (20,250)

  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      reblit |= self.DrawColony()

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit


  def DrawColony(self):
    body = None
    colony = None
    if (self.systemID is None) or (self.bodyID is None):
      return False
    if (self.bodyID in self.game.systemBodies):
      body = self.game.systemBodies[self.bodyID]
    if (self.bodyID in self.game.colonies):
      colony = self.game.colonies[self.bodyID]
    if (body is None):# or (colony is None):
      return False
    
    scale = (200,200)
    scaledSurface = pygame.transform.smoothscale(body['Image'],scale)
      
    self.surface.blit(scaledSurface,(30,50))

    self.lineNr = 0
    if (body['Class'] == 'Asteroid' or body['Class'] == 'Comet' or body['Class'] == 'Moon'):
      name = body['Name']
      if (body['Class'] == 'Comet' and name.find('Comet') == -1):
        name = 'Comet '+name+(' (Unsurveyed)' if body['Unsurveyed'] else '')
    else:
      name = body['Class']+' '+body['Name']+(' (Unsurveyed)' if body['Unsurveyed'] else '')

    name += ' in ' + Systems.GetSystemName(self.game, self.systemID)
    self.DrawLineOfText(self.surface, name, 0, unscrollable = True, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Type:', 0, str(body['Type']), 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Radius:', 0, str(body['RadiusBody'])+' km', 130, anchor = self.anchor)
    if (body['ColonyCost']):
      self.DrawTextWithTabs(self.surface, 'Colony Cost:', 0, '%2.3f'%body['ColonyCost'], 130, anchor = self.anchor)
    pop_text = '-'
    tf_text = '-'
    if (colony):
      pop_text = f"{colony['Pop']:,} M"
      tf_text = 'Yes' if colony['Terraforming']['State'] else '-'
    self.DrawTextWithTabs(self.surface, 'Population:', 0, pop_text, 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Pop Capacity:', 0, f"{body['Population Capacity']:,} M", 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Gravity:', 0, '%s x Earth'%Utils.GetFormattedNumber(body['Gravity']), 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Mass:', 0, '%s x Earth'%Utils.GetFormattedNumber(body['Mass']), 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Orbit:', 0, '%s AU'%Utils.GetFormattedNumber(body['Orbit']), 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Year:', 0, Utils.GetTimeScale(body['HoursPerYear']), 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Day:', 0, Utils.GetTimeScale(body['HoursPerDay'])+(' - tidal locked' if body['Tidal locked'] else ''), 130, anchor = self.anchor)
    parentBody_str = ''
    parentID = body['ParentID']
    if (parentID in self.game.systemBodies):
      parentBody = self.game.systemBodies[parentID]
      parentBody_str = parentBody['Class'] + ' ' + parentBody['Name']
    else:
      system = self.game.starSystems[self.game.currentSystem]
      for starID in system['Stars']:
        if (starID == parentID) or (len(system['Stars'])==1):
          star = system['Stars'][starID]
          parentBody_str = 'Star ' + star['Name'] + ' ' + star['Suffix']
          
    self.DrawTextWithTabs(self.surface, 'Orbiting:', 0, parentBody_str, 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Orbit Radius:', 0, '%s AU'%Utils.GetFormattedNumber(body['Orbit']), 130, anchor = self.anchor)
    if (colony):
      if (colony['Terraforming']['State']):
        self.DrawTextWithTabs(self.surface, 'Terraforming Active:', 0, tf_text, 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Temperature:', 0, '%d C'%(int(body['Temperature'])), 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Atmosphere:', 0, ('%s atm'%Utils.GetFormattedNumber(body['AtmosPressure'])) if body['AtmosPressure'] > 0 else '-', 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Hydrosphere:', 0, ('%s'%Utils.GetFormattedNumber(body['Hydrosphere'])) if body['AtmosPressure'] > 0 else '-', 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Magnetic Field:', 0, ('%s'%Utils.GetFormattedNumber(body['MagneticField'])) if body['MagneticField'] > 0 else '-',130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Density:', 0, '%s'%Utils.GetFormattedNumber(body['Density']), 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Escape Velocity:', 0, '%s m/s'%Utils.GetFormattedNumber(body['EscapeVelocity']), 130, anchor = self.anchor)
    self.DrawTextWithTabs(self.surface, 'Greenhouse Factor:', 0, ('%s'%Utils.GetFormattedNumber(body['GHFactor'])) if body['AtmosPressure'] > 0 else '-', 130, anchor = self.anchor)

    t1 = 100
    t2 = 180
    t3 = 230
    if (colony):
      self.DrawTextWithTabs(self.surface, 'Resource', 0, 'Deposit', t1, 0, text3 = '(Acc)', tab_dist2 = t2, tab_dist3 = t3, text4 = 'Stockpile', anchor = self.anchor)
    
      stock = f"{colony['Stockpile']['Fuel']:,}"
      if (stock == '0'):
        stock = '-'
      self.DrawTextWithTabs(self.surface, 'Fuel', 0, '-', t1, 0, text3 = '', tab_dist2 = t2, tab_dist3 = t3, text4 = stock, anchor = self.anchor)
      stock = f"{colony['Stockpile']['Supplies']:,}"
      if (stock == '0'):
        stock = '-'
      self.DrawTextWithTabs(self.surface, 'Supplies', 0, '-', t1, 0, text3 = '', tab_dist2 = t2, tab_dist3 = t3, text4 = stock, anchor = self.anchor)

    for i in Utils.MineralNames:
      mineral = Utils.MineralNames[i]
      deposit = 0
      acc = 0
      stock = 0
      if ('Deposits' in body):
        if (colony):
          stock = colony['Stockpile']['Fuel']
        if mineral in body['Deposits']:
          deposit = f"{int(Utils.Round(body['Deposits'][mineral]['Amount'],0)):,}"
          acc = '(%1.1f)'%Utils.Round(body['Deposits'][mineral]['Accessibility'],1)
          if (deposit == '0'):
            deposit = '-'
            acc = ''
          if (colony):
            stock = f"{colony['Stockpile'][mineral]:,}"
          if (stock == '0'):
            stock = '-'
      self.DrawTextWithTabs(self.surface, mineral, 0, deposit, t1, 0, text3 = acc, tab_dist2 = t2, tab_dist3 = t3, text4 = stock, anchor = self.anchor)

    return True


  def DrawLineOfText(self, surface, line, indentLevel, offset = 0, color = Utils.WHITE, unscrollable = False, window_info_scoll_pos = 0, anchor = (0,0)):
    label_size = None

    if (unscrollable) and (self.lineNr < self.unscrollableLineNr):
      self.cursorPos = (self.pad_x+(indentLevel*self.indentWidth)+offset+anchor[0], (self.pad_y+self.unscrollableLineNr*self.line_height)+anchor[1])
      self.unscrollableLineNr += 1
      self.cursorPos, label_size = Utils.DrawText2Surface(surface, line, cursorPos, self.textSize, color)
      self.lineNr += 1
      self.cursorPos = (self.pad_x+anchor[0],(self.pad_y+self.unscrollableLineNr*self.line_height)+anchor[1])
    elif (self.lineNr >= self.unscrollableLineNr):
      self.cursorPos = (self.pad_x+(indentLevel*self.indentWidth)+offset+anchor[0], (self.pad_y+(self.lineNr)*self.line_height)+anchor[1])
      self.cursorPos, label_size = Utils.DrawText2Surface(surface, line, self.cursorPos, self.textSize, color)
      self.lineNr += 1
      self.cursorPos = (self.pad_x+anchor[0], (self.pad_y+self.lineNr*self.line_height)+anchor[1])
    else:
      self.lineNr += 1

    return label_size


  def DrawTextWithTabs(self, surface, text1, indentLevel, text2, tab_distance, window_info_scoll_pos = 0, offset = 0, anchor = (0,0), color1 = Utils.WHITE, color2 = Utils.WHITE, text3 = None, tab_dist2 = 0, tab_dist3 = 0, text4 = None, color3 = Utils.WHITE,color4 = Utils.WHITE):
    label_size = None
  
    if (self.lineNr >= self.unscrollableLineNr):
      self.cursorPos = (self.pad_x+(indentLevel*self.indentWidth)+anchor[0],(self.pad_y+(self.lineNr)*self.line_height)+anchor[1])
      self.cursorPos, label_size = Utils.DrawText2Surface(surface, text1, self.cursorPos, self.textSize, color1)
      if (self.cursorPos):
        self.cursorPos, label_size = Utils.DrawText2Surface(surface, text2, (self.cursorPos[0]+tab_distance,self.cursorPos[1]), self.textSize, color2)
  
      if (text3):
        self.cursorPos = (self.pad_x+(indentLevel*self.indentWidth)+offset+anchor[0],(self.pad_y+self.lineNr*self.line_height)+anchor[1])
        self.cursorPos, label_size = Utils.DrawText2Surface(surface, text3, (self.cursorPos[0]+tab_dist2,self.cursorPos[1]), self.textSize, color3)
        if (self.cursorPos) and (text4):
          self.cursorPos = (self.pad_x+(indentLevel*self.indentWidth)+offset+anchor[0],(self.pad_y+self.lineNr*self.line_height)+anchor[1])
          self.cursorPos, label_size = Utils.DrawText2Surface(surface, text4, (self.cursorPos[0]+tab_dist3,self.cursorPos[1]), self.textSize, color4)
      else:
        if (self.cursorPos) and (text4):
          self.cursorPos = (self.pad_x+(indentLevel*self.indentWidth)+offset+anchor[0],(self.pad_y+self.lineNr*self.line_height)+anchor[1])
          self.cursorPos, label_size = Utils.DrawText2Surface(surface, text4, (self.cursorPos[0]+tab_dist3,self.cursorPos[1]), self.textSize, color4)
      self.cursorPos = (self.pad_x+anchor[0],(self.pad_y+(self.lineNr+1)*self.line_height)+anchor[1])
    self.lineNr += 1

    return label_size

#  _indentLevel = 0
    #    elif (game.highlighted_body_ID in game.systemBodies):
    #      body = game.systemBodies[game.highlighted_body_ID]
    #      if (body['Class'] == 'Asteroid' or body['Class'] == 'Comet' or body['Class'] == 'Moon'):
    #        name = body['Name']
    #        if (body['Class'] == 'Comet' and name.find('Comet') == -1):
    #          name = 'Comet '+name+(' (Unsurveyed)' if body['Unsurveyed'] else '')
    #      else:
    #        name = body['Class']+' '+body['Name']+(' (Unsurveyed)' if body['Unsurveyed'] else '')
    #      DrawLineOfText(context.window_info, name, 0, unscrollable = True)

    #      if ('Deposits' in body):
    #        # Mineral Deposits info
    #        expRect = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
    #        game.MakeClickable(context.info_category_deposits, expRect, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_deposits, parent = context.window_info_identifier, anchor=context.window_info_anchor)
    #        DrawLineOfText(context.window_info, context.info_category_deposits, _indentLevel+1, unscrollable = True)

    #        if (context.info_cat_deposits_expanded):
    #          for mineral in body['Deposits']:
    #            amount = int(Utils.Round(body['Deposits'][mineral]['Amount'],0))
    #            acc = Utils.Round(body['Deposits'][mineral]['Accessibility'],1)
    #            if (amount > 0):
    #              DrawTextWithTabs(context.window_info, mineral[:2]+':', _indentLevel+1, f"{amount:,}", 30, context.window_info_scoll_pos, text3 = '('+str(acc)+')', color3 = Utils.LIGHT_GREEN if acc >= 0.7 else Utils.RED if acc <= 0.3 else Utils.YELLOW, tab_dist2 = 110)
        

    #      # Physical body info
    #      expRect = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
    #      game.MakeClickable(context.info_category_physical, expRect, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_physical, parent = context.window_info_identifier, anchor=context.window_info_anchor)
    #      DrawLineOfText(context.window_info, context.info_category_physical, _indentLevel+1, unscrollable = True)

    #      if (context.info_cat_phys_expanded):
    #        DrawTextWithTabs(context.window_info, 'Type:', _indentLevel+1, str(body['Type']), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Radius:', _indentLevel+1, str(body['RadiusBody'])+' km', 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Type:', _indentLevel+1, str(body['Type']), 130, context.window_info_scoll_pos)
    #        if (body['ColonyCost']):
    #          DrawTextWithTabs(context.window_info, 'Colony Cost:', _indentLevel+1, '%2.3f'%body['ColonyCost'], 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Pop Capacity:', _indentLevel+1, f"{body['Population Capacity']:,} M", 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Gravity:', _indentLevel+1, '%s x Earth'%Utils.GetFormattedNumber(body['Gravity']), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Mass:', _indentLevel+1, '%s x Earth'%Utils.GetFormattedNumber(body['Mass']), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Orbit:', _indentLevel+1, '%s AU'%Utils.GetFormattedNumber(body['Orbit']), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Year:', _indentLevel+1, Utils.GetTimeScale(body['HoursPerYear']), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Day:', _indentLevel+1, Utils.GetTimeScale(body['HoursPerDay'])+(' - tidal locked' if body['Tidal locked'] else ''), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Orbit:', _indentLevel+1, '%s AU'%Utils.GetFormattedNumber(body['Orbit']), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Temperature:', _indentLevel+1, '%d C'%(int(body['Temperature'])), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Atmosphere:', _indentLevel+1, ('%s atm'%Utils.GetFormattedNumber(body['AtmosPressure'])) if body['AtmosPressure'] > 0 else '-', 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Hydrosphere:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['Hydrosphere'])) if body['AtmosPressure'] > 0 else '-', 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Magnetic Field:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['MagneticField'])) if body['MagneticField'] > 0 else '-',130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Density:', _indentLevel+1, '%s'%Utils.GetFormattedNumber(body['Density']), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Escape Velocity:', _indentLevel+1, '%s m/s'%Utils.GetFormattedNumber(body['EscapeVelocity']), 130, context.window_info_scoll_pos)
    #        DrawTextWithTabs(context.window_info, 'Greenhouse Factor:', _indentLevel+1, ('%s'%Utils.GetFormattedNumber(body['GHFactor'])) if body['AtmosPressure'] > 0 else '-', 130, context.window_info_scoll_pos)

    #      # Economical body info
    #      if (game.highlighted_body_ID in game.colonies):
    #        colony = game.colonies[game.highlighted_body_ID]

    #        expRect1 = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
    #        game.MakeClickable(context.info_category_economical, expRect1, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_economical, parent = context.window_info_identifier, anchor=context.window_info_anchor)
    #        DrawLineOfText(context.window_info, context.info_category_economical, _indentLevel+1, unscrollable = True)
    #        if (context.info_cat_eco_expanded):
    #          DrawTextWithTabs(context.window_info, 'Population:', _indentLevel+1, str(colony['Pop']), 130, context.window_info_scoll_pos)
    #          supported_pop = 0
    #          found_Installations = False
    #          for installationID in colony['Installations']:
    #            amountInstallations = colony['Installations'][installationID]['Amount']
    #            if (amountInstallations > 0):
    #              found_Installations = True
    #            if (colony['Installations'][installationID]['Name'] == 'Infrastructure'):
    #              colonyCost = colony['ColonyCost'] * (1-game.cc_cost_reduction)
    #              if (colonyCost == 0):
    #                supported_pop = body['Population Capacity']
    #              else:
    #                supported_pop = amountInstallations / colonyCost / 100
    #              if (found_Installations):
    #                break
    #          DrawTextWithTabs(context.window_info, 'Popul. Supported:', _indentLevel+1, f"{Utils.Round(supported_pop,2):,} M", 130, context.window_info_scoll_pos)
    #          #DrawTextWithTabs(context.window_info, 'Annual Growth:', _indentLevel+1, '%1.2f%%'%(0), 130)
    #          req = 0
    #          act = 0
    #          DrawTextWithTabs(context.window_info, 'Protection:', _indentLevel+1, '%d / %d'%(act,req), 130, context.window_info_scoll_pos, color2=(Utils.MED_GREEN if act >= req else Utils.RED))

    #          if (colony['Stockpile']['Sum'] > 0 or colony['Stockpile']['Sum of Minerals'] > 0):
    #            cursorPos = (cursorPos[0]+indentWidth, cursorPos[1])
    #            expRect2 = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
    #            game.MakeClickable(context.info_category_stockpile, expRect2, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_stockpile, parent = context.window_info_identifier, anchor=context.window_info_anchor)
    #            DrawLineOfText(context.window_info, 'Stockpile', _indentLevel+2, unscrollable = True)
    #            if (context.info_cat_stock_expanded):
    #              if (colony['Stockpile']['Sum'] > 0):
    #                DrawTextWithTabs(context.window_info, 'Fuel:', _indentLevel+2, f"{colony['Stockpile']['Fuel']:,}", 70, context.window_info_scoll_pos)
    #                DrawTextWithTabs(context.window_info, 'Supplies:', _indentLevel+2, f"{colony['Stockpile']['Supplies']:,}", 70, context.window_info_scoll_pos)
    #              if (colony['Stockpile']['Sum of Minerals'] > 0):
    #                index = 1
    #                while (index+1 in Utils.MineralNames):
    #                  mineral = Utils.MineralNames[index]
    #                  amount = colony['Stockpile'][mineral]
    #                  mineral2 = Utils.MineralNames[index+1]
    #                  amount2 = colony['Stockpile'][mineral]
    #                  DrawTextWithTabs(context.window_info, '%s:'%mineral[:2], _indentLevel+2, f"{amount:,}", 30, context.window_info_scoll_pos, text3 = '%s:'%mineral2[:2], tab_dist2 = 100, text4 = f"{amount2:,}")
    #                  index+=2
    #                if (index in Utils.MineralNames):
    #                  mineral = Utils.MineralNames[index]
    #                  amount = colony['Stockpile'][mineral]
    #                  DrawTextWithTabs(context.window_info, '%s:'%mineral[:2], _indentLevel+2, f"{amount:,}", 30, context.window_info_scoll_pos)

    #          # installations
    #          if (found_Installations):
    #            cursorPos = (cursorPos[0]+indentWidth, cursorPos[1])
    #            expRect2 = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
    #            game.MakeClickable(context.info_category_installations, expRect2, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_installations, parent = context.window_info_identifier, anchor=context.window_info_anchor)
    #            DrawLineOfText(context.window_info, context.info_category_installations, _indentLevel+2, unscrollable = True)
    #            if (context.info_cat_inst_expanded):
    #              for InstallationID in colony['Installations']:
    #                installation = colony['Installations'][InstallationID]
    #                name = installation['Name']
    #                amount = installation['Amount']
    #                if (installation['Amount'] > 0):
    #                  DrawTextWithTabs(context.window_info, '%4d'%amount, _indentLevel+1, name, 40, context.window_info_scoll_pos)
        
    #      fleetsInOrbit = False
    #      for fleetID in game.fleets[game.currentSystem]:
    #        fleet = game.fleets[game.currentSystem][fleetID]
    #        if (fleet['Orbit']['Body'] == game.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
    #          fleetsInOrbit = True
    #          break
    #      if fleetsInOrbit:
    #        #if (not context.info_cat_eco_expanded):
    #        cursorPos = (cursorPos[0], cursorPos[1])
    #        expRect = Utils.DrawExpander(context.window_info, (cursorPos[0],cursorPos[1]+3), textSize, textColor)
    #        game.MakeClickable(context.info_category_orbit, expRect, left_click_call_back = context.ExpandBodyInfo, par=context.info_category_orbit, parent = context.window_info_identifier, anchor=context.window_info_anchor)
    #        DrawLineOfText(context.window_info, context.info_category_orbit, _indentLevel+1, unscrollable = True)
    #        pygame.draw.line(context.window_info, Utils.WHITE, (cursorPos[0],cursorPos[1]-2),(cursorPos[0]+200,cursorPos[1]-2),1)
    #        if (context.info_cat_orbit_expanded):
    #          # orbiting fleets
    #          for fleetID in game.fleets[game.currentSystem]:
    #            fleet = game.fleets[game.currentSystem][fleetID]
    #            if (fleet['Orbit']['Body'] == game.highlighted_body_ID and fleet['Orbit']['Distance'] == 0):
    #              DrawFleet(context, fleet, _indentLevel)

    #  context.surface.blit(context.window_info, context.window_info_anchor)
    #  context.reDraw_InfoWindow = False
    #  return True
    #else:
    #  return False