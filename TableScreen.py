import Table
import pygame
import Utils
import Events
import GUI
from Screen import Screen
from operator import itemgetter
import Utils
#import Colonies
#import Bodies
#import Fleets
#import Systems


class TableScreen(Screen):
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
    self.GUI_identifier = 'Table'
    self.images_GUI = {}
    self.table = Table.Table(self, 1, 5, anchor = (20,60), max_rows=15, col_widths = [10,10,10,10,10])
    self.table.hideEmptyColumns = False

    self.GUI_Table_Header_Anchor = self.table.anchor
    self.GUI_Table_identifier = 'Table'
    self.GUI_Table_radioGroup = 1
    self.GUI_identifier = 'Table Screen'
    self.GUI_Bottom_Anchor = (525, game.height-50)
    self.GUI_table_ID = 0
    self.GUI_ID_dropdown_systems = 1
    self.GUI_ID_dropdown_designations = 2
    self.selectedItem = None
    self.selectedRow = -1

    self.Option1 = False

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
    table.AddFormat(2, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(3, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(4, {'Operation':'Align', 'value':'center'} )
       

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

    size = 32
    x = self.GUI_Bottom_Anchor[0]
    y = self.GUI_Bottom_Anchor[1]
    bb = (x,y,size,size)
    name = 'Option1'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.Option1, tooltip='Option1')
    #self.GUI_Elements[idGUI].SetImages(self.game.images_GUI, 'checkbox_enabled', 'checkbox_disabled')


  def RefreshData(self):
    self.UpdateTable()


  def UpdateGUI(self):
    for i in range(len(self.table.cells[0])):
      if (self.table.cells[0][i]):
        self.GUI_Elements[i].rect = self.table.cells[0][i].rect
        if (self.table.hideEmptyColumns and self.table.dataColumns[i] == False):
          if (self.GUI_Elements[i].clickable):
            self.GUI_Elements[i].clickable.enabled = False
            self.GUI_Elements[i].clickable.rect = None
          self.GUI_Elements[i].visible = False
        else:
          self.GUI_Elements[i].visible = True
          if (self.GUI_Elements[i].clickable):
            self.GUI_Elements[i].clickable.enabled = True
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
    unsortedIDs.append(['#', 'Name', 'Something'])

    unsortedIDs[-1].append('Something')
    unsortedIDs[-1].append(5)
    
    index+=1

    id, rev = self.GetTableSortState()
    sortedIDs = sorted(unsortedIDs, key=itemgetter(id), reverse=rev)
    
    row = 0
    header = ['AU', 'Name', 'System', 'Cost', 'Value']
    
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
          elif (element.clickable.parent == 'Complete Table'):
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


  def ToggleHideCells(self, par, void = None, void2 = None):
    self.table.ToggleHideCells()
    self.ToggleGUI(par)
    self.reDraw = True


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      reblit |= self.table.Draw()
      self.DrawSelectedItem()

      self.GUI_Elements[self.GUI_table_ID].rect = self.table.rect
      self.GUI_Elements[self.GUI_table_ID].clickable.rect = self.table.rect

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit


  def DrawSelectedItem(self):
    anchor = (self.table.rect[0], self.table.rect[1]+self.table.row_height*self.table.max_rows+30)
    pygame.draw.rect(self.surface, Utils.BLUE, (anchor,(1000,500)), 1)
    self.lineNr = 0
    self.unscrollableLineNr = 0

    if (self.selectedItem) and (self.selectedRow > -1):
      Utils.DrawLineOfText(self, self.surface, self.selectedItem, 0, anchor = anchor)
      
        

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
    if (name == 'Option1'):
      self.Option1 = not self.Option1
    self.UpdateTable()
    

  def GetDrawConditions(self, body, colony):
    ret_value = True
    
    return ret_value


  def GetItemFromInsideTable(self, par, parent, mouse_pos):
    selectedRow = -1
    row, col, value = self.table.GetLocationInsideTable(mouse_pos)
    if (row is not None) and (col is not None):
      if row > 0 and col == 1:
        if (self.selectedItem != value):
          self.reDraw = True
          self.selectedItem = value
          self.selectedRow = row


  def DrawColorCodedColonyCosts(self, category_name, value, limit_text, limit_value, cc_factor, anchor, value_text = None, threshold_below = None, threshold = None, threshold_min = None, remedy = ''):
    #if (value == None):
    #  value = 0
    #_color2 = Utils.LIGHT_GREEN if cc_factor < 0.001 else Utils.RED
    #if (threshold_below is not None):
    #  if (threshold is not None):
    #    _color = Utils.LIGHT_GREEN
    #    if value < threshold_below:
    #      _color = Utils.LIGHT_BLUE
    #    elif value > threshold:
    #      _color = Utils.RED

    #    Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor, color2 = _color)
    #  else:
    #    Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor,color2 = Utils.LIGHT_GREEN if value < threshold_below else Utils.RED)
    #else:
    #  if (threshold is not None):
    #    Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor,color2 = Utils.RED if value > threshold else Utils.LIGHT_GREEN)
    #  else:
    #    if (threshold_min is not None):
    #      Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor,color2 = Utils.LIGHT_BLUE if value < threshold_min else Utils.LIGHT_GREEN)
    #    else:
    #      _color = Utils.WHITE
        
    #      Utils.DrawTextWithTabs(self, self.surface, category_name+':', 0, value_text if value_text is not None else str(Utils.GetFormattedNumber3(value,2,3)), self.tab1, text3=limit_text+':', tab_dist2 = self.tab2, text4 = str(limit_value), tab_dist3 = self.tab3, anchor = anchor, color2 = _color)
    #self.lineNr -= 1
    #Utils.DrawTextWithTabs(self, self.surface, 'CC Factor:', 0, str(Utils.GetFormattedNumber3(cc_factor,2,2)), self.tab5, color2 = _color2, anchor = (anchor[0]+self.tab4,anchor[1]), text3 = remedy, tab_dist2 = self.tab6)
    pass
    

  def ResetBodies(self):
    #self.bodies = {}
    #self.bodies[self.game.currentSystem] = self.game.systemBodies

    #systems = {}
    #for colonyID in self.game.colonies:
    #  colony = self.game.colonies[colonyID]
    #  if colony['SystemID'] not in systems:
    #    systems[colony['SystemID']] = []
    #  systems[colony['SystemID']].append(colonyID)

    #for systemID in systems:
    #  if (systemID not in self.bodies):
    #    self.bodies[systemID] = Bodies.GetSystemBodies(self.game, systemID)
    pass


