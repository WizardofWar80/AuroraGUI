import Table
import pygame
import Utils
import Events

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
    self.table = Table.Table(self, 50, 17, anchor = (20,50), col_widths = [150,120,50,70,70,55,40])
    self.GUI_Elements = []
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

  def InitGUI(self):
    pass
    #idGUI = 1
    #x = self.GUI_Bottom_Anchor[0]
    #y = self.GUI_Bottom_Anchor[1]
    #size = 32
    #bb = (x,y,size,size)
    #name = 'Show Bodies'
    #gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    #self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl)
    #showBodiesGUI = self.GUI_Elements[idGUI]
    #parentName = name


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      self.UpdateTable()
      if (self.Events):
        self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)

      reblit |= self.table.Draw()

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit


  def UpdateTable(self):
    self.table.cells[0]
    system = self.game.starSystems[self.currentSystem]
    row = 0
    data = ['Name', 'Type','CC','Pop Cap', 'Colonizable', 'Dist(AU)']
    for id in Utils.MineralNames:
      data.append(Utils.MineralNames[id][:2])
    self.table.AddRow(row, data)

    row = 1
    for bodyID in self.game.systemBodies:
      body = self.game.systemBodies[bodyID]
      cond = self.GetDrawConditions(body)
      if (cond):
        data = [ body['Name'] 
                ,body['Type'] 
                ,round(body['ColonyCost'],1)
                ,f"{round(body['Population Capacity'],2):,}"
                ,True if body['ColonyCost'] < 10000 else False
                #,Utils.GetFormattedNumber(body['Distance2Center'])
                ,int(round(body['Distance2Center'],0)) if (body['Distance2Center']>= 10) else round(body['Distance2Center'],1)
               ]
        index =6
        for id in Utils.MineralNames:
          data.append(None)
        if ('Deposits' in body):
          for id in Utils.MineralNames:
            if Utils.MineralNames[id] in body['Deposits']:
              data[index] = Utils.ConvertNumber2kMGT(body['Deposits'][Utils.MineralNames[id]]['Amount'])
            index += 1
        self.table.AddRow(row, data)
        row += 1
        if (row > self.table.num_rows):
          break
    self.table.FormatColumnIfValuesBetween(2,0,self.highColonyCostThreshold,text_color = Utils.GREEN)
    self.table.FormatColumnIfValuesAbove(2,self.highColonyCostThreshold,text_color = Utils.RED)
    self.reDraw = True


  def DrawGUI(self):
    if (self.reDraw_GUI):
      for GUI_ID in self.GUI_Elements:
        element = self.GUI_Elements[GUI_ID]
        if (element.visible):
          element.Draw(self.surface)
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

