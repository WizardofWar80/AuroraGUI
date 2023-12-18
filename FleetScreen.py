import Table
import pygame
import Utils
import Events
import GUI
from Screen import Screen
from operator import itemgetter
import Utils
import TableScreen
from TableScreen import TableScreen
import Fleets


class FleetScreen(TableScreen):
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
    self.images_GUI = {}
    self.table = Table.Table(self, 1, 7, anchor = (20,60), max_rows=15, col_widths = [10,10,10,10,10])
    self.table.hideEmptyColumns = False

    self.GUI_Table_Header_Anchor = self.table.anchor
    self.GUI_Table_identifier = 'Fleet Table'
    self.GUI_Table_radioGroup = 1
    self.GUI_identifier = 'Fleet Screen'
    self.GUI_Bottom_Anchor = (525, game.height-50)
    self.GUI_table_ID = 0
    self.GUI_ID_dropdown_designations = 2
    self.selectedItem = None
    self.selectedRow = -1
    self.selectedCol = -1

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
    self.fleets = {}

    self.showEmptyFleets = False
    self.showStationaryFleets = True
    self.showStations = True
    self.colIndexSystemID = 0
    self.colIndexFleetID = 0

  def InitGUI(self):
    self.table.scrollbar.clickable.enabled = True
    idGUI = 0
    reverse_order_columns = []
    col_index = 0
    for cell in self.table.cells[0]:
      gui_cl = self.game.MakeClickable(cell.value, cell.rect, self.SortTableGUI, par=idGUI, parent=self.GUI_Table_identifier)
      self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, cell.value, cell.rect, gui_cl, 'Button', enabled = True if idGUI == 0 else False, radioButton = True, radioGroup = self.GUI_Table_radioGroup, state = 1 if (col_index in reverse_order_columns) else 0)
      idGUI += 1
      col_index += 1

    gui_cl = self.game.MakeClickable('Complete Table', self.table.rect, self.GetItemFromInsideTable, parent='Complete Table')
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, self.GUI_Table_identifier, self.table.rect, gui_cl, 'Button')
    self.GUI_table_ID = idGUI
    idGUI += 1

    x = self.GUI_Bottom_Anchor[0] - 275
    y = self.GUI_Bottom_Anchor[1]
    bb = (x,y,32,32)
    gui_cl = self.game.MakeClickable('Hide empty columns', bb, self.ToggleHideCells, par=idGUI)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, 'Hide empty columns', bb, gui_cl, 'Button', enabled = self.table.hideEmptyColumns, showLabel = True, labelPos = GUI.GUI_LABEL_POS_RIGHT)
    self.GUI_Elements[idGUI].SetImages(self.game.images_GUI, 'checkbox_enabled', 'checkbox_disabled')
    idGUI += 1

    x = self.GUI_Bottom_Anchor[0]
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Show Empty Fleets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.showEmptyFleets)

    idGUI += 1
    x += size+5
    size = 32
    bb = (x,y,size,size)
    name = 'Show Stationary Fleets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.showStationaryFleets)
    
    idGUI += 1
    x += size+5
    size = 32
    bb = (x,y,size,size)
    name = 'Show Stations'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.showStations)


  def ToggleGUI_Element_ByName(self, name):
    if (name == 'Show Empty Fleets'):
      self.showEmptyFleets = not self.showEmptyFleets
    elif(name == 'Show Stationary Fleets'):
      self.showStationaryFleets = not self.showStationaryFleets
    elif(name == 'Show Stations'):
      self.showStations = not self.showStations
    self.UpdateTable()


  def UpdateTable(self):
    game = self.game
    t1 = pygame.time.get_ticks()
    self.table.Clear()
    self.fleets={}
    text_widths = []
    unsortedIDs = []
    #self.table.max_cell_sizes = []
    index = 1
    systems = {}
    for systemID in game.fleets:
      systemFleets = game.fleets[systemID]
      for fleetID in systemFleets:
        fleet = systemFleets[fleetID]
        if (self.GetDrawConditions(fleet)):
          fleetType = ''
          if (fleet['Harvesters'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'H'
          if (fleet['Refueling Hub'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'FH'
          if (fleetType == ''):
            if (fleet['Tanker'] > 0):
              fleetType += 'T'
          if (fleet['Terraformers'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'TF'
          if (fleet['Orbital Miners'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'OM'
          if (fleet['Ordnance Hub'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'OH'
          if (fleet['Supply Ship'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'SS'
          if (fleet['Tug'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'Tug'
          numShips = len(fleet['Ships'])
          order = self.GetCondensedMoveOrders(fleet)
          unsortedIDs.append([fleet['Name'], fleet['System_Name'], fleet['Admin'], fleet['Station'], fleetType, numShips, order])
          
          self.colIndexSystemID = len(unsortedIDs[-1])
          self.colIndexFleetID = self.colIndexSystemID + 1
          unsortedIDs[-1].append(systemID)
          unsortedIDs[-1].append(fleetID)

    index+=1

    id, rev = self.GetTableSortState()
    sortedIDs = sorted(unsortedIDs, key=itemgetter(id), reverse=rev)
    
    row = 0
    header = ['Name', 'System', 'Admin', 'Station', 'Fleet Type', '# Ships', 'Orders']
    
    self.table.AddRow(row, header, [True]*len(header))

    row = 1
    sortedRowIndex = 0
    self.table.maxScroll = min(0,self.table.max_rows-len(sortedIDs)-1)
    self.table.num_rows = 1

    for row_sorted in sortedIDs:
      if (sortedRowIndex + self.table.scroll_position >= 0) and (row < self.table.max_rows):
        #printed_row = [int(Utils.Round(row_sorted[0],0)) if (row_sorted[0]>= 10) else Utils.Round(row_sorted[0],1),# AU
        #               row_sorted[1], # Name
        #               row_sorted[2], # System
        #               row_sorted[3], # Cost
        #               row_sorted[4]  # Terraforming
        #               ]

        self.table.AddRow(row, row_sorted)
        self.fleets[row]=row_sorted
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
    #self.reDraw = True
    t2 = pygame.time.get_ticks()
    deltaTime = t2- t1
    print('UpdateTable ',deltaTime)


  def FormatTable(self, table):
    color_red = Utils.RED
    color_blue = Utils.LIGHT_BLUE
    color_green = Utils.LIGHT_GREEN
    table.AddFormat(0, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(1, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(2, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(3, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(4, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(5, {'Operation':'Align', 'value':'center'} )


  def GetDrawConditions(self, fleet):
    show = True
    if (fleet['Ships'] == []):
      if (self.showEmptyFleets):
        show = True
      else:
        show = False
    elif (fleet['Station']):
      if (self.showStations):
        show = True
      else:
        show = False
    elif (fleet['Speed'] <= 1 ):
      if (self.showStationaryFleets):
        show = True
      else:
        show = False
    return show

  
  def DrawSelectedItem(self):
    anchor = (self.table.rect[0], self.table.rect[1]+self.table.row_height*self.table.max_rows+30)
    pygame.draw.rect(self.surface, Utils.BLUE, (anchor,(1000,500)), 1)
    self.lineNr = 0
    self.unscrollableLineNr = 0

    if (self.selectedItem) and (self.selectedRow > -1):
      if (self.selectedRow in self.fleets):
        selectedFleetArray = self.fleets[self.selectedRow]
        systemID = selectedFleetArray[self.colIndexSystemID]
        fleetID = selectedFleetArray[self.colIndexFleetID]
        fleet = self.game.fleets[systemID][fleetID]
        Utils.DrawLineOfText(self, self.surface, fleet['Name'], 0, anchor = anchor)
        orderText = self.GetCondensedMoveOrders(fleet)
        Utils.DrawLineOfText(self, self.surface, orderText, 0, anchor = anchor)
        for ship in fleet['Ships']:
          Utils.DrawLineOfText(self, self.surface, ship['Name'], 0, anchor = anchor)


  def GetCondensedMoveOrders(self, fleet):
    orderText = ''
    item=''
    sourceLocation = ''
    destinationLocation = ''
    if (fleet is not None):
      fleetID = fleet['ID']
      orders_table = [list(x) for x in self.game.db.execute('''SELECT * from FCT_MoveOrders WHERE FleetID = %d;'''%fleetID)]
      loadActionIDs = [4,33,62,86,140,165,176,178,180,223]
      unloadActionIDs = [6,63,67,87,88,96,129,141,156,165,177,179,187,189,193,225,226,227]
      for order in orders_table:
        #print(order)
        orderDescr = order[18]
        if order[4] == 64 or order[4] == 161:
          orderText = orderDescr
        else:
          if order[4] in loadActionIDs:
            sourceLocation = orderDescr[:orderDescr.find(':')]
            findHyphen = orderDescr.rfind(' - ')
            if (findHyphen > -1):
              item = orderDescr[findHyphen+3:]
            else:
              findSpace = orderDescr.rfind(' ')
              if (findSpace > -1):
                item = orderDescr[findSpace:]
            if orderDescr.find('Fuel') > -1:
              item = 'Fuel'
            orderText = 'Transport %s from %s to %s'%(item, sourceLocation, destinationLocation)
          if order[4] in unloadActionIDs:
            destinationLocation = orderDescr[:orderDescr.find(':')]
            findHyphen = orderDescr.rfind(' - ')
            if (findHyphen > -1):
              item = orderDescr[findHyphen+3:]
            else:
              findSpace = orderDescr.rfind(' ')
              if (findSpace > -1):
                item = orderDescr[findSpace:]
            if orderDescr.find('Fuel') > -1:
              item = 'Fuel'
            orderText = 'Transport %s %s%s to %s'%(item, ('from 'if sourceLocation !='' else ''), sourceLocation, destinationLocation)
    return orderText