import Table
import pygame
import Utils
import Events
import GUI
import Tab
from Screen import Screen
from operator import itemgetter

class CommandsScreen(Screen):
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
    self.GUI_identifier = 'CommandTabs'
    self.images_GUI = {}
    self.tab_pos = (50,100)
    self.tab_size = (game.width-100,game.height-game.GUI_Top_Anchor[1]-100)
    self.tabs = {'Navy': Tab.Tab(self.game, self.Events, self, self.tab_size, self.tab_pos),
                 'Ground': Tab.Tab(self.game, self.Events, self, self.tab_size, self.tab_pos),
                 'Admin': Tab.Tab(self.game, self.Events, self, self.tab_size, self.tab_pos)
                 }
    self.active_tab = 'Navy'
    self.indentLevel = 0
    self.unscrollableLineNr = 0
    self.cursorPos = (0,0)
    self.lineNr = 0
    self.pad_x = 5
    self.pad_y = 5
    self.line_height = 22
    self.textColor = Utils.WHITE
    self.textSize = 15
    self.indentWidth = 25
    self.ranks = {}
    self.navyCommands = {}
    self.navyMainCommand = 0

    #self.UpdateCommandData()

  def Clear(self):
    self.cursorPos = (0,0)
    self.pad_x = 5
    self.pad_y = 5
    self.lineNr = 0
    self.unscrollableLineNr = 0


  def UpdateCommandData(self):
    if (self.GUI_Elements == {}):
      self.InitGUI()
    else:
      self.UpdateGUI()
    self.GetCommandData()
    #self.GetWealthData()
    #self.GetPopulationData()
    #self.GetStockpileData()
    #self.GetShipData()
    #self.GetStationData()


  def UpdateGUI(self):
    pass


  def InitGUI(self):
    idGUI = 1
    x = self.tab_pos[0]
    y = self.tab_pos[1]-self.GUI_Button_Size[1]
    bb = (x,y,self.GUI_Button_Size[0],self.GUI_Button_Size[1])
    name = 'Navy'
    gui_cl = self.game.MakeClickable(name, bb, self.SwitchTabs, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, tab = True, enabled = True if self.active_tab == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Button_Size[0]+5
    bb = (x,y,self.GUI_Button_Size[0],self.GUI_Button_Size[1])
    name = 'Ground'
    gui_cl = self.game.MakeClickable(name, bb, self.SwitchTabs, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, tab = True, enabled = True if self.active_tab == name else False, radioButton = True, radioGroup = 0)

    idGUI += 1
    x += self.GUI_Button_Size[0]+5
    bb = (x,y,self.GUI_Button_Size[0],self.GUI_Button_Size[1])
    name = 'Admin'
    gui_cl = self.game.MakeClickable(name, bb, self.SwitchTabs, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', textButton = True, tab = True, enabled = True if self.active_tab == name else False, radioButton = True, radioGroup = 0)


  def GetCommandData(self):
    self.GetRanks()
    self.navyCommands = {}
    self.navyMainCommand = 0
    self.RecursiveReadCommandData(0)
  

  def GetRanks(self):
    self.ranks = {}
    ranks = self.game.db.execute('''SELECT * from FCT_Ranks WHERE GameID = %d and RaceID = %d and RankType = 0;'''%(self.game.gameID, self.game.myRaceID)).fetchall()
    for r in ranks:
      self.ranks[r[0]] = {'Rank':r[2], 'Level':r[3], 'ID':r[0], 'Abbr':r[5]}

  def GetRankOfLevel(self, level):
    for ID in self.ranks:
      if level == self.ranks[ID]['Level']:
        return ID
    return None


  def RecursiveReadCommandData(self, parentID):
    commands = self.game.db.execute('''SELECT NavalAdminCommandID, AdminCommandName, MinimumRankPriority from FCT_NavalAdminCommand WHERE GameID = %d and RaceID = %d and ParentAdminCommandID = %d;'''%(self.game.gameID, self.game.myRaceID, parentID)).fetchall()
    for c in commands:
      commandID, commandName, minLevel = c
      cmdr_fields = self.game.db.execute('''SELECT Name, RankID from FCT_Commander WHERE GameID = %d and RaceID = %d and CommandID = %d;'''%(self.game.gameID, self.game.myRaceID, commandID)).fetchall()
      name = None
      rankID = None
      rank = None
      abbr = None
      level = None
      minLevelRankID = self.GetRankOfLevel(minLevel)
      if len(cmdr_fields) > 0:
        name, rankID = cmdr_fields[0]
        rank = self.ranks[rankID]['Rank'] if rankID in self.ranks else None
        abbr = self.ranks[rankID]['Abbr'] if rankID in self.ranks else None
        level = self.ranks[rankID]['Level'] if rankID in self.ranks else None
      self.navyCommands[commandID]={'ID':commandID, 'Name':commandName, 'ParentID':parentID, 'Commander':name, 'Level':level, 'Rank':rank, 'RankAbbr':abbr, 'SubCommands': [], 'Min Rank ID':minLevelRankID}
      # paranoia IF should not really happen
      if (parentID in self.navyCommands):
        self.navyCommands[parentID]['SubCommands'].append(commandID)
      self.RecursiveReadCommandData(commandID)
      if (parentID == 0):
        self.navyMainCommand = commandID


  def DrawCommandWithSubs(self, commandID):
    if (commandID in self.navyCommands):
      text = self.navyCommands[commandID]['Name'] + ' :  '
      labelsize = Utils.DrawLineOfText(self, self.surface,text, self.indentLevel, unscrollable = True, anchor=self.tab_pos)
      self.lineNr -= 1
      if (labelsize):
        if (self.navyCommands[commandID]['Commander']):
          text = self.navyCommands[commandID]['Rank'] + ' ' + self.navyCommands[commandID]['Commander']
          labelsize = Utils.DrawLineOfText(self, self.surface,text, self.indentLevel, offset=labelsize[0], unscrollable = True,anchor=self.tab_pos)
        else:
          mri = self.navyCommands[commandID]['Min Rank ID']
          if (mri):
            minRank = self.ranks[mri]['Rank']
          else:
            minRank = '-'
          text = 'No commander (%s)'%minRank
          labelsize = Utils.DrawLineOfText(self, self.surface,text, self.indentLevel, offset=labelsize[0], color = Utils.RED, unscrollable = True,anchor=self.tab_pos)

      self.indentLevel += 1
      for sub in self.navyCommands[commandID]['SubCommands']:
        self.DrawCommandWithSubs(sub)
      self.indentLevel -= 1


  def DrawData(self):
    self.Clear()
    self.surface.fill(self.bg_color)
    pygame.draw.rect(self.surface, Utils.GRAY, (self.tab_pos,self.tab_size),3)
    self.category = 'Navy'
    if (self.active_tab == 'Navy'):
      self.DrawCommandWithSubs(self.navyMainCommand)
      #Utils.DrawLineOfText(self, self.surface,'Commander', self.indentLevel, unscrollable = True,anchor=self.tab_pos)


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      self.DrawData()
      #self.tabs[self.active_tab].Draw(self.surface)

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit


  def SwitchTabs(self, id, parent, mousepos):
    thisGroup = None
    thisElement = None
    if (id in self.GUI_Elements):
      thisElement = self.GUI_Elements[id]
      if (thisElement.radioButton):
        thisGroup = thisElement.radioGroup
        if (not thisElement.enabled):
          thisElement.enabled = True
          self.reDraw = True
          self.reDraw_GUI = True
          self.active_tab = thisElement.name
          for otherID in self.GUI_Elements:
            if (otherID != id):
              otherElement = self.GUI_Elements[otherID]
              if (otherElement.radioButton):
                if (otherElement.radioGroup == thisGroup):
                  otherElement.enabled = False