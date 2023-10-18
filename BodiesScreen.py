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
    self.table = Table.Table(self, 10, 5, anchor = (20,50), col_widths = [20,150,50,200,200])
    self.GUI_Elements = []
      
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

