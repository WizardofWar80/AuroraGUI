from Screen import Screen
import sqlite3
import pygame
import Events
import Clickable
import GUI
import Table
from operator import itemgetter
import Utils

class DevelopmentScreen(Screen):
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
    self.GUI_identifier = 'Development'
    self.images_GUI = {}
    self.table = Table.Table(self, 1, 15, anchor = (20,60), col_widths = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10])

    self.GUI_Table_Header_Anchor = self.table.anchor
    self.GUI_Table_identifier = 'Development Table'
    self.GUI_Table_radioGroup = 1
    self.GUI_identifier = 'Development Screen'
    self.GUI_Bottom_Anchor = (525, game.height-50)
    self.GUI_table_ID = 0
    self.GUI_ID_dropdown_systems = 1
    self.GUI_ID_dropdown_designations = 2

    #self.pad_x = 5
    #self.pad_y = 5
    #self.lineNr = 0
    #self.unscrollableLineNr = 0
    #self.indentWidth = 17
    #self.line_height = 20
    #self.textSize = 14

    self.FormatTable(self.table)
    self.table.Scrollbar()


    self.installations = ['Construction Factory',
                          'Terraforming Installation',
                          'Mine',
                          'Research Facility',
                          'Infrastructure',
                          'Automated Mine',
                          'Convert Mine to Automated',
                          'Maintenance Facility',
                          'Mass Driver',
                          'Financial Centre',
                          'Low Gravity Infrastructure']

  def FormatTable(self, table):
    pass
    #table.AddFormat(4, {'Operation':'Between', 'threshold_low':0, 'threshold_high':self.highColonyCostThreshold, 'text_color':Utils.GREEN} )
    #table.AddFormat(4, {'Operation':'Above', 'threshold':self.highColonyCostThreshold, 'text_color':Utils.RED} )
    #table.AddFormat(7, {'Operation':'Above', 'threshold':False, 'text_color':Utils.GREEN} )
    #table.AddFormat(19,{'Operation':'Above', 'threshold':False, 'text_color':Utils.GREEN} )
    table.AddFormat(0, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(2, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(3, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(4, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(5, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(6, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(7, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(8, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(9, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(10, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(11, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(12, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(13, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(14, {'Operation':'Align', 'value':'center'} )
    #table.AddFormat(3, {'Operation':'Align', 'value':'center'} )
    #table.AddFormat(7, {'Operation':'Align', 'value':'center'} )
    #table.AddFormat(9, {'Operation':'Align', 'value':'center'} )
    #table.AddFormat(4, {'Operation':'Align', 'value':'right'} )
    #table.AddFormat(5, {'Operation':'Align', 'value':'right'} )
    #table.AddFormat(6, {'Operation':'Align', 'value':'right'} )


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

    gui_cl = self.game.MakeClickable('Complete Development Table', self.table.rect, parent='Complete Development Table')
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, 'Development Table', self.table.rect, gui_cl, 'Button')
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

    #self.GetWealthData()
    #self.GetPopulationData()
    #self.GetStockpileData()
    #self.GetShipData()
    #self.GetStationData()


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
    for installation in self.installations:
      results = self.game.db.execute('''SELECT * from DIM_PlanetaryInstallation WHERE Name =\"%s\";'''%(installation)).fetchall()[0]
      cost = results[2]
      size = results[5]
      workers_M = results[25]

      Duranium    = results[36]
      Neutronium  = results[37]
      Corbomite   = results[38]
      Tritanium   = results[39]
      Boronide    = results[40]
      Mercassium  = results[41]
      Vendarite   = results[42]
      # nothing needs sorium, just fuel
      Uridium     = results[44]
      Corundium   = results[45]
      Gallicite   = results[46]
      unsortedIDs.append([index, installation, cost, Duranium, Neutronium, Corbomite, Tritanium, Boronide, Mercassium, Vendarite, Uridium, Corundium, Gallicite, size, workers_M])
      index+=1

    id, rev = self.GetTableSortState()
    sortedIDs = sorted(unsortedIDs, key=itemgetter(id), reverse=rev)
      
    row = 0
    header = ['#', 'Name', 'Cost', 'Duranium', 'Neutronium', 'Corbomite', 'Tritanium', 'Boronide', 'Mercassium', 'Vendarite', 'Uridium', 'Corundium', 'Gallicite', 'Size', 'Workers']
    self.table.AddRow(row, header, [True]*len(header))

    row = 1
    sortedRowIndex = 0
    self.table.maxScroll = min(0,self.table.max_rows-len(sortedIDs)-1)
    self.table.num_rows = 1
    printed_row = []
    for row_sorted in sortedIDs:
      if (sortedRowIndex + self.table.scroll_position >= 0) and (row < self.table.max_rows):
        printed_row = [row_sorted[0],
                       row_sorted[1],
                       '' if row_sorted[2] == 0  else f"{int(row_sorted[2]):,}",
                       '' if row_sorted[3] == 0  else f"{int(row_sorted[3]):,}",
                       '' if row_sorted[4] == 0  else f"{int(row_sorted[4]):,}",
                       '' if row_sorted[5] == 0  else f"{int(row_sorted[5]):,}",
                       '' if row_sorted[6] == 0  else f"{int(row_sorted[6]):,}",
                       '' if row_sorted[7] == 0  else f"{int(row_sorted[7]):,}",
                       '' if row_sorted[8] == 0  else f"{int(row_sorted[8]):,}",
                       '' if row_sorted[9] == 0  else f"{int(row_sorted[9]):,}",
                       '' if row_sorted[10] == 0 else f"{int(row_sorted[10]):,}",
                       '' if row_sorted[11] == 0 else f"{int(row_sorted[11]):,}",
                       '' if row_sorted[12] == 0 else f"{int(row_sorted[12]):,}",
                       '' if row_sorted[13] == 0 else f"{int(row_sorted[13]):,}",
                       '' if row_sorted[14] == 0 else f"{row_sorted[14]:,}"
                       ]
        self.table.AddRow(row, printed_row)
        row += 1
        #self.table.num_rows += 1
        if (row >= self.table.max_rows):
          break
      sortedRowIndex += 1
    for timestampW in self.game.statisticsWealth:
      pass
    for timestampM in self.game.statisticsStockpile['Duranium']:
      pass
    printed_row = ['', 'Empire Stockpile',
                    '' if self.game.statisticsWealth[timestampW] == 0  else f"{int(self.game.statisticsWealth[timestampW]):,}",
                    '' if self.game.statisticsStockpile['Duranium'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Duranium'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Neutronium'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Neutronium'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Corbomite'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Corbomite'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Tritanium'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Tritanium'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Boronide'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Boronide'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Mercassium'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Mercassium'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Vendarite'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Vendarite'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Uridium'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Uridium'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Corundium'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Corundium'][timestampM]):,}",
                    '' if self.game.statisticsStockpile['Gallicite'][timestampM] == 0  else f"{int(self.game.statisticsStockpile['Gallicite'][timestampM]):,}",
                    '', '']
    self.table.AddRow(row, printed_row)
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
          elif (element.clickable.parent == 'Complete Development Table'):
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
