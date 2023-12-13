import Table
import pygame
import Utils
import Events
import GUI
from Screen import Screen
from operator import itemgetter
import Utils
import Colonies
import Bodies
import Fleets
import Systems
from math import pi as PI

class ColoniesScreen(Screen):
  def __init__(self, game, events, name):
    self.reDraw = True
    self.reDraw_GUI = True
    self.name = name
    self.game = game
    self.width = game.width
    self.height = game.height

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

    self.GUI_Button_Size = (100,30)
    self.GUI_Elements = {}
    self.GUI_identifier = 'Colonies'
    self.images_GUI = {}
    self.table = Table.Table(self, 1, 35, anchor = (20,60), max_rows=15, col_widths = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10])

    self.GUI_Table_Header_Anchor = self.table.anchor
    self.GUI_Table_identifier = 'Colonies Table'
    self.GUI_Table_radioGroup = 1
    self.GUI_identifier = 'Colonies Screen'
    self.GUI_Bottom_Anchor = (525, game.height-50)
    self.GUI_table_ID = 0
    self.GUI_ID_dropdown_systems = 1
    self.GUI_ID_dropdown_designations = 2
    self.selectedBodyName = None
    self.selectedRow = -1

    self.hideNoTerraformingActive = False
    self.hideCivilian = True
    self.hideHighCCBodies = False
    self.hideComets = True
    self.hideAsteroids = True

    self.breatheGas = 'Oxygen'
    self.breatheMinAtm = 0.1
    self.breatheMaxAtm = 0.3
    self.safeLevel = 30
    self.maxAtm = 4
    self.minTemp = -10
    self.maxTemp = 38
    self.breathableGasAtmCol = 0
    self.breathableGasLevelCol = 0
    self.tableFirstGasColumn = 0
    self.tableLastGasColumn = 0
    self.FormatTable(self.table)
    self.table.Scrollbar()

    self.pad_x = 5
    self.pad_y = 5
    self.lineNr = 0
    self.unscrollableLineNr = 0
    self.indentWidth = 17
    self.line_height = 20
    self.textSize = 14

    self.tab1 = 200
    self.tab2 = self.tab1+150
    self.tab3 = self.tab2+100
    self.tab4 = self.tab3+80
    self.tab5 = 80
    self.tab6 = 120
    self.bodies = {}

  def FormatTable(self, table):
    color_red = Utils.RED
    color_blue = Utils.LIGHT_BLUE
    color_green = Utils.LIGHT_GREEN
    table.AddFormat(0, {'Operation':'Align', 'value':'center'} )
    #header = ['AU', 'Name', 'System', 'Pop/Sup', 'Cost', 'Terraforming', 'Workers', 'Unemployed', 'Mines (M/A)', 'MassDrv', 'Fuel Ml', 'Refuel Station', 'Supplies', 'Cargo Station', 'Spaceport', 'Unrest']
    for i in range(1,table.num_cols):
      table.AddFormat(i, {'Operation':'Align', 'value':'center'} )
      if i in [6,12,14,15]:
        table.AddFormat(i, {'Operation':'Below', 'threshold':True, 'text_color':Utils.WHITE, 'else_color':color_green} )
      if i == 4:
        table.AddFormat(i, {'Operation':'Above', 'threshold':3, 'text_color':Utils.RED, 'else_color':color_green} )

    #table.AddFormat(4, {'Operation':'Align', 'value':'center'} )
    #table.AddFormat(5, {'Operation':'Align', 'value':'center'} )
    #table.AddFormat(6, {'Operation':'Align', 'value':'center'} )
    
    #last_index = 4
    #gasIndex = 1
    #self.tableFirstGasColumn = last_index+gasIndex
    #for gasID in self.game.gases:
    #  if (gasID > 0):
    #    if (self.game.gases[gasID]['Name'] == 'Oxygen'):
    #      table.AddFormat(last_index+gasIndex, {'Operation':'Between', 'threshold_low':self.breatheMinAtm, 
    #                                                'threshold_high':self.breatheMaxAtm, 
    #                                                'text_color':color_green, 
    #                                                'too_low_color': color_blue, 
    #                                                'too_high_color':color_red} )
    #      table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center'} )
    #      self.breathableGasAtmCol = last_index+gasIndex
    #      gasIndex+=1
    #      table.AddFormat(last_index+gasIndex, {'Operation':'Above', 'threshold':self.safeLevel, 'text_color':color_red, 'else_color':color_green} )
    #      self.breathableGasLevelCol = last_index+gasIndex
    #    else:
    #      if (self.game.gases[gasID]['DangerousLevel'] > 0):
    #        table.AddFormat(last_index+gasIndex, {'Operation':'Above', 'threshold':self.game.gases[gasID]['DangerousLevel'], 'text_color':color_red, 'else_color':color_green} )
    #    table.AddFormat(last_index+gasIndex, {'Format':'Percent','Operation':'Align', 'value':'center'} )
    #    gasIndex+=1
    #self.tableLastGasColumn = last_index+gasIndex-1
    #table.AddFormat(last_index+gasIndex, {'Operation':'Below', 'threshold':self.maxAtm, 'text_color':color_green, 'else_color':color_red} )
    #table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center'} )
    #gasIndex+=1
    #table.AddFormat(last_index+gasIndex, {'Operation':'Between',  'threshold_low':self.minTemp,
    #                                                              'threshold_high':self.maxTemp, 
    #                                                              'text_color':color_green, 
    #                                                              'too_low_color': color_blue, 
    #                                                              'too_high_color':color_red} )

    #table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center'} )
    #gasIndex+=1
    #table.AddFormat(last_index+gasIndex, {'Operation':'Below', 'threshold':20, 'text_color':color_blue, 'else_color':color_green} )
    #table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center'} )
    #gasIndex+=1
    ##table.AddFormat(last_index+gasIndex, {'Operation':'Between',  'threshold_low':0.99,
    ##                                                              'threshold_high':1.01, 
    ##                                                              'text_color':color_green, 
    ##                                                              'too_low_color': color_blue, 
    ##                                                              'too_high_color':color_red} )
    #table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center'} )
    #gasIndex+=1
    #table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center'} )
    #gasIndex+=1
    #table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center'} )
    #gasIndex+=1
    #table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center'} )
    #gasIndex+=1
    #table.AddFormat(last_index+gasIndex, {'Operation':'Align', 'value':'center', 'Suffix':' a'} )
    #table.AddFormat(last_index+gasIndex, {'Operation':'Above', 'threshold':100, 'text_color':color_red, 'else_color':Utils.WHITE} )
    

  def InitGUI(self):
    self.table.scrollbar.clickable.enabled = True
    idGUI = 0
    reverse_order_columns = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]
    col_index = 0
    for cell in self.table.cells[0]:
      gui_cl = self.game.MakeClickable(cell.value, cell.rect, self.SortTableGUI, par=idGUI, parent=self.GUI_Table_identifier)
      self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, cell.value, cell.rect, gui_cl, 'Button', enabled = True if idGUI == 0 else False, radioButton = True, radioGroup = self.GUI_Table_radioGroup, state = 1 if (col_index in reverse_order_columns) else 0)
      idGUI += 1
      col_index += 1

    gui_cl = self.game.MakeClickable('Complete Colonies Table', self.table.rect, self.GetBodyFromInsideTable, parent='Complete Colonies Table')
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, self.GUI_Table_identifier, self.table.rect, gui_cl, 'Button')
    self.GUI_table_ID = idGUI
    idGUI += 1

    #x = self.GUI_Bottom_Anchor[0] - 275
    #y = self.GUI_Bottom_Anchor[1] + 3
    #bb = (x,y,250,25)
    #gui_cl = self.game.MakeClickable('Development Dropdown', bb, self.OpenSystemDropdown, parent='Development Dropdown')
    #systemNames = Systems.GetKnownSystemNames(self.game)
    #self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, 'Development', bb, gui_cl, 'Dropdown', content = systemNames, dropUp = True, showLabel = True)
    #self.GUI_ID_dropdown_systems = idGUI
    #self.GUI_Elements[idGUI].dropdownSelection = Systems.GetIndexOfCurrentSystem(self.game)
    #idGUI += 1

    size = 32
    x = self.GUI_Bottom_Anchor[0]
    y = self.GUI_Bottom_Anchor[1]
    bb = (x,y,size,size)
    name = 'Colonies'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.hideNoTerraformingActive, tooltip='Hide with no terraforming')
    self.GUI_Elements[idGUI].SetImages(self.game.images_GUI, 'no_TF_enabled', 'no_TF_disabled')
    #no_TF_disabled.png
    #no_TF_disabled.png

    idGUI += 1
    x += size+5
    bb = (x,y,size,size)
    name = 'Civilian'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', enabled = self.hideCivilian, tooltip='Hide civilian colonies')
    self.GUI_Elements[idGUI].SetImages(self.game.images_GUI, 'no_civilian_enabled', 'no_civilian_disabled')

    idGUI += 1
    x += size+5
    bb = (x,y,size,size)
    name = 'High ColonyCost'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', enabled = self.hideHighCCBodies, tooltip='Hide high colony costs')
    self.GUI_Elements[idGUI].SetImages(self.game.images_GUI, 'no_highcc_enabled', 'no_highcc_disabled')
    
    idGUI += 1
    x += size+5
    bb = (x,y,size,size)
    name = 'Comets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', enabled = self.hideComets, tooltip='Hide comets')
    self.GUI_Elements[idGUI].SetImages(self.game.images_GUI, 'no_comet_enabled', 'no_comet_disabled')

    idGUI += 1
    x += size+5
    bb = (x,y,size,size)
    name = 'Asteroids'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', enabled = self.hideAsteroids, tooltip='Hide asteroids')
    self.GUI_Elements[idGUI].SetImages(self.game.images_GUI, 'no_asteroid_enabled', 'no_asteroid_disabled')


  def RefreshData(self):
    self.UpdateTable()


  def UpdateGUI(self):
    for i in range(len(self.table.cells[0])):
      self.GUI_Elements[i].rect = self.table.cells[0][i].rect
      self.GUI_Elements[i].clickable.rect = self.table.cells[0][i].rect
    self.GUI_Elements[self.GUI_table_ID].rect = self.table.rect


  def UpdateTable(self):
    t1 = pygame.time.get_ticks()
    self.table.Clear()

    text_widths = []
    unsortedIDs = []
    #self.table.max_cell_sizes = []
    index = 1
    systems = {}
    surfAreaEarth =  511185932.52
    for colonyID in self.game.colonies:
      colony = self.game.colonies[colonyID]
      if colony['SystemID'] not in systems:
        systems[colony['SystemID']] = []
      systems[colony['SystemID']].append(colonyID)

    for systemID in systems:
      system = systems[systemID]
      bodies = self.bodies[systemID]
      for colonyID in system:
        colony = self.game.colonies[colonyID]
        body = bodies[colonyID]
        if (self.GetDrawConditions(body, colony)):
          systemName = colony['System']
          bodyName = body['Name']
          radiusBody = body['RadiusBody']
          colonyName = colony['Name']
          au = body['Distance2Center']
          tf = colony['Terraforming']['Active']
          pop = colony['Pop']
          workers = 0
          unemployed = 0
          numTerraformers = 0
          mines = 0
          mass_drivers = 0
          refuel_station = False
          cargo_station = False
          spaceport = False
          unrest = colony['Unrest']
          surveyPotential = body['GroundMineralSurvey']

          if (self.game.terraformerID in colony['Installations']):
            numTerraformers = colony['Installations'][self.game.terraformerID]['Amount']
          for instID in colony['Installations']:
            installation = colony['Installations'][instID]
            if (installation['Name'] == 'Automated Mine'):
              mines += installation['Amount']
            elif (installation['Name'] == 'Mine'):
              mines += installation['Amount']
            elif (installation['Name'] == 'Spaceport'):
              spaceport = True
            elif (installation['Name'] == 'Refuelling Station'):
              refuel_station = True
            elif (installation['Name'] == 'Mass Driver'):
              mass_drivers += installation['Amount']
            elif (installation['Name'] == 'Cargo Shuttle Station'):
              cargo_station = True

          fleetIDs = Fleets.GetIDsOfFleetsInOrbit(self.game, systemID, body['ID'], type = 'Body')
          for fleetID in fleetIDs:
            numTerraformers += self.game.fleets[systemID][fleetID]['Terraformers']

          colonyCost = Utils.Round(body['ColonyCost'],1)
          ag_workers = 0.05*(colonyCost + 1)
          service_workers = min(0.7,0.1775*pop**0.2505)
          workers = pop * (1 - ag_workers - service_workers)
          
          supportedPop = 0
          if (colonyCost > -1):
            if (colonyCost > 0):
              if (body['LG']):
                supportedPop = ((colony['LG Infrastructure']) * 10000)/colonyCost/1000000
              else:
                supportedPop = ((colony['LG Infrastructure']+colony['Infrastructure']) * 10000)/colonyCost/1000000
            if (colonyCost == 0):
              supportedPop = body['Population Capacity']

            #unsortedIDs.append([colonyName, systemName, colonyCost, tf, state, gas, target])
            #header = ['AU', 'Name', 'System', 'Pop/Sup', 'Cost', 'Terraforming', 'Workers', 'Unemployed', 'Mines (M/A)', 'MassDrv', 'Fuel', 'Refuel Station', 'Supplies', 'Cargo Station', 'Spaceport']
            unsortedIDs.append([au, bodyName, surveyPotential, systemName, pop, colonyCost, tf, workers, unemployed, mines, mass_drivers, 
                                colony['Stockpile']['Fuel'], refuel_station, colony['Stockpile']['Supplies'], cargo_station, spaceport, unrest, supportedPop])
            index+=1

    id, rev = self.GetTableSortState()
    sortedIDs = sorted(unsortedIDs, key=itemgetter(id), reverse=rev)
    
    row = 0
    header = ['AU', 'Name', 'GSPot', 'System', 'Pop/Sup', 'Cost', 'Terraforming', 'Workers', 'Unemployed', 'Mines (M/A)', 'MassDrv', 'Fuel Ml', 'Refuel Station', 'Supplies', 'Cargo Station', 'Spaceport', 'Unrest']

    self.table.AddRow(row, header, [True]*len(header))

    row = 1
    sortedRowIndex = 0
    self.table.maxScroll = min(0,self.table.max_rows-len(sortedIDs)-1)
    self.table.num_rows = 1

    for row_sorted in sortedIDs:
      if (sortedRowIndex + self.table.scroll_position >= 0) and (row < self.table.max_rows):
        
        printed_row = [int(Utils.Round(row_sorted[0],0)) if (row_sorted[0]>= 10) else Utils.Round(row_sorted[0],1),# AU
                       row_sorted[1], # Name
                       row_sorted[2] if row_sorted[2] > 0 else '', # Ground Survey Potential
                       row_sorted[3], # System
                       str(Utils.GetFormattedNumber3(row_sorted[4],1, 2))+' / '+str(Utils.GetFormattedNumber3(row_sorted[17],1, 2)), # Pop/Supp
                       row_sorted[5], # Cost
                       row_sorted[6],  # Terraforming
                       Utils.GetFormattedNumber3(row_sorted[7],1, 2),  # Workers
                       row_sorted[8],  # Unemployed
                       Utils.GetFormattedNumber3(row_sorted[9],1, 1),  # Mines
                       Utils.GetFormattedNumber3(row_sorted[10],1, 1),  # MassDrv
                       Utils.GetFormattedNumber3(row_sorted[11]/1000000,1, 1),  # Fuel
                       row_sorted[12],  # Refuel Station
                       int(Utils.Round(row_sorted[13])),  # Supplies
                       row_sorted[14],  # Cargo Station
                       row_sorted[15],  # Spaceport
                       int(Utils.Round(row_sorted[16]*100))  # Unrest
                       ]
        #for i in range(len(printed_row),len(row_sorted)):
        #  if (header[i] == 'GHF' or header[i] == 'AGHF'):
        #    printed_row.append(Utils.GetFormattedNumber3(row_sorted[i],2, 3))
        #  elif (header[i] == breathGasSymbol):
        #    printed_row.append(Utils.GetFormattedNumber3(row_sorted[i],2,3))
        #  elif (header[i] == 'ETA'):
        #    printed_row.append(Utils.GetFormattedNumber4(row_sorted[i]))
        #  else:
        #    if (row_sorted[i] == 0):
        #      printed_row.append(None)
        #    else:
        #      printed_row.append(Utils.GetFormattedNumber3(row_sorted[i],1,2))

        self.table.AddRow(row, printed_row)
        row += 1
        if (row >= self.table.max_rows):
          break
      sortedRowIndex += 1

    self.table.scrollbar.Update(total_range = len(sortedIDs), current_position = -self.table.scroll_position)
    self.table.Realign()


    if (self.GUI_Elements == {}):
      self.InitGUI()
    else:
      self.UpdateGUI()
    self.reDraw = True
    t2 = pygame.time.get_ticks()
    deltaTime = t2- t1
    print('UpdateTable ',deltaTime)


  def DrawGUI(self):
    if (self.reDraw_GUI):
      for GUI_ID in self.GUI_Elements:
        element = self.GUI_Elements[GUI_ID]
        if (element.visible) and (element.clickable):
          if (element.clickable.parent == self.GUI_Table_identifier):
            if (element.enabled):
              color = Utils.TEAL
            else:
              color = Utils.DARK_GRAY
            if (element.state == 0):
              heading = 270
            else:
              heading = 90
            Utils.DrawTriangle(self.surface,(element.rect[0]+element.rect[2]-7,element.rect[1]+0.5*element.rect[3]), color, heading)
          elif (element.clickable.parent == 'Complete Colonies Table'):
            #pygame.draw.rect(self.surface, (255,0,0),self.table.rect,1)
            pass
          else:
            element.Draw(self.surface)
      for GUI_ID in self.GUI_Elements:
        element = self.GUI_Elements[GUI_ID]
        if (element.visible):
          element.DrawTooltip(self.surface)
      self.reDraw_GUI = False
      return True
    else:
      return False


  def GetTableSortState(self):
    reverse = False
    activeID = 0

    for GUI_ID in self.GUI_Elements:
      element = self.GUI_Elements[GUI_ID]
      if (element.radioGroup==self.GUI_Table_radioGroup):
        if (element.enabled):
          activeID = GUI_ID
          if (element.state == 1):
            reverse = True
    return activeID, reverse


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      #self.UpdateTable()
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      #self.tabs[self.active_tab].Draw(self.surface)
      reblit |= self.table.Draw()
      self.DrawSelectedBody()

      self.GUI_Elements[self.GUI_table_ID].rect = self.table.rect
      self.GUI_Elements[self.GUI_table_ID].clickable.rect = self.table.rect

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit


  def DrawSelectedBody(self):
    anchor = (self.table.rect[0], self.table.rect[1]+self.table.row_height*self.table.max_rows+30)
    pygame.draw.rect(self.surface, Utils.BLUE, (anchor,(1000,500)), 1)
    self.lineNr = 0
    self.unscrollableLineNr = 0

    if (self.selectedBodyName) and (self.selectedRow > -1):
      body = Bodies.GetBodyFromName(self.game, self.selectedBodyName)
      if (body):
        bodyGases = self.GetBodyGases(body)

        Utils.DrawLineOfText(self, self.surface, self.selectedBodyName, 0, anchor = anchor)
        #DrawTextWithTabs(context, surface, text1, indentLevel, text2, tab_distance, window_info_scoll_pos = 0, offset = 0, anchor = (0,0), color1 = WHITE, color2 = WHITE, text3 = None, tab_dist2 = 0, tab_dist3 = 0, text4 = None, color3 = WHITE,color4 = WHITE):
        cc = Utils.GetFormattedNumber3(body['ColonyCost'],1)
        Utils.DrawTextWithTabs(self, self.surface, 'Colony Cost:', 0, str(cc), self.tab1, anchor = anchor,color2 = Utils.LIGHT_GREEN if cc < .1 else Utils.RED)
      
        remedy = 'remove gases below limit' if (body['AtmosPressure'] > self.maxAtm) else ''
        self.DrawColorCodedColonyCosts('Atmospheric Pressure', body['AtmosPressure'], limit_text='Max pressure', limit_value=self.maxAtm, cc_factor=body['ColonyCostDetails']['Atmospheric Pressure Factor'], anchor=anchor, threshold_below = self.maxAtm, remedy = remedy)

        if (body['Temperature'] < self.minTemp):
          targetAtm, maxAtm, minTemp = self.GetTargetAtmAestusium(body, bodyGases)
          if (maxAtm):
            remedy = 'Add Aestusium to %3.2f atm to increase GH Factor and temperature (will not reach target Temp)'%(targetAtm)
          else:
            remedy = 'Add Aestusium to %3.2f atm to increase GH Factor and temperature'%(targetAtm)
        elif (body['Temperature'] > self.maxTemp):
          targetAtm, maxAtm, maxTemp = self.GetTargetAtmFrigusium(body, bodyGases)
          if (maxAtm):
            remedy = 'Add Frigusium to %3.2f atm to increase Anti GH Factor and lower temperature (will not reach target Temp)'%(targetAtm)
          else:
            remedy = 'Add Frigusium to %3.2f atm to increase Anti GH Factor lower temperature'%(targetAtm)
        else:
          remedy = ''
        
        self.DrawColorCodedColonyCosts('Temperature', body['Temperature'], limit_text='Temp Range', limit_value='%3.1f to %3.1f'%(self.minTemp, self.maxTemp), cc_factor=body['ColonyCostDetails']['Temp Factor'], anchor=anchor, threshold_below = self.minTemp, threshold = self.maxTemp, remedy = remedy)

        #Each 1% of Hydro Extent requires 0.025 atm of water vapour. This means that creating 20% Hydro Extent would require 0.5 
        remedy = ''
        if (body['Hydrosphere'] < 20):
          remedy = 'Add Water Vapor up to 0.5 atm'
        self.DrawColorCodedColonyCosts('Hydrosphere', body['Hydrosphere'], limit_text='Minimum', limit_value='20%', cc_factor=body['ColonyCostDetails']['Water Factor'], anchor=anchor, threshold_min = 20, remedy = remedy)

        gasAtm = self.table.cells[self.selectedRow][self.breathableGasAtmCol].value
        gasAtm = 0 if gasAtm is None else gasAtm
        remedy = 'Add O2 to until minimum' if (gasAtm < self.breatheMinAtm) else 'Remove O2 until below maximum' if (gasAtm > self.breatheMaxAtm) else ''
        self.DrawColorCodedColonyCosts('Oxygen Atmospheric Pressure', gasAtm, limit_text='Min/Max', limit_value='%1.1f to %1.1f'%(self.breatheMinAtm, self.breatheMaxAtm), cc_factor=body['ColonyCostDetails']['Breath Factor'], anchor=anchor, threshold_below = self.breatheMinAtm, threshold = self.breatheMaxAtm, remedy = remedy)

        gasLevel = self.table.cells[self.selectedRow][self.breathableGasLevelCol].value
        gasLevel = 0 if gasLevel is None else gasLevel

        if (remedy == '') and gasLevel > 30:
          remedy = 'Add other (non toxic) gases' if (gasLevel > 30) else ''
        self.DrawColorCodedColonyCosts('Oxygen Safe Level', gasLevel, limit_text='Maximum', limit_value=str(self.safeLevel)+'%', cc_factor=body['ColonyCostDetails']['Breath Factor'], anchor=anchor, threshold_below = 30, remedy = remedy)

        dangerAtmFactor = 0 
        for id in bodyGases:
          gas = bodyGases[id]
          if (gas['Name'] != 'Oxygen'):
            percentage = gas['Percentage']
            atm = gas['Atmospheric Pressure']
            gasDangerLevel = self.game.gases[id]['DangerousLevel']
            gasDangerFactor = self.game.gases[id]['DangerFactor']
            if (self.game.gases[id]['DangerFactor'] > 0):
              if (percentage > gasDangerLevel):
                dangerAtmFactor = max(gasDangerFactor, dangerAtmFactor)

            remedy = 'remove gas below limit' if (percentage > gasDangerLevel) and (gasDangerLevel > 0) else ''
            self.DrawColorCodedColonyCosts(self.game.gases[id]['Name'], percentage, value_text = str(Utils.GetFormattedNumber3(atm,2))+' / '+str(Utils.GetFormattedNumber3(percentage,1))+'%', limit_text='Maximum', limit_value=gasDangerLevel if gasDangerLevel != 0 else '-', cc_factor=gasDangerFactor, anchor=anchor, threshold = gasDangerLevel if gasDangerLevel != 0 else 9999, remedy = remedy)


  def ExitScreen(self):
    self.table.scrollbar.clickable.enabled = False
    self.selectedBodyName = None


  def SortTableGUI(self, id, parent = None, mousepos = None):
    thisGroup = None
    thisElement = None
    if (id in self.GUI_Elements):
      thisElement = self.GUI_Elements[id]
      if (thisElement.radioButton):
        thisGroup = thisElement.radioGroup
        if (thisElement.enabled):
          thisElement.state += 1
          thisElement.state %= 2
        else:
          thisElement.enabled = True
        self.reDraw = True
        self.reDraw_GUI = True
        

        for otherID in self.GUI_Elements:
          if (otherID != id):
            otherElement = self.GUI_Elements[otherID]
            if (otherElement.radioButton):
              if (otherElement.radioGroup == thisGroup):
                otherElement.enabled = False
        self.UpdateTable()


  def ToggleGUI_Element_ByName(self, name):
    if (name == 'Terraforming'):
      self.hideNoTerraformingActive = not self.hideNoTerraformingActive
    elif (name == 'Civilian'):
      self.hideCivilian = not self.hideCivilian
    elif (name == 'High ColonyCost'):
      self.hideHighCCBodies = not self.hideHighCCBodies
    elif (name == 'Asteroids'):
      self.hideAsteroids = not self.hideAsteroids
    elif (name == 'Comets'):
      self.hideComets = not self.hideComets
    self.UpdateTable()
    

  def GetDrawConditions(self, body, colony):
    #self.hideNoTerraformingActive = False
    #self.hideCivilian = True
    #self.hideHighCCBodies = False
    #self.hideComets = True
    #self.hideAsteroids = True

    if (colony['Terraforming']['Active']):
      ret_value = True
    else:
      ret_value = True
      if (colony['Civilian'] and self.hideCivilian):
        ret_value = False
      elif ((body['ColonyCost'] > 10) and self.hideHighCCBodies ):
        ret_value = False
      elif (body['Class'] == 'Asteroid') and (self.hideAsteroids):
        ret_value = False
      elif (body['Class'] == 'Comet') and (self.hideComets):
        ret_value = False

      if (ret_value):
        if ((colony['Terraforming']['Active'] == False) and self.hideNoTerraformingActive):
          ret_value = False

    return ret_value


  def GetBodyFromInsideTable(self, par, parent, mouse_pos):
    selectedRow = -1
    row, col, value = self.table.GetLocationInsideTable(mouse_pos)
    if (row is not None) and (col is not None):
      if row > 0 and col == 1:
        if (self.selectedBodyName != value):
          self.reDraw = True
          self.selectedBodyName = value
          self.selectedRow = row


  #DrawTextWithTabs(context, surface, text1, indentLevel, text2, tab_distance, window_info_scoll_pos = 0, offset = 0, anchor = (0,0), color1 = WHITE, color2 = WHITE, text3 = None, tab_dist2 = 0, tab_dist3 = 0, text4 = None, color3 = WHITE,color4 = WHITE):
  def DrawColorCodedColonyCosts(self, category_name, value, limit_text, limit_value, cc_factor, anchor, value_text = None, threshold_below = None, threshold = None, threshold_min = None, remedy = ''):
    if (value == None):
      value = 0
    _color2 = Utils.LIGHT_GREEN if cc_factor < 0.001 else Utils.RED
    if (threshold_below is not None):
      if (threshold is not None):
        _color = Utils.LIGHT_GREEN
        if value < threshold_below:
          _color = Utils.LIGHT_BLUE
        elif value > threshold:
          _color = Utils.RED

        Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor, color2 = _color)
      else:
        Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor,color2 = Utils.LIGHT_GREEN if value < threshold_below else Utils.RED)
    else:
      if (threshold is not None):
        Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor,color2 = Utils.RED if value > threshold else Utils.LIGHT_GREEN)
      else:
        if (threshold_min is not None):
          Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor,color2 = Utils.LIGHT_BLUE if value < threshold_min else Utils.LIGHT_GREEN)
        else:
          _color = Utils.WHITE
        
          Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor, color2 = _color)
    self.lineNr -= 1
    Utils.DrawTextWithTabs(self, self.surface, 'CC Factor:', 0, str(Utils.GetFormattedNumber3(cc_factor,2,2)), self.tab5, color2 = _color2, anchor = (anchor[0]+self.tab4,anchor[1]), text3 = remedy, tab_dist2 = self.tab6)
    

  def ResetBodies(self):
    self.bodies = {}
    self.bodies[self.game.currentSystem] = self.game.systemBodies

    systems = {}
    for colonyID in self.game.colonies:
      colony = self.game.colonies[colonyID]
      if colony['SystemID'] not in systems:
        systems[colony['SystemID']] = []
      systems[colony['SystemID']].append(colonyID)

    for systemID in systems:
      if (systemID not in self.bodies):
        self.bodies[systemID] = Bodies.GetSystemBodies(self.game, systemID)


  def GreenHouseGasPressure(self, bodyGases):
    atm = 0
    for gasName in Utils.GH_Gases:
      id = self.game.gasIDs[gasName]['ID']
      if id in bodyGases:
        atm += bodyGases[id]['Atmospheric Pressure']
    return atm


  def CalcGreenHouseFactor(self, body, bodyGases):
    gasPressGH = self.GreenHouseGasPressure(bodyGases)
    gHF = 1 + body['AtmosPressure'] * 1/10 + gasPressGH
    
    return min(gHF,3)
    

  def CalcAntiGreenHouseFactor(self, body, bodyGases):
    frigID = self.game.gasIDs['Frigusium']['ID']
    if (frigID in bodyGases):
      aGHF = 1 + body['DustLevel'] * 1/20000 + bodyGases[frigID]
    else:
      aGHF = 1 + body['DustLevel'] * 1/20000
    
    return min(aGHF,3)


  def GetTargetAtmAestusium(self, body, bodyGases):
    aGHF = self.CalcAntiGreenHouseFactor(body, bodyGases)
    targetTemp = self.minTemp+273
    baseTemp = body['BaseTemp']+273
    nominator = targetTemp * aGHF
    denominator = baseTemp * body['Albedo']
    targetAtm = (nominator / denominator) - 1 - (0.1 * body['AtmosPressure'])

    gHF = 1 + body['AtmosPressure'] * 1/10 + targetAtm
    #this calculation below is somehow wrong
    maxAtm = maxTemp = None
    #if (gHF > 3):
    #  nominator = targetTemp * 3
    #  maxAtm = (nominator / denominator) - 1 - (0.1 * body['AtmosPressure'])
    #  gHF = self.CalcGreenHouseFactor(body, bodyGases)
    #  maxTemp = baseTemp * 3 * body['Albedo'] / aGHF - 273
    return targetAtm, maxAtm, maxTemp


  def GetTargetAtmFrigusium(self, body, bodyGases):
    gHF = self.CalcGreenHouseFactor(body, bodyGases)
    targetTemp = self.maxTemp+273
    baseTemp = body['BaseTemp']+273
    nominator = baseTemp * body['Albedo'] * gHF
    targetAtm = (nominator / targetTemp) - 1 - (body['DustLevel'] * 1/20000)
    maxAtm = minTemp = None
    aGHF = 1 + body['DustLevel'] * 1/20000 + targetAtm
    #this calculation below is somehow wrong
    if (aGHF > 3):
      nominator = baseTemp * body['Albedo'] * 3
      maxAtm = (nominator / targetTemp) - 1 - (body['DustLevel'] * 1/20000)
      minTemp = baseTemp * gHF * body['Albedo'] / 3 - 273

    return targetAtm, maxAtm, minTemp


  def GetBodyGases(self, body):
    bodyGasTable = self.game.db.execute('''SELECT AtmosGasID, AtmosGasAmount, GasAtm from FCT_AtmosphericGas WHERE GameID = %d AND SystemBodyID = %d ORDER BY AtmosGasAmount Desc;'''%(self.game.gameID, body['ID'])).fetchall()
    bodyGases = {}
    for bodyGas in bodyGasTable:
      bodyGases[bodyGas[0]] = {'Name': self.game.gases[bodyGas[0]]['Name'], 'Atmospheric Pressure': bodyGas[2], 'Percentage':bodyGas[1]}

    return bodyGases
