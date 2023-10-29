import pygame

class Screen():
  def __init__(self, game, events):
    self.reDraw = True
    self.reDraw_GUI = True
    self.game = game
    self.width = game.width
    self.height = game.height
    self.surface = game.surface
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


  def InitGUI(self):
    pass


  def ResetGUI(self):
    self.GUI_Elements = {}
    

  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)

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


  def ToggleGUI(self, id, parent = None):
    if (id in self.GUI_Elements):
      self.reDraw = True
      element = self.GUI_Elements[id]
      #print('Click '+element.name)
      if (element.parent) or (len(element.children) == 0):
        element.enabled = not element.enabled
        self.ToggleGUI_Element_ByName(element.name)
        #element.clickable.enabled = not element.clickable.enabled
      else:
        if (not element.open):
          self.CloseMenus()
        element.open = not element.open

      for childID in element.children:
        if (childID not in self.GUI_Elements):
          print('Error, GUI child %d does not exist for parent %d (%s)'%(childID, id, element.name))
        else:
          child = self.GUI_Elements[childID]
          child.visible = element.open
          child.clickable.enabled = element.open


  def CloseMenus(self):
    for id in self.GUI_Elements:
      element = self.GUI_Elements[id]
      if (not element.parent):
        if (element.open):
          self.ToggleGUI(id)


  def ToggleGUI_Element_ByName(self, name):
    #if (name == 'Show Colonies'):
    #  self.showColonizedBodies = not self.showColonizedBodies
    #elif (name == 'LargeWorlds'):
    #  self.showResourcelessLargeWorlds = not self.showResourcelessLargeWorlds
    #elif (name == 'SmallWorlds'):
    #  self.showResourcelessSmallWorlds = not self.showResourcelessSmallWorlds
    #elif (name == 'Asteroids'):
    #  self.showResourcelessAsteroids = not self.showResourcelessAsteroids
    #elif (name == 'Comets'):
    #  self.showResourcelessComets = not self.showResourcelessComets
    #elif (name == 'Show Installations'):
    #  self.showIndustrializedBodies = not self.showIndustrializedBodies
    #elif (name == 'Show Unsurveyed'):
    #  self.showUnsurveyedBodies = not self.showUnsurveyedBodies
    pass


