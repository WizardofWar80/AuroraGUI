import time
import pygame
import logger as lg
import Utils

logger = lg.Logger(logfile= 'log_events.txt', module='Events.py', log_level = 1)
logger.Reset()
EVENTS_DEBUG = False

class Events:
  def __init__(self, clickables=[]):
    self.LeftMouseButtonDown = False
    self.LeftMouseButtonClicked = False
    self.LeftMouseButtonDoubleClicked = False
    self.LeftMouseClickPosition = []
    self.LeftMousePressPosition = []
    self.LeftMouseReleasePosition = []
    self.LeftDoubleClickPosition = []

    self.RightMouseButtonDown = False
    self.RightMouseButtonClicked = False
    self.RightMouseButtonDoubleClicked = False
    self.RightMouseClickPosition = []
    self.RightMousePressPosition = []
    self.RightMouseReleasePosition = []
    self.RightDoubleClickPosition = []

    self.TimestampInit = -1000
    self.TimeDeltaInit = 1000
    self.singleClickTiming = 0.7
    self.doubleClickTiming = 0.2
    self.clickables = clickables

    self.TimeLeftMouseButtonPressed = self.TimestampInit
    self.TimeSinceLeftMouseButtonPressed = self.TimeDeltaInit
    self.TimeLeftMouseButtonReleased = self.TimestampInit
    self.TimeSinceLeftMouseButtonReleased = self.TimeDeltaInit
    self.TimeLeftMouseButtonDoubleClick = self.TimestampInit
    self.TimeSinceLeftMouseButtonDoubleClick = self.TimeDeltaInit

    self.TimeRightMouseButtonPressed = self.TimestampInit
    self.TimeSinceRightMouseButtonPressed = self.TimeDeltaInit
    self.TimeRightMouseButtonReleased = self.TimestampInit
    self.TimeSinceRightMouseButtonReleased = self.TimeDeltaInit
    self.TimeRightMouseButtonDoubleClick = self.TimestampInit
    self.TimeSinceRightMouseButtonDoubleClick = self.TimeDeltaInit
    self.lastEnteredElement = None
    self.timestampEnteredElement = self.TimestampInit
    self.timeSinceEnteredElement = self.TimeDeltaInit


  def Update(self, game):
    current_time = self.GetTimeinSeconds()
    # Left Mouse Button
    if (self.TimeLeftMouseButtonReleased > self.TimestampInit):
      self.TimeSinceLeftMouseButtonReleased = current_time - self.TimeLeftMouseButtonReleased
    if (self.TimeLeftMouseButtonPressed > self.TimestampInit):
      self.TimeSinceLeftMouseButtonPressed = current_time - self.TimeLeftMouseButtonPressed
    if (self.TimeLeftMouseButtonDoubleClick > self.TimestampInit):
      self.TimeSinceLeftMouseButtonDoubleClick = current_time - self.TimeLeftMouseButtonDoubleClick
    # Right Mouse Button
    if (self.TimeRightMouseButtonReleased > self.TimestampInit):
      self.TimeSinceRightMouseButtonReleased = current_time - self.TimeRightMouseButtonReleased
    if (self.TimeRightMouseButtonPressed > self.TimestampInit):
      self.TimeSinceRightMouseButtonPressed = current_time - self.TimeRightMouseButtonPressed
    if (self.TimeRightMouseButtonDoubleClick > self.TimestampInit):
      self.TimeSinceRightMouseButtonDoubleClick = current_time - self.TimeRightMouseButtonDoubleClick
    if (self.lastEnteredElement != None):
      self.timeSinceEnteredElement = current_time - self.timestampEnteredElement
      if(self.timeSinceEnteredElement > .7):
        if (not self.lastEnteredElement.hover):
          game.SetRedrawFlag(game.currentScreen)
          if (EVENTS_DEBUG):
            print('hover over %s'%self.lastEnteredElement.name)
          self.lastEnteredElement.hover = True
        


  def ClearClickables(self, volatile_only = False, parent = None, exclude = None):
    listOfElementsToDelete = []
    if (volatile_only):
      for clickable in self.clickables:
        if (clickable.volatile):
          listOfElementsToDelete.append(clickable)
    elif(parent):
      for clickable in self.clickables:
        if (clickable.parent == parent):
          listOfElementsToDelete.append(clickable)
    elif (exclude):
      for clickable in self.clickables:
        if (clickable.parent != exclude):
          if (clickable.parent != 'Global GUI') and (not clickable.persistent):
            listOfElementsToDelete.append(clickable)
    else:
      for clickable in self.clickables:
        if (clickable.parent != 'Global GUI') and (not clickable.persistent):
          listOfElementsToDelete.append(clickable)

    for cl in listOfElementsToDelete:
        self.clickables.remove(cl)
    

  def RemoveClickable(self, cl, parent = None):
    listOfElementsToDelete = []
    if(parent):
      listOfElementsToDelete = []
      for clickable in self.clickables:
        if (clickable.parent == parent) and (cl == clickable.name):
          listOfElementsToDelete.append(clickable)
    else:
      listOfElementsToDelete = []
      for clickable in self.clickables:
        if (clickable.parent != 'Global GUI'):
          if (cl == clickable.name):
            listOfElementsToDelete.append(clickable)
    for cl in listOfElementsToDelete:
        self.clickables.remove(cl)


  def Bind(self, clickable):
    self.clickables.append(clickable)


  def UnBind(self, clickable):
    #self.clickables.append(clickable)
    pass


  def GetTimeinSeconds(self):
    return pygame.time.get_ticks()/1000


  def HandleMouseEvents(self, event, game):
    # The mouse wheel will generate pygame.MOUSEBUTTONDOWN and pygame.MOUSEBUTTONUP events when rolled. 
    # The button will be set to 4 when the wheel is rolled up, and to button 5 when the wheel is rolled down

    if event.type == pygame.MOUSEBUTTONDOWN:
      if (event.button == 4 or event.button == 5):
        self.HandleMouseWheelEvents(event, game)
      else:
        self.HandleMouseDownEvents(event, game)
    if event.type == pygame.MOUSEBUTTONUP:
      self.HandleMouseUpEvents(event)
    if event.type == pygame.MOUSEMOTION:
      self.HandleMouseMotionEvents(event, game)
    if (self.LeftMouseButtonClicked):
      self.HandleSingleClickEvents(1, game)
    if (self.RightMouseButtonClicked):
      self.HandleSingleClickEvents(3, game)
    if (self.LeftMouseButtonDoubleClicked):
      self.HandleDoubleClickEvents(1)


  def HandleKeyboardEvents(self, event, game):
    if (event.type == pygame.KEYDOWN):
      if (event.key == pygame.K_HOME):
        if (game.screenCenter != game.cameraCenter):
          game.screenCenter = game.cameraCenter
        else:
          game.systemScale = game.systemScaleStart
        game.reDraw = True
      if (event.key == pygame.K_d):
        game.Debug = not game.Debug
        game.reDraw = True


  def HandleMouseDownEvents(self, event,game):
    current_time = self.GetTimeinSeconds()
    if (event.button == 1):
      #logger.write('Button %d down at: %d,%d'%(event.button,event.pos[0], event.pos[1]))
      #print('LMB')
      if(not self.LeftMouseButtonDown):
        game.systemScreen.screenCenterBeforeDrag = game.systemScreen.screenCenter
      if (self.TimeSinceLeftMouseButtonReleased < self.doubleClickTiming):
        self.LeftMouseButtonDoubleClicked = True
        self.TimeLeftMouseButtonDoubleClick = current_time
        self.TimeSinceLeftMouseButtonDoubleClick = 0
        self.LeftDoubleClickPosition = event.pos

      self.TimeSinceLeftMouseButtonReleased = current_time - self.TimeLeftMouseButtonReleased
      self.TimeLeftMouseButtonPressed = current_time
      self.LeftMouseButtonDown = True
      #print('Left MB was released for %3.2fs'%self.TimeSinceLeftMouseButtonReleased)
      self.TimeLeftMouseButtonReleased = -1000
      self.TimeSinceLeftMouseButtonReleased = 1000
      self.LeftMousePressPosition = event.pos
    elif (event.button == 2):
      print('unhandled event for mouse button 2')
      print(event)
      logger.write('Unhandled Button %d down'%event.button)
    elif (event.button == 3):
      #logger.write('Button %d down at: %d,%d'%(event.button,event.pos[0], event.pos[1]))
      #print('LMB')
      if(not self.RightMouseButtonDown):
        game.screenCenterBeforeDrag = game.screenCenter
      if (self.TimeSinceRightMouseButtonReleased < self.doubleClickTiming):
        self.RightMouseButtonDoubleClicked = True
        self.TimeRightMouseButtonDoubleClick = current_time
        self.TimeSinceRightMouseButtonDoubleClick = 0
        self.RightDoubleClickPosition = event.pos

      self.TimeSinceRightMouseButtonReleased = current_time - self.TimeRightMouseButtonReleased
      self.TimeRightMouseButtonPressed = current_time
      self.RightMouseButtonDown = True
      #print('Left MB was released for %3.2fs'%self.TimeSinceLeftMouseButtonReleased)
      self.TimeRightMouseButtonReleased = -1000
      self.TimeSinceRightMouseButtonReleased = 1000
      self.RightMousePressPosition = event.pos


  def HandleMouseUpEvents(self, event):
    current_time = self.GetTimeinSeconds()
    if (event.button == 1):
      #logger.write('Button %d up'%event.button)
      # store time between mouse down and now
      self.TimeSinceLeftMouseButtonPressed = current_time - self.TimeLeftMouseButtonPressed
      self.LeftMouseReleasePosition = event.pos
      # was this time short enough to count as a click and not a click and hold?
      if (self.TimeSinceLeftMouseButtonPressed < self.singleClickTiming):
        # was there another click just before then do not register another click
        if (self.TimeSinceLeftMouseButtonDoubleClick > self.singleClickTiming):
          self.LeftMouseButtonClicked = True
          self.LeftMouseClickPosition = event.pos

      self.TimeLeftMouseButtonReleased = current_time
      self.LeftMouseButtonDown = False
      #print('Left MB was pressed for %3.2fs'%self.TimeSinceLeftMouseButtonPressed)
      self.TimeLeftMouseButtonPressed = -1000
      self.TimeSinceLeftMouseButtonPressed = 1000
    elif (event.button == 2):
      print('unhandled event for mouse button 2')
      print(event)
      logger.write('Unhandled Button %d up'%event.button)
    elif (event.button == 3):
      #logger.write('Button %d up'%event.button)
      # store time between mouse down and now
      self.TimeSinceRightMouseButtonPressed = current_time - self.TimeRightMouseButtonPressed
      self.RightMouseReleasePosition = event.pos
      # was this time short enough to count as a click and not a click and hold?
      if (self.TimeSinceRightMouseButtonPressed < self.singleClickTiming):
        # was there another click just before then do not register another click
        if (self.TimeSinceRightMouseButtonDoubleClick > self.singleClickTiming):
          self.RightMouseButtonClicked = True
          self.RightMouseClickPosition = event.pos

      self.TimeRightMouseButtonReleased = current_time
      self.RightMouseButtonDown = False
      #print('Right MB was pressed for %3.2fs'%self.TimeSinceRightMouseButtonPressed)
      self.TimeRightMouseButtonPressed = -1000
      self.TimeSinceRightMouseButtonPressed = 1000
    #print(event.pos)
    #print(event.button)
    #print(event.touch)
    pass


  def HandleMouseMotionEvents(self, event, game):
    #print(event.pos)
    #print(event.buttons)
    #print(event.touch)
    game.mousePos = event.pos
    exited_element = True
    if (game.currentScreen == 'System'):
      if (self.LeftMouseButtonDown):
        if (self.TimeSinceLeftMouseButtonPressed > 0.3):
          mousePosDelta2 = Utils.SubTuples(game.mousePos, self.LeftMousePressPosition)
          game.mouseDragged = mousePosDelta2
          game.systemScreen.screenCenter = Utils.AddTuples(game.systemScreen.screenCenterBeforeDrag, mousePosDelta2)
          game.systemScreen.reDraw = True
          #print(game.systemScreen.screenCenter,game.systemScreen.screenCenterBeforeDrag)
    if (not self.LeftMouseButtonDown):
      for clickable in self.clickables:
        if (clickable.rect) and (clickable.enabled):
          if (     (game.mousePos[0]  > clickable.rect[0])
               and (game.mousePos[0] <  clickable.rect[0]+clickable.rect[2])
               and (game.mousePos[1]  > clickable.rect[1])
               and (game.mousePos[1] <  clickable.rect[1]+clickable.rect[3]) ):
            clickable.mousepos = game.mousePos
            if (self.lastEnteredElement != clickable):
              if (self.lastEnteredElement != None):
                self.lastEnteredElement.hover = False
              if (EVENTS_DEBUG):
                print('entered %s'%clickable.name)
              self.lastEnteredElement = clickable
              self.timestampEnteredElement = self.GetTimeinSeconds()
              self.timeSinceEnteredElement = self.TimeDeltaInit
            exited_element = False
      if (exited_element):
        if (self.lastEnteredElement != None):
          if (EVENTS_DEBUG):
            print('exited %s'%self.lastEnteredElement.name)
          self.lastEnteredElement.hover = False
          self.lastEnteredElement = None
          self.timeSinceEnteredElement = self.TimeDeltaInit
          game.SetRedrawFlag(game.currentScreen)


  def HandleSingleClickEvents(self, button, game):
    clicked_clickable = -1
    self.LeftMouseButtonClicked = False
    self.RightMouseButtonClicked = False
    index = 0
    rightClickProcessed = False
    if (EVENTS_DEBUG):
      print(self.LeftMouseClickPosition)
    for clickable in self.clickables:
      if (clickable.rect) and (clickable.enabled):
        if (clickable.LeftClickCallBack is not None and button == 1):
          if (     (self.LeftMouseClickPosition[0]  > clickable.rect[0])
               and (self.LeftMouseClickPosition[0] <  clickable.rect[0]+clickable.rect[2])
               and (self.LeftMouseClickPosition[1]  > clickable.rect[1])
               and (self.LeftMouseClickPosition[1] <  clickable.rect[1]+clickable.rect[3]) ):
            clicked_clickable = index
            clickable.LeftClick()
            clickable.mousepos = self.LeftMouseClickPosition
            #print(clickable.name)
        elif (clickable.RightClickCallBack is not None and button == 3):
          if (     (self.LeftMouseClickPosition[0]  > clickable.rect[0])
               and (self.LeftMouseClickPosition[0] <  clickable.rect[0]+clickable.rect[2])
               and (self.LeftMouseClickPosition[1]  > clickable.rect[1])
               and (self.LeftMouseClickPosition[1] <  clickable.rect[1]+clickable.rect[3]) ):
            rightClickProcessed = True
            clicked_clickable = index
            clickable.RightClick()
            clickable.mousepos = self.RightMouseClickPosition
      index += 1
    if (button == 3 and rightClickProcessed == False):
      if (game.currentScreen == 'System'):
        game.systemScreen.CloseMenus()
      if (game.currentScreen == 'Bodies'):
        game.bodiesScreen.CloseMenus()


  def HandleDoubleClickEvents(self, button):
    self.LeftMouseButtonClicked = False
    self.RightMouseButtonClicked = False
    self.LeftMouseButtonDoubleClicked = False
    for clickable in self.clickables:
      if (clickable.rect) and (clickable.enabled) and (clickable.DoubleClickCallBack is not None):
        if (     (self.LeftMouseClickPosition[0]  > clickable.rect[0])
             and (self.LeftMouseClickPosition[0] <  clickable.rect[0]+clickable.rect[2])
             and (self.LeftMouseClickPosition[1]  > clickable.rect[1])
             and (self.LeftMouseClickPosition[1] <  clickable.rect[1]+clickable.rect[3]) ):
          #clickable.parameter = self.LeftMouseClickPosition
          #clickable.mousepos = self.LeftMouseClickPosition
          clickable.DoubleClick()
          
          #print(clickable.name)


  def HandleMouseWheelEvents(self, event, game):
    if (game.currentScreen == 'System'):
      screen = game.systemScreen
      # The button will be set to 4 when the wheel is rolled up, and to button 5 when the wheel is rolled down
      current_time = self.GetTimeinSeconds()
      if (screen.window_fleet_info_rect.collidepoint(event.pos)):
        # scrool the info window instead of zooming
        if (event.button == 4):
          if (screen.window_fleet_info_scoll_pos < 0):
            screen.window_fleet_info_scoll_pos+=1
        else:
          screen.window_fleet_info_scoll_pos-=1
        screen.reDraw_FleetInfoWindow = True
      elif (screen.window_info_rect.collidepoint(event.pos)):
        # scrool the info window instead of zooming
        if (event.button == 4):
          if (screen.window_info_scoll_pos < 0):
            screen.window_info_scoll_pos+=1
        else:
          screen.window_info_scoll_pos-=1
        screen.reDraw_InfoWindow = True
      else:
        if (event.button == 4):
          if (screen.systemScale < 1000000000):
            screen.systemScale *= 2
            delta = Utils.SubTuples(screen.screenCenter, event.pos)# game.cameraCenter)
            #zoomed_delta = Utils.MulTuples(delta, 2)
            screen.screenCenter=Utils.AddTuples(screen.screenCenter, delta)
            screen.reDraw = True
        else:
          if (screen.systemScale > 0.01):
            screen.systemScale /= 2
            delta = Utils.SubTuples(screen.screenCenter, event.pos)#, game.cameraCenter)
            zoomed_delta = Utils.DivTuples(delta, 2)
            screen.screenCenter=Utils.SubTuples(screen.screenCenter, zoomed_delta)
            screen.reDraw = True
    elif (game.currentScreen == 'Bodies'):
      screen = game.bodiesScreen
      dropdown_element = screen.GUI_Elements[screen.GUI_ID_dropdown_systems]
      if (dropdown_element.extendedBB):
        if (dropdown_element.extendedBB.collidepoint(event.pos)):
          if (dropdown_element.open):
            if (event.button == 4):
              if (dropdown_element.scroll_position < 0):
                dropdown_element.scroll_position += 1
            else:
              if (dropdown_element.scroll_position > dropdown_element.maxScroll):
                dropdown_element.scroll_position -= 1
            screen.reDraw_GUI = True
        else:
          dropdown_element = screen.GUI_Elements[screen.GUI_ID_dropdown_designations]
          if (dropdown_element.extendedBB.collidepoint(event.pos)):
            if (dropdown_element.open):
              if (event.button == 4):
                if (dropdown_element.scroll_position < 0):
                  dropdown_element.scroll_position += 1
              else:
                if (dropdown_element.scroll_position > dropdown_element.maxScroll):
                  dropdown_element.scroll_position -= 1
              screen.reDraw_GUI = True
          else:
            scrollable_element = screen.table
            if (scrollable_element.rect.collidepoint(event.pos)):
              if (event.button == 4):
                if (scrollable_element.scroll_position < 0):
                  scrollable_element.scroll_position += 1
              else:
                if (scrollable_element.scroll_position > scrollable_element.maxScroll):
                  scrollable_element.scroll_position -= 1
              screen.reDraw = True
    elif (game.currentScreen == 'Fleets'):
      screen = game.fleetScreen
      #dropdown_element = game.fleetScreen.GUI_Elements[game.fleetScreen.GUI_ID_dropdown]
      #if (dropdown_element.extendedBB):
      #  if (dropdown_element.extendedBB.collidepoint(event.pos)):
      #    if (dropdown_element.open):
      #      if (event.button == 4):
      #        if (dropdown_element.scroll_position < 0):
      #          dropdown_element.scroll_position += 1
      #      else:
      #        if (dropdown_element.scroll_position > dropdown_element.maxScroll):
      #          dropdown_element.scroll_position -= 1
      #      game.bodiesScreen.reDraw_GUI = True
      #  else:
      #    dropdown_element = game.bodiesScreen.GUI_Elements[game.bodiesScreen.GUI_ID_dropdown_designations]
      #    if (dropdown_element.extendedBB.collidepoint(event.pos)):
      #      if (dropdown_element.open):
      #        if (event.button == 4):
      #          if (dropdown_element.scroll_position < 0):
      #            dropdown_element.scroll_position += 1
      #        else:
      #          if (dropdown_element.scroll_position > dropdown_element.maxScroll):
      #            dropdown_element.scroll_position -= 1
      #        game.bodiesScreen.reDraw_GUI = True
      #    else:

      scrollable_element = screen.table
      if (scrollable_element.rect.collidepoint(event.pos)):
        if (event.button == 4):
          if (scrollable_element.scroll_position < 0):
            scrollable_element.scroll_position += 1
        else:
          if (scrollable_element.scroll_position > scrollable_element.maxScroll):
            scrollable_element.scroll_position -= 1
        screen.reDraw = True
        screen.UpdateTable()


  def ProcessClickablesEvents(self, game):
    for clickable in self.clickables:
      if (clickable.toBeProcessed):
        #if (not clickable.doubleClicked):
        clickable.Process()
          