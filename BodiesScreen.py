import Table
import pygame
import Utils
import Events
import GUI
from Screen import Screen
from operator import itemgetter
import Bodies
import Systems
import Designations

class BodiesScreen(Screen):
  def __init__(self, game, events):
    self.reDraw = True
    self.reDraw_GUI = True
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

    self.GUI_Elements = {}
    self.images_GUI = {}
    #self.InitGUI()
  #def Init2(self, game, events):
    self.table = Table.Table(self, 1, 20, anchor = (20,50), col_widths = [10,10,10,10,10,10,10])

    self.showColonizedBodies = True
    self.showIndustrializedBodies = True
    self.showUnsurveyedBodies = False
    self.showResourcelessComets = False
    self.showResourcelessAsteroids = False
    self.showResourcelessSmallWorlds = False
    self.showResourcelessLargeWorlds = True
    self.showLowCCBodies = True
    self.highColonyCostThreshold = 3

    self.GUI_Table_Header_Anchor = self.table.anchor
    self.GUI_Table_identifier = 'Bodies Table'
    self.GUI_Table_radioGroup = 1
    self.GUI_identifier = 'Bodies Screen'
    self.GUI_Bottom_Anchor = (525, game.height-50)
    self.GUI_table_ID = 0
    self.GUI_ID_dropdown_systems = 1
    self.GUI_ID_dropdown_designations = 2

    self.FormatTable(self.table)
    self.table.Scrollbar()


  def FormatTable(self, table):
    table.AddFormat(4, {'Operation':'Between', 'threshold_low':0, 'threshold_high':self.highColonyCostThreshold, 'text_color':Utils.GREEN} )
    table.AddFormat(4, {'Operation':'Above', 'threshold':self.highColonyCostThreshold, 'text_color':Utils.RED} )
    table.AddFormat(7, {'Operation':'Above', 'threshold':False, 'text_color':Utils.GREEN} )
    table.AddFormat(19,{'Operation':'Above', 'threshold':False, 'text_color':Utils.GREEN} )
    table.AddFormat(0, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(3, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(7, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(9, {'Operation':'Align', 'value':'center'} )
    table.AddFormat(4, {'Operation':'Align', 'value':'right'} )
    table.AddFormat(5, {'Operation':'Align', 'value':'right'} )
    table.AddFormat(6, {'Operation':'Align', 'value':'right'} )


  def InitGUI(self):
    self.table.scrollbar.clickable.enabled = True
    idGUI = 0
    reverse_order_columns = [5,6,8,9,10,11,12,13,14,15,16,17,18]
    col_index = 0
    for cell in self.table.cells[0]:
      gui_cl = self.game.MakeClickable(cell.value, cell.rect, self.SortTableGUI, par=idGUI, parent=self.GUI_Table_identifier)
      self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, cell.value, cell.rect, gui_cl, 'Button', enabled = True if idGUI == 0 else False, radioButton = True, radioGroup = self.GUI_Table_radioGroup, state = 1 if (col_index in reverse_order_columns) else 0)
      idGUI += 1
      col_index += 1

    gui_cl = self.game.MakeClickable('Complete Bodies Table', self.table.rect, double_click_call_back = self.GetBodyFromInsideTable, parent='Complete Bodies Table')
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, 'Bodies Table', self.table.rect, gui_cl, 'Button')
    self.GUI_table_ID = idGUI
    idGUI += 1

    x = self.GUI_Bottom_Anchor[0] - 275
    y = self.GUI_Bottom_Anchor[1] + 3
    bb = (x,y,250,25)
    gui_cl = self.game.MakeClickable('Bodies Dropdown', bb, self.OpenSystemDropdown, parent='Bodies Dropdown')
    systemNames = Systems.GetKnownSystemNames(self.game)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, 'System', bb, gui_cl, 'Dropdown', content = systemNames, dropUp = True, showLabel = True)
    self.GUI_ID_dropdown_systems = idGUI
    self.GUI_Elements[idGUI].dropdownSelection = Systems.GetIndexOfCurrentSystem(self.game)
    idGUI += 1

    x = 25
    y = self.GUI_Bottom_Anchor[1] + 3
    bb = (x,y,200,25)
    gui_cl = self.game.MakeClickable('Designation', bb, self.OpenDesignationDropdown, parent='Designation Dropdown')
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, 'Designation', bb, gui_cl, 'Dropdown', content = Designations.system_designations, dropUp = True, showLabel = True)
    self.GUI_ID_dropdown_designations = idGUI
    self.GUI_Elements[idGUI].dropdownSelection = Designations.GetIndexOfCurrentSystem()
    idGUI += 1

    size = 32
    x = self.GUI_Bottom_Anchor[0]
    y = self.GUI_Bottom_Anchor[1]
    bb = (x,y,size,size)
    name = 'Show Colonies'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', enabled = self.showColonizedBodies, tooltip='Always show colonized bodies')

    idGUI += 1
    x += size+5
    bb = (x,y,size,size)
    name = 'Filter Resources'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', tooltip='Show bodies without resources')
    showBodiesGUI = self.GUI_Elements[idGUI]

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'LargeWorlds'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showBodiesGUI.GetID(), enabled = self.showResourcelessLargeWorlds, tooltip='Show large worlds without resources')
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'SmallWorlds'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showBodiesGUI.GetID(), enabled = self.showResourcelessSmallWorlds, tooltip='Show small worlds without resources')
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Comets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showBodiesGUI.GetID(), enabled = self.showResourcelessComets, tooltip='Show comets without resources')
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Asteroids'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showBodiesGUI.GetID(), enabled = self.showResourcelessAsteroids, tooltip='Show asteroids without resources')
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    x += size+5
    y = self.GUI_Bottom_Anchor[1]
    bb = (x,y,size,size)
    name = 'Show Installations'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.showIndustrializedBodies, tooltip='Always show bodies with installations')

    idGUI += 1
    x += size+5
    bb = (x,y,size,size)
    name = 'Show Unsurveyed'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', enabled = self.showUnsurveyedBodies, tooltip='Always show unsurveyed bodies')

    idGUI += 1
    x += size+5
    bb = (x,y,size,size)
    name = 'Show LowColonyCost'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', enabled = self.showLowCCBodies, tooltip='Always show bodies with low colony costs')


  def UpdateGUI(self):
    for i in range(len(self.table.cells[0])):
      self.GUI_Elements[i].rect = self.table.cells[0][i].rect
      self.GUI_Elements[i].clickable.rect = self.table.cells[0][i].rect
    self.GUI_Elements[self.GUI_table_ID].rect = self.table.rect


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


  def ToggleGUI_Element_ByName(self, name):
    if (name == 'Show Colonies'):
      self.showColonizedBodies = not self.showColonizedBodies
    elif (name == 'LargeWorlds'):
      self.showResourcelessLargeWorlds = not self.showResourcelessLargeWorlds
    elif (name == 'SmallWorlds'):
      self.showResourcelessSmallWorlds = not self.showResourcelessSmallWorlds
    elif (name == 'Asteroids'):
      self.showResourcelessAsteroids = not self.showResourcelessAsteroids
    elif (name == 'Comets'):
      self.showResourcelessComets = not self.showResourcelessComets
    elif (name == 'Show Installations'):
      self.showIndustrializedBodies = not self.showIndustrializedBodies
    elif (name == 'Show Unsurveyed'):
      self.showUnsurveyedBodies = not self.showUnsurveyedBodies
    elif (name == 'Show LowColonyCost'):
      self.showLowCCBodies = not self.showLowCCBodies


  def ExitScreen(self):
    self.table.scrollbar.clickable.enabled = False


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      self.UpdateTable()
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)

      reblit |= self.table.Draw()
      self.GUI_Elements[self.GUI_table_ID].rect = self.table.rect
      self.GUI_Elements[self.GUI_table_ID].clickable.rect = self.table.rect

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit


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


  def UpdateTable(self):
    t1 = pygame.time.get_ticks()
    self.table.Clear()
    system = self.game.starSystems[self.game.currentSystem]
    text_widths = []
    unsortedIDs = []
    #self.table.max_cell_sizes = []
    for bodyID in self.game.systemBodies:
      cond = self.GetDrawConditions(self.game.systemBodies[bodyID])
      if (cond):
        pop = 0
        if (bodyID in self.game.colonies):
          colony = self.game.colonies[bodyID]
          pop = colony['Pop']
        body = self.game.systemBodies[bodyID]
        unsortedIDs.append([bodyID, body['Distance2Center'], body['Name'], body['Type'], body['Status'], body['ColonyCost'], pop, body['Population Capacity'], body['Colonizable']])
        for id in Utils.MineralNames:
          unsortedIDs[-1].append(body['Deposits'][Utils.MineralNames[id]]['Amount'])
        unsortedIDs[-1].append(body['Terraforming']['Active'])
        #unsortedIDs.append([bodyID, self.game.systemBodies[bodyID]['Population Capacity']])
        #unsortedIDs.append([bodyID, self.game.systemBodies[bodyID]['ColonyCost']])
    
    id, rev = self.GetTableSortState()
    sortedIDs = sorted(unsortedIDs, key=itemgetter(id+1), reverse=rev)
      
    row = 0
    header = ['AU', 'Name', 'Type', 'S', 'CC', 'Pop','Pop Cap', 'Colonizable']
    for id in Utils.MineralNames:
      header.append(Utils.MineralNames[id][:2])
    header.append('TF')
    self.table.AddRow(row, header, [True]*len(header))

    row = 1
    sortedRowIndex = 0
    self.table.maxScroll = min(0,self.table.max_rows-len(sortedIDs)-1)
    self.table.num_rows = 1
    for row_sorted in sortedIDs:
      if (sortedRowIndex + self.table.scroll_position >= 0) and (row < self.table.max_rows):
        bodyID = row_sorted[0]
      #for bodyID in self.game.systemBodies:
        body = self.game.systemBodies[bodyID]
        pop = 0
        if (bodyID in self.game.colonies):
          colony = self.game.colonies[bodyID]
          pop = colony['Pop']
        row_format = [False, True if body['Colonized'] else False, False, False, False,False,False,]
        data = [ int(round(body['Distance2Center'],0)) if (body['Distance2Center']>= 10) else round(body['Distance2Center'],1)
                ,body['Name'] 
                ,body['Type'] 
                ,body['Status']
                ,round(body['ColonyCost'],1)
                ,f"{round(pop,2):,}" if pop > 0 else ''
                ,f"{round(body['Population Capacity'],2):,}"
                ,body['Colonizable']
                ]
        index = len(data)
        for id in Utils.MineralNames:
          data.append(None)
          row_format.append(False)
        if ('Deposits' in body):
          for id in Utils.MineralNames:
            if Utils.MineralNames[id] in body['Deposits']:
              val = body['Deposits'][Utils.MineralNames[id]]['Amount']
              data[index] = '' if val == 0 else Utils.ConvertNumber2kMGT(val) + '  (' + str(body['Deposits'][Utils.MineralNames[id]]['Accessibility']) + ')'
            index += 1
        data.append(body['Terraforming']['Active'])
        row_format.append(False)
        self.table.AddRow(row, data, row_format)
        row += 1
        #self.table.num_rows += 1
        if (row >= self.table.max_rows):
          break
      sortedRowIndex += 1
    self.table.scrollbar.Update(total_range = len(sortedIDs), current_position = -self.table.scroll_position)
    #self.table.FormatColumnIfValuesBetween(4,0,self.highColonyCostThreshold,text_color = Utils.GREEN)
    #self.table.FormatColumnIfValuesAbove(4,self.highColonyCostThreshold,text_color = Utils.RED)
    self.table.Realign()
    #self.table.FormatColumn(0,align = 'center')
    #self.table.FormatColumn(3,align = 'center')
    #self.table.FormatColumn(4,align = 'right')
    #self.table.FormatColumn(5,align = 'right')
    #self.table.FormatColumn(6,align = 'right')
    #self.table.FormatColumn(7,align = 'center')
    #self.table.FormatColumn(19,align = 'center')
    #self.table.FormatColumnIfValuesAbove(7,False,text_color = Utils.GREEN)
    #self.table.FormatColumnIfValuesAbove(19,False,text_color = Utils.GREEN)
    
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
          elif (element.clickable.parent == 'Complete Bodies Table'):
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


  def GetDrawConditions(self, body):
    if (body['Colonized'] and self.showColonizedBodies):
      return True
    elif (body['Resources']):
      return True
    elif (self.showLowCCBodies and body['ColonyCost'] < self.highColonyCostThreshold):
      return True
    else:
      if (body['Class'] == 'Asteroid'):
        if (self.showResourcelessAsteroids):
          return True
      elif (body['Class'] == 'Comet'):
        if (self.showResourcelessComets):
          return True
      elif (body['Type'] == 'Planet Small' or body['Class'] == 'Moon'):
        if (self.showResourcelessSmallWorlds):
          return True
      elif (body['Class'] == 'Planet'):
        if (self.showResourcelessLargeWorlds):
          return True
    return False


  def GetBodyFromInsideTable(self, par, parent, mouse_pos):
    row, col, value = self.table.GetLocationInsideTable(mouse_pos)
    if (row is not None) and (col is not None):
      if row > 0 and col == 1:
        if (value is not None):
          #body = Bodies.GetBodyFromName(value)
          #print(value)
          self.game.FollowEvent([value, self.game.currentSystem, 0, 0, 0, 0], 'Body')


  def OpenSystemDropdown(self, parameter, parent, mousepos):
    self.GUI_Elements[self.GUI_ID_dropdown_systems].open = not self.GUI_Elements[self.GUI_ID_dropdown_systems].open
    if (self.GUI_Elements[self.GUI_ID_dropdown_systems].open):
      self.game.MakeClickable('open dropdown', self.GUI_Elements[self.GUI_ID_dropdown_systems].extendedBB, self.GetDropdownSelection, par=mousepos, parent='Bodies Dropdown')
    else:
      self.game.Events.RemoveClickable('open dropdown', parent='Bodies Dropdown')
      self.GUI_Elements[self.GUI_ID_dropdown_systems].scroll_position = 0
    self.reDraw = True


  def OpenDesignationDropdown(self, parameter, parent, mousepos):
    self.GUI_Elements[self.GUI_ID_dropdown_designations].open = not self.GUI_Elements[self.GUI_ID_dropdown_designations].open
    if (self.GUI_Elements[self.GUI_ID_dropdown_designations].open):
      self.game.MakeClickable('open dropdown', self.GUI_Elements[self.GUI_ID_dropdown_designations].extendedBB, self.GetDropdownSelection, par=mousepos, parent='Designation Dropdown')
    else:
      self.game.Events.RemoveClickable('open dropdown', parent='Designation Dropdown')
      self.GUI_Elements[self.GUI_ID_dropdown_designations].scroll_position = 0
    self.reDraw = True

    
  def GetDropdownSelection(self, mouse_pos, parent, mousepos):
    lineNr = 0
    id = None
    if (parent == 'Bodies Dropdown'):
      id = self.GUI_ID_dropdown_systems
    elif (parent == 'Designation Dropdown'):
      id = self.GUI_ID_dropdown_designations
    if id is not None:
      for i in range(len(self.GUI_Elements[id].content)):
        if (self.GUI_Elements[id].scroll_position+i >= 0):
          height = self.GUI_Elements[id].rect[3]
          anchor = (self.GUI_Elements[id].extendedBB[0],self.GUI_Elements[id].extendedBB[1])
          y = lineNr*height
          lineNr+=1
          if (mousepos[1]-anchor[1] > y) and (mousepos[1]-anchor[1] < y + height):
            self.GUI_Elements[id].dropdownSelection = i
            self.GUI_Elements[id].open  = False
            if (parent == 'Bodies Dropdown'):
              id = Systems.GetSystemIDByName(self.game, self.GUI_Elements[id].content[i])
              if (id is not None):
                self.game.currentSystem = id
                self.game.GetNewLocalData(id)
              self.reDraw = True
              break
            elif (parent == 'Designation Dropdown'):
              Designations.Set(self.game.currentSystem, i)
              self.reDraw = True
              break

        
