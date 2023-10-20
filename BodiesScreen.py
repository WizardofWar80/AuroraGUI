import Table
import pygame
import Utils
import Events
import GUI
from operator import itemgetter

class BodiesScreen():
  def __init__(self, game, events):
    self.game = game
    self.Events = events
    self.surface = game.surface
    self.screen = game.screen
    self.bg_color = game.bg_color

    self.reDraw = True
    self.reDraw_GUI = True
    #['Name', 'Class','Colony Cost','Population Capacity']
    self.table = Table.Table(self, 50, 17, anchor = (20,50), col_widths = [10,150,120,30,50,70,40])
    self.GUI_Elements = {}
    self.currentSystem = game.currentSystem
    self.showColonizedBodies = True
    self.showIndustrializedBodies = True
    self.showUnsurveyedBodies = False
    self.showResourcelessComets = False
    self.showResourcelessAsteroids = False
    self.showResourcelessSmallWorlds = False
    self.showResourcelessLargeWorlds = False
    self.showLowCCBodies = True
    self.highColonyCostThreshold = 3

    self.GUI_Table_Header_Anchor = self.table.anchor
    self.GUI_Table_identifier = 'Bodies Table'
    self.GUI_Table_radioGroup = 1


  def InitGUI(self):
    idGUI = 0
    for cell in self.table.cells[0]:
      gui_cl = self.game.MakeClickable(cell.value, cell.rect, self.SortTableGUI, par=idGUI, parent=self.GUI_Table_identifier)
      self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, cell.value, cell.rect, gui_cl, enabled = True if idGUI == 0 else False, radioButton = True, radioGroup = self.GUI_Table_radioGroup, state = 0)
      idGUI += 1


  def UpdateGUI(self):
    for i in range(len(self.table.cells[0])):
      self.GUI_Elements[i].rect = self.table.cells[0][i].rect


  def SortTableGUI(self, id, parent = None):
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
    system = self.game.starSystems[self.currentSystem]
    text_widths = []
    unsortedIDs = []
    for bodyID in self.game.systemBodies:
      cond = self.GetDrawConditions(self.game.systemBodies[bodyID])
      if (cond):
        unsortedIDs.append([bodyID, self.game.systemBodies[bodyID]['Distance2Center'], self.game.systemBodies[bodyID]['Name'], self.game.systemBodies[bodyID]['Type'] , self.game.systemBodies[bodyID]['ColonyCost'], self.game.systemBodies[bodyID]['Population Capacity'], self.game.systemBodies[bodyID]['Colonizable']])
        for id in Utils.MineralNames:
          unsortedIDs[-1].append(self.game.systemBodies[bodyID]['Deposits'][Utils.MineralNames[id]]['Amount'])
        #unsortedIDs.append([bodyID, self.game.systemBodies[bodyID]['Population Capacity']])
        #unsortedIDs.append([bodyID, self.game.systemBodies[bodyID]['ColonyCost']])
    
    id, rev = self.GetTableSortState()
    sortedIDs = sorted(unsortedIDs, key=itemgetter(id+1), reverse=rev)
      
    row = 0
    header = ['AU', 'Name', 'Type','CC','Pop Cap', 'Colonizable']
    for id in Utils.MineralNames:
      header.append(Utils.MineralNames[id][:2])
    self.table.AddRow(row, header)

    row = 1
    for row_sorted in sortedIDs:
      bodyID = row_sorted[0]
    #for bodyID in self.game.systemBodies:
      body = self.game.systemBodies[bodyID]
      data = [ int(round(body['Distance2Center'],0)) if (body['Distance2Center']>= 10) else round(body['Distance2Center'],1)
              ,body['Name'] 
              ,body['Type'] 
              ,round(body['ColonyCost'],1)
              ,f"{round(body['Population Capacity'],2):,}"
              ,body['Colonizable']
              #,Utils.GetFormattedNumber(body['Distance2Center'])
              ]
      index = 6
      for id in Utils.MineralNames:
        data.append(None)
      if ('Deposits' in body):
        for id in Utils.MineralNames:
          if Utils.MineralNames[id] in body['Deposits']:
            val = body['Deposits'][Utils.MineralNames[id]]['Amount']
            data[index] = '' if val == 0 else Utils.ConvertNumber2kMGT(val) + '  (' + str(body['Deposits'][Utils.MineralNames[id]]['Accessibility']) + ')'
          index += 1
      self.table.AddRow(row, data)
      row += 1
      if (row > self.table.num_rows):
        break
    self.table.FormatColumnIfValuesBetween(3,0,self.highColonyCostThreshold,text_color = Utils.GREEN)
    self.table.FormatColumnIfValuesAbove(3,self.highColonyCostThreshold,text_color = Utils.RED)
    self.table.Realign()
    self.table.FormatColumn(0,align = 'center')
    self.table.FormatColumn(3,align = 'right')
    self.table.FormatColumn(4,align = 'right')
    self.table.FormatColumn(5,align = 'center')
    
    if (self.GUI_Elements == {}):
      self.InitGUI()
    else:
      self.UpdateGUI()
    self.reDraw = True
    t2 = pygame.time.get_ticks()
    deltaTime = t2- t1
    print(deltaTime)


  def DrawGUI(self):
    if (self.reDraw_GUI):
      for GUI_ID in self.GUI_Elements:
        element = self.GUI_Elements[GUI_ID]
        if (element.visible):
          if (element.enabled):
            color = Utils.TEAL
          else:
            color = Utils.DARK_GRAY
          if (element.state == 0):
            heading = 270
          else:
            heading = 90
          Utils.DrawTriangle(self.surface,(element.rect[0]+element.rect[2]-7,element.rect[1]+0.5*element.rect[3]), color, heading)
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

