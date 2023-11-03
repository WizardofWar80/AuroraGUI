import pygame
import sqlite3
import logger as lg
import Utils
import math
import random
import Clickable
import GUI
import Bodies
import InfoWindow
import Fleets
import Colonies
import Systems
from Screen import Screen

class SystemScreen(Screen):
  def __init__(self, game, events):
    self.reDraw = True
    self.reDraw_GUI = True
    self.reDraw_FleetInfoWindow = True
    self.reDraw_InfoWindow = True
    self.reDraw_MapWindow = True
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
    self.systemScaleStart = 50
    self.systemScale = self.systemScaleStart

    self.radius_Sun = 696000
    self.minPixelSize_Star = 15
    self.minPixelSize_Planet = 9
    self.minPixelSize_Moon = 5
    self.minPixelSize_Small = 5
    self.mouseDragged = (0,0)
    # Options
    self.bg_color = Utils.BLACK
    self.showEmptyFleets = False
    self.showMilitaryFleets = True
    self.showCommercialFleets = True
    self.showStationaryFleets = False
    self.showUnsurveyedLocations = True
    self.showSurveyedLocations = False
    self.show_FleetTraces = True
    self.show_Planets = True
    self.show_Moons = True
    self.show_DwarfPlanets = True
    self.show_Comets = True
    self.show_Asteroids = False

    self.showColonizedBodies = True
    self.showIndustrializedBodies = True
    self.showUnsurveyedBodies = True
    self.showEnemyBodies = True
    self.showResourcefulBodies = True
    self.showXenosBodies = True
    self.showArtifactsBodies = True

    self.highlightColonizedBodies = True
    self.highlightIndustrializedBodies = True
    self.highlightUnsurveyedBodies = True
    self.highlightEnemyBodies = True
    self.highlightResourcefulBodies = True
    self.highlightXenosBodies = True
    self.highlightArtifactsBodies = True

    self.showOrbits_Planets = True
    self.showOrbits_DwarfPlanets = True
    self.showOrbits_Moons = True
    self.showOrbits_Comets = False
    self.showOrbits_Asteroids = False
    self.showOrbits_Stars = True

    self.showLabels_Planets = True
    self.showLabels_DwarfPlanets = True
    self.showLabels_Moons = True
    self.showLabels_Comets = True
    self.showLabels_Asteroids = False
    self.showLabels_Stars = True
    self.minDist4Labels = 100
    
    # Colorscheme
    self.color_JP = Utils.ORANGE
    self.color_Jumpgate = Utils.ORANGE
    self.color_SurveyedLoc = Utils.TEAL
    self.color_UnsurveyedLoc = Utils.BLUE
    self.color_Fleet = Utils.GREEN

    # bodies
    self.color_Star = Utils.YELLOW
    self.color_Planet = Utils.MED_GREEN
    self.color_DwarfPlanet = Utils.MED_GREEN
    self.color_Moon = Utils.GREEN
    self.color_Asteroid = Utils.GRAY
    self.color_Comet = Utils.BLUE

    # body labels
    self.color_Label_Star = Utils.WHITE
    self.color_Label_Planet = Utils.WHITE
    self.color_Label_DwarfPlanet = Utils.WHITE
    self.color_Label_Moon = Utils.WHITE
    self.color_Label_Asteroid = Utils.WHITE
    self.color_Label_Comet = Utils.WHITE

    # body orbits
    self.color_Orbit_Star = Utils.YELLOW
    self.color_Orbit_Planet = Utils.DARK_GRAY
    self.color_Orbit_DwarfPlanet = Utils.DARK_GRAY
    self.color_Orbit_Moon = Utils.DARK_GRAY
    self.color_Orbit_Asteroid = Utils.SUPER_DARK_GRAY
    self.color_Orbit_Comet = Utils.SUPER_DARK_GRAY
    self.images_Body = {}

    self.Events = events
    self.surface = game.surface
    self.screen = game.screen
    self.bg_color = game.bg_color

    self.window_fleet_info_identifier = 'Fleet Info Window'
    self.window_fleet_info_size = (300,545)
    self.window_map_size = (self.window_fleet_info_size[0],self.window_fleet_info_size[0])

    self.window_fleet_info_anchor = (5,self.height-self.window_map_size[1]-self.window_fleet_info_size[1]-2*5)#(self.width-self.window_fleet_info_size[0]-5,self.height-self.window_map_size[1]-self.window_fleet_info_size[1]-2*5)
    self.window_fleet_info = pygame.Surface(self.window_fleet_info_size, pygame.SRCALPHA,32)
    self.window_fleet_info_rect = pygame.Rect(self.window_fleet_info_anchor, self.window_fleet_info_size)
    self.window_fleet_info.set_colorkey(Utils.GREENSCREEN)
    self.reDraw_FleetInfoWindow = True;
    self.window_fleet_info_scoll_pos = 0
    self.highlighted_fleet_ID = -1
    self.highlighted_body_ID = -1


    self.window_info_identifier = 'Info Window'
    self.window_info_size = (300,600)
    self.window_info_anchor = (self.width-self.window_info_size[0]-5,self.height-self.window_fleet_info_size[1]-5)#(self.width-self.window_fleet_info_size[0]-5,self.height-self.window_map_size[1]-self.window_fleet_info_size[1]-2*5)
    self.window_info = pygame.Surface(self.window_info_size, pygame.SRCALPHA,32)
    self.window_info_rect = pygame.Rect(self.window_info_anchor, self.window_info_size)
    self.window_info.set_colorkey(Utils.GREENSCREEN)
    self.reDraw_InfoWindow = True
    self.window_info_scoll_pos = 0
    self.info_category_physical = 'Physical Info'
    self.info_cat_phys_expanded = True
    self.info_category_economical = 'Economical Info'
    self.info_cat_eco_expanded = False
    self.info_category_orbit = 'Orbit Info'
    self.info_cat_orbit_expanded = False
    self.info_category_stockpile = 'Stockpile'
    self.info_cat_stock_expanded = True
    self.info_category_installations = 'Installations'
    self.info_cat_inst_expanded = True
    self.info_category_deposits = 'Mineral Deposits'
    self.info_cat_deposits_expanded = True

    self.window_map_anchor = (5,self.height-self.window_map_size[1]-5)#(self.width-self.window_map_size[0]-5,self.height-self.window_map_size[1]-5)
    self.window_map = pygame.Surface(self.window_map_size, pygame.SRCALPHA,32)
    self.window_map_rect = pygame.Rect(self.window_map_anchor, self.window_map_size)
    self.window_map.set_colorkey(Utils.GREENSCREEN)
    self.reDraw_MapWindow = True;
    self.GUI_identifier = 'System Screen GUI'
    self.GUI_Elements = {}
    self.GUI_Bottom_Anchor = (500,game.height-50)
    self.GUI_Left_Anchor = (15,self.window_fleet_info_rect[1]-50)
    self.images_GUI = {}
    self.GUI_expanded_fleets = []
    self.GUI_expanded_fleets2 = []
    self.GUI_expanded_fleets3 = []
    #self.InitGUI()

      
  def InitGUI(self):
    idGUI = 1
    x = self.GUI_Bottom_Anchor[0]
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Show Bodies'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button')
    showBodiesGUI = self.GUI_Elements[idGUI]
    parentName = name

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Planets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showBodiesGUI.GetID(), enabled = self.show_Planets)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Moons'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showBodiesGUI.GetID(), enabled = self.show_Moons)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Asteroids'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', parent=showBodiesGUI.GetID(), enabled = self.show_Asteroids)
    showBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Comets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showBodiesGUI.GetID(), enabled = self.show_Comets)
    showBodiesGUI.AddChildren(idGUI)

    # Second Column
    idGUI += 1
    x += size+5
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Show Orbits'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button')
    showOrbitsGUI = self.GUI_Elements[idGUI]
    parentName = name

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Planet Orbits'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showOrbitsGUI.GetID(), enabled = self.showOrbits_Planets)
    showOrbitsGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Moon Orbits'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showOrbitsGUI.GetID(), enabled = self.showOrbits_Moons)
    showOrbitsGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Asteroid Orbits'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', parent=showOrbitsGUI.GetID(), enabled = self.showOrbits_Asteroids)
    showOrbitsGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Show Comet Orbits'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=showOrbitsGUI.GetID(), enabled = self.showOrbits_Comets)
    showOrbitsGUI.AddChildren(idGUI)

    # Third Column
    idGUI += 1
    x += size+5
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Filter'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button')
    FilterBodiesGUI = self.GUI_Elements[idGUI]
    parentName = name

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Filter Colonies'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=FilterBodiesGUI.GetID(), enabled = self.showColonizedBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Filter Resources'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=FilterBodiesGUI.GetID(), enabled = self.showResourcefulBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Filter Installations'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=FilterBodiesGUI.GetID(), enabled = self.showIndustrializedBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Filter Unsurveyed'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', parent=FilterBodiesGUI.GetID(), enabled = self.showUnsurveyedBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Filter Enemies'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=FilterBodiesGUI.GetID(), enabled = self.showEnemyBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Filter Xenos'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=FilterBodiesGUI.GetID(), enabled = self.showXenosBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Filter Artifacts'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=FilterBodiesGUI.GetID(), enabled = self.showArtifactsBodies)
    FilterBodiesGUI.AddChildren(idGUI)

    # Fourth Column
    idGUI += 1
    x += size+5
    y = self.GUI_Bottom_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Highlight'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button')
    HighlightGUI = self.GUI_Elements[idGUI]
    parentName = name

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Highlight Colonies'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=HighlightGUI.GetID(), enabled = self.highlightColonizedBodies)
    HighlightGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Highlight Resources'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=HighlightGUI.GetID(), enabled = self.highlightResourcefulBodies)
    HighlightGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Highlight Installations'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=HighlightGUI.GetID(), enabled = self.highlightIndustrializedBodies)
    HighlightGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Highlight Unsurveyed'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name, bb, gui_cl, 'Button', parent=HighlightGUI.GetID(), enabled = self.highlightUnsurveyedBodies)
    HighlightGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Highlight Enemies'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=HighlightGUI.GetID(), enabled = self.highlightEnemyBodies)
    HighlightGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Highlight Xenos'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=HighlightGUI.GetID(), enabled = self.highlightXenosBodies)
    HighlightGUI.AddChildren(idGUI)

    idGUI += 1
    y += -size-5
    bb = (x,y,size,size)
    name = 'Highlight Artifacts'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier, enabled = False)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', parent=HighlightGUI.GetID(), enabled = self.highlightArtifactsBodies)
    HighlightGUI.AddChildren(idGUI)

    # Left GUI
    idGUI += 1
    x = self.GUI_Left_Anchor[0]
    y = self.GUI_Left_Anchor[1]
    size = 32
    bb = (x,y,size,size)
    name = 'Show Empty Fleets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.showEmptyFleets)

    idGUI += 1
    x += size+5
    size = 32
    bb = (x,y,size,size)
    name = 'Show Military Fleets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.showMilitaryFleets)

    idGUI += 1
    x += size+5
    size = 32
    bb = (x,y,size,size)
    name = 'Show Commercial Fleets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.showCommercialFleets)

    idGUI += 1
    x += size+5
    size = 32
    bb = (x,y,size,size)
    name = 'Show Stationary Fleets'
    gui_cl = self.game.MakeClickable(name, bb, self.ToggleGUI, par=idGUI, parent=self.GUI_identifier)
    self.GUI_Elements[idGUI] = GUI.GUI(self, idGUI, name,bb, gui_cl, 'Button', enabled = self.showStationaryFleets)


  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      if (self.Events):
        self.Events.ClearClickables(exclude = self.GUI_identifier)
      self.reDraw_FleetInfoWindow = True
      self.reDraw_InfoWindow = True
      self.reDraw_MapWindow = True
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)

      reblit |= self.DrawSystem()

    reblit |= self.DrawMiniMap()

    reblit |= Fleets.DrawFleetInfoWindow(self)

    reblit |= InfoWindow.Draw(self)

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.counter_FPS += 1

    currentTimestamp = pygame.time.get_ticks()
    deltaTime = currentTimestamp - self.timestampLastSecond
    if (deltaTime >= 1000):
      #self.FPS = 1000*self.counter_FPS / deltaTime
      self.FPS = self.counter_FPS 
      self.counter_FPS = 0
      self.timestampLastSecond = currentTimestamp
    Utils.DrawText2Screen(self.screen,'%d FPS'%(self.FPS),(5,50),18,Utils.WHITE, False)
    # draw mouse position and scale
    #Utils.DrawText2Screen(self.screen,'(%d,%d) Scale: %3.1f'%(self.mousePos[0], self.mousePos[1], self.systemScale),(5,5),18,Utils.WHITE, False)
    #Utils.DrawText2Screen(self.screen,'(%d,%d)'%(self.mouseDragged[0], self.mouseDragged[1]),(5,25),18,Utils.WHITE, False)

    self.reDraw = False
    
    return reblit

  
  def DrawMiniMap(self):
    if (self.reDraw_MapWindow):
      self.window_map.fill(Utils.SUPER_DARK_GRAY)

      self.surface.blit(self.window_map,self.window_map_anchor)
      self.reDraw_MapWindow = False
      return True
    else:
      return False


  #def DrawGUI(self):
  #  if (self.reDraw_GUI):
  #    for GUI_ID in self.GUI_Elements:
  #      element = self.GUI_Elements[GUI_ID]
  #      if (element.visible):
  #        element.Draw(self.surface)
  #    self.reDraw_GUI = False
  #    return True
  #  else:
  #    return False


  def DrawSystem(self):
    Bodies.Draw(self)
    Systems.DrawSystemJumpPoints(self)
    Systems.DrawSurveyLocations(self)
    Fleets.DrawSystemFleets(self)
    return True


  def WorldPos2ScreenPos(self, world_pos):
    scaled_world_pos = Utils.MulTuples(world_pos,(Utils.AU_INV*self.systemScale))

    return Utils.AddTuples(self.screenCenter ,scaled_world_pos)

    
  def ExpandFleet(self, id, parent):
    game = self.game
    if (id in game.fleets[game.currentSystem]):
      if (parent == self.window_fleet_info_identifier):
        if (id in self.GUI_expanded_fleets):
          self.GUI_expanded_fleets.remove(id)
        else:
          self.GUI_expanded_fleets.append(id)
        self.reDraw_FleetInfoWindow = True
      elif (parent == self.window_info_identifier):
        if (id in self.GUI_expanded_fleets2):
          self.GUI_expanded_fleets2.remove(id)
        else:
          self.GUI_expanded_fleets2.append(id)
        self.reDraw_InfoWindow = True


  def ExpandBodyInfo(self, category, parent):
    if (category == self.info_category_physical):
      self.info_cat_phys_expanded = not self.info_cat_phys_expanded
    elif (category == self.info_category_economical):
      self.info_cat_eco_expanded = not self.info_cat_eco_expanded
    elif (category == self.info_category_orbit):
      self.info_cat_orbit_expanded = not self.info_cat_orbit_expanded
    elif (category == self.info_category_stockpile):
      self.info_cat_stock_expanded = not self.info_cat_stock_expanded
    elif (category == self.info_category_installations):
      self.info_cat_inst_expanded = not self.info_cat_inst_expanded
    elif (category == self.info_category_deposits):
      self.info_cat_deposits_expanded = not self.info_cat_deposits_expanded

    self.reDraw_InfoWindow = True


  def ExpandShipClasses(self, shipClass, parent):
    if (shipClass in self.GUI_expanded_fleets3):
      self.GUI_expanded_fleets3.remove(shipClass)
    else:
      self.GUI_expanded_fleets3.append(shipClass)
    self.reDraw_InfoWindow = True


  def ToggleGUI_Element_ByName(self, name):
    #self.showEmptyFleets = False
    #self.showStationaryFleets = False
    #self.showUnsurveyedLocations = True
    #self.showSurveyedLocations = False
    #self.showFleetTraces = True
    #self.showDwarfPlanets = True
    #self.showLabels_Planets = True
    #self.showLabels_DwarfPlanets = True
    #self.showLabels_Moons = True
    #self.showLabels_Comets = True
    #self.showLabels_Asteroids = False
    #self.showLabels_Stars = True

    if (name == 'Show Planets'):
      self.show_Planets = not self.show_Planets
      self.show_DwarfPlanets = self.show_Planets
    elif (name == 'Show Moons'):
      self.show_Moons = not self.show_Moons
    elif (name == 'Show Comets'):
      self.show_Comets = not self.show_Comets
    elif (name == 'Show Asteroids'):
      self.show_Asteroids = not self.show_Asteroids
    elif (name == 'Show Planet Orbits'):
      self.showOrbits_Planets = not self.showOrbits_Planets
      self.showOrbits_DwarfPlanets = self.showOrbits_Planets
    elif (name == 'Show Moon Orbits'):
      self.showOrbits_Moons = not self.showOrbits_Moons
    elif (name == 'Show Comet Orbits'):
      self.showOrbits_Comets = not self.showOrbits_Comets
    elif (name == 'Show Asteroid Orbits'):
      self.showOrbits_Asteroids = not self.showOrbits_Asteroids
    elif (name == 'Filter Colonies'):
      self.showColonizedBodies = not self.showColonizedBodies
    elif (name == 'Filter Resources'):
      self.showResourcefulBodies = not self.showResourcefulBodies
    elif (name == 'Filter Installations'):
      self.showIndustrializedBodies = not self.showIndustrializedBodies
    elif (name == 'Filter Unsurveyed'):
      self.showUnsurveyedBodies = not self.showUnsurveyedBodies
    elif (name == 'Filter Enemies'):
      self.showEnemyBodies = not self.showEnemyBodies
    elif (name == 'Filter Xenos'):
      self.showXenosBodies = not self.showXenosBodies
    elif (name == 'Filter Artifacts'):
      self.showArtifactsBodies = not self.showArtifactsBodies
    elif (name == 'Highlight Colonies'):
      self.highlightColonizedBodies = not self.highlightColonizedBodies
    elif (name == 'Highlight Resources'):
      self.highlightResourcefulBodies = not self.highlightResourcefulBodies
    elif (name == 'Highlight Installations'):
      self.highlightIndustrializedBodies = not self.highlightIndustrializedBodies
    elif (name == 'Highlight Unsurveyed'):
      self.highlightUnsurveyedBodies = not self.highlightUnsurveyedBodies
    elif (name == 'Highlight Enemies'):
      self.highlightEnemyBodies = not self.highlightEnemyBodies
    elif (name == 'Highlight Xenos'):
      self.highlightXenosBodies = not self.highlightXenosBodies
    elif (name == 'Highlight Artifacts'):
      self.highlightArtifactsBodies = not self.highlightArtifactsBodies
    elif (name == 'Show Empty Fleets'):
      self.showEmptyFleets = not self.showEmptyFleets
    elif (name == 'Show Military Fleets'):
      self.showMilitaryFleets = not self.showMilitaryFleets
    elif (name == 'Show Commercial Fleets'):
      self.showCommercialFleets = not self.showCommercialFleets
    elif (name == 'Show Stationary Fleets'):
      self.showStationaryFleets = not self.showStationaryFleets


  def Follow_Jumppoint(self, id, parent):
    if (id in self.game.starSystems):
      self.game.currentSystem = id
      self.window_fleet_info_scoll_pos = 0
      InfoWindow.CleanUp(self, self.window_fleet_info_identifier)
      InfoWindow.CleanUp(self, self.window_info_identifier)
      self.game.GetNewLocalData(id)
      self.reDraw = True


  def ZoomTo(self, world_pos, zoom_level):
    print(world_pos)
    self.systemScale=zoom_level
    scaled_position = Utils.MulTuples(world_pos,(Utils.AU_INV*self.systemScale))
    self.screenCenter = Utils.SubTuples(self.game.screenCenter, scaled_position)
    #self.systemScale = 10

  #def ToggleGUI(self, id, parent = None):
  #  if (id in self.GUI_Elements):
  #    self.reDraw = True
  #    element = self.GUI_Elements[id]
  #    #print('Click '+element.name)
  #    if (element.parent) or (len(element.children) == 0):
  #      element.enabled = not element.enabled
  #      self.ToggleGUI_Element_ByName(element.name)
  #      #element.clickable.enabled = not element.clickable.enabled
  #    else:
  #      if (not element.open):
  #        self.CloseMenus()
  #      element.open = not element.open

  #    for childID in element.children:
  #      if (childID not in self.GUI_Elements):
  #        print('Error, GUI child %d does not exist for parent %d (%s)'%(childID, id, element.name))
  #      else:
  #        child = self.GUI_Elements[childID]
  #        child.visible = element.open
  #        child.clickable.enabled = element.open


  #def CloseMenus(self):
  #  for id in self.GUI_Elements:
  #    element = self.GUI_Elements[id]
  #    if (not element.parent):
  #      if (element.open):
  #        self.ToggleGUI(id)
