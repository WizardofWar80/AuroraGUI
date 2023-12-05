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

class TerraformingScreen(Screen):
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
    self.GUI_identifier = 'Terraforming'
    self.images_GUI = {}
    self.table = Table.Table(self, 1, 31, anchor = (20,50), col_widths = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10])

    self.GUI_Table_Header_Anchor = self.table.anchor
    self.GUI_Table_identifier = 'Terraforming Table'
    self.GUI_Table_radioGroup = 1
    self.GUI_identifier = 'Terraforming Screen'
    self.GUI_Bottom_Anchor = (525, game.height-50)
    self.GUI_table_ID = 0
    self.GUI_ID_dropdown_systems = 1
    self.GUI_ID_dropdown_designations = 2

    self.breatheGas = 'Oxygen'
    self.breatheMinAtm = 0.1
    self.breatheMaxAtm = 0.3
    self.safeLevel = 30
    self.maxAtm = 4
    self.minTemp = -10
    self.maxTemp = 38
    self.FormatTable(self.table)
    self.table.Scrollbar()



  def FormatTable(self, table):
    color_red = Utils.RED
    color_blue = Utils.LIGHT_BLUE
    color_green = Utils.LIGHT_GREEN

    table.AddFormat(1, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(2, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(3, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(4, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(5, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(6, {'Operation':'Align', 'value':'center'} )

    gasIndex = 1
    for gasID in self.game.gases:
      if (gasID > 0):
        if (self.game.gases[gasID]['Name'] == 'Oxygen'):
          table.AddFormat(6+gasIndex, {'Operation':'Between', 'threshold_low':self.breatheMinAtm, 
                                                              'threshold_high':self.breatheMaxAtm, 
                                                              'text_color':color_green, 
                                                              'too_low_color': color_blue, 
                                                              'too_high_color':color_red} )
          table.AddFormat(6+gasIndex, {'Operation':'Align', 'value':'center'} )
          gasIndex+=1
          table.AddFormat(6+gasIndex, {'Operation':'Above', 'threshold':self.safeLevel, 'text_color':color_red, 'else_color':color_green} )
        else:
          if (self.game.gases[gasID]['DangerousLevel'] > 0):
            table.AddFormat(6+gasIndex, {'Operation':'Above', 'threshold':self.game.gases[gasID]['DangerousLevel'], 'text_color':color_red, 'else_color':color_green} )
        table.AddFormat(6+gasIndex, {'Operation':'Align', 'value':'center'} )
        gasIndex+=1
    table.AddFormat(29, {'Operation':'Between', 'threshold_low':self.minTemp,
                                                'threshold_high':self.maxTemp, 
                                                'text_color':color_green, 
                                                'too_low_color': color_blue, 
                                                'too_high_color':color_red} )

    table.AddFormat(29, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(30, {'Operation':'Below', 'threshold':20, 'text_color':color_blue, 'else_color':color_green} )
    table.AddFormat(30, {'Operation':'Align', 'value':'center'} )
    

  def InitGUI(self):
    self.table.scrollbar.clickable.enabled = True
    idGUI = 0
    reverse_order_columns = [3,4,5,6,7,8,9,10,11,12]
    col_index = 0
    for cell in self.table.cells[0]:
      gui_cl = self.game.MakeClickable(cell.value, cell.rect, self.SortTableGUI, par=idGUI, parent=self.GUI_Table_identifier)
      self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, cell.value, cell.rect, gui_cl, 'Button', enabled = True if idGUI == 0 else False, radioButton = True, radioGroup = self.GUI_Table_radioGroup, state = 1 if (col_index in reverse_order_columns) else 0)
      idGUI += 1
      col_index += 1

    gui_cl = self.game.MakeClickable('Complete Terraforming Table', self.table.rect, parent='Complete Terraforming Table')
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, 'Terraforming Table', self.table.rect, gui_cl, 'Button')
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


  def UpdateDevelopmentData(self):
    if (self.GUI_Elements == {}):
      self.InitGUI()
    else:
      self.UpdateGUI()


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
    for colonyID in self.game.colonies:
      colony = self.game.colonies[colonyID]
      if colony['SystemID'] not in systems:
        systems[colony['SystemID']] = []
      systems[colony['SystemID']].append(colonyID)

    for systemID in systems:
      system = systems[systemID]
      bodies = Bodies.GetSystemBodies(self.game, systemID)
      for colonyID in system:
        colony = self.game.colonies[colonyID]
        body = bodies[colonyID]

        systemName = colony['System']
        colonyName = colony['Name']
        tf = colony['Terraforming']['Active']
        state = gas = target = ''
        if (tf):
          state = colony['Terraforming']['State']
          gas = colony['Terraforming']['Gas']['Symbol']
          target = colony['Terraforming']['TargetATM']
        colonyCost = round(body['ColonyCost'],1)
        if (colonyCost > -1):
          unsortedIDs.append([colonyName, systemName, colonyCost, tf, state, gas, target])
          bodyGases = self.game.db.execute('''SELECT AtmosGasID, AtmosGasAmount, GasAtm from FCT_AtmosphericGas WHERE GameID = %d AND SystemBodyID = %d;'''%(self.game.gameID, colonyID)).fetchall()
          for gasID in self.game.gases:
            if (gasID > 0):
              percentage = 0
              atm = 0
              for bodyGas in bodyGases:
                id = bodyGas[0]
                if (id == gasID):
                  percentage = bodyGas[1]
                  atm = bodyGas[2]
                  break

              unsortedIDs[-1].append(atm)
              if (self.game.gases[gasID]['Name'] == 'Oxygen'):
                unsortedIDs[-1].append(percentage)
          unsortedIDs[-1].append(body['Temperature'])
          unsortedIDs[-1].append(body['Hydrosphere'])
          index+=1

    id, rev = self.GetTableSortState()
    sortedIDs = sorted(unsortedIDs, key=itemgetter(id), reverse=rev)
      
    row = 0
    header = ['Name', 'System', 'Cost', 'Terraforming', 'TF State', 'TF Gas', 'Target ATM']

    for gasID in self.game.gases:
      if (gasID > 0):
        header.append(self.game.gases[gasID]['Symbol'])
        if (self.game.gases[gasID]['Name'] == 'Oxygen'):
          header.append(self.game.gases[gasID]['Symbol']+' %')

    header.append('Temp')
    header.append('Water %')

    self.table.AddRow(row, header, [True]*len(header))

    row = 1
    sortedRowIndex = 0
    self.table.maxScroll = min(0,self.table.max_rows-len(sortedIDs)-1)
    self.table.num_rows = 1
    printed_row = []
    for row_sorted in sortedIDs:
      if (sortedRowIndex + self.table.scroll_position >= 0) and (row < self.table.max_rows):
        printed_row = [row_sorted[0],# Name
                       row_sorted[1],# System
                       row_sorted[2],# Cost
                       row_sorted[3] if row_sorted[3] else '',# Terraforming
                       row_sorted[4],# TF State
                       row_sorted[5],# TF Gas
                       row_sorted[6] # Target ATM
                       ]
        for i in range(len(printed_row),len(row_sorted)):
          if (i == 16):
            printed_row.append(Utils.GetFormattedNumber2(row_sorted[i]))
          else:
            if (row_sorted[i] == 0):
              printed_row.append(None)
            else:
              printed_row.append(Utils.GetFormattedNumber2(row_sorted[i]))

        #self.table.AddRow(row, printed_row)
        self.table.AddRow(row, printed_row)
        row += 1
        #self.table.num_rows += 1
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
          elif (element.clickable.parent == 'Complete Terraforming Table'):
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
      self.UpdateTable()
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      #self.tabs[self.active_tab].Draw(self.surface)
      reblit |= self.table.Draw()

      self.GUI_Elements[self.GUI_table_ID].rect = self.table.rect
      self.GUI_Elements[self.GUI_table_ID].clickable.rect = self.table.rect

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit



  def ExitScreen(self):
    self.table.scrollbar.clickable.enabled = False


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