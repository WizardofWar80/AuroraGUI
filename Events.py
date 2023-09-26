import time
import pygame
import logger as lg
import Utils

logger = lg.Logger(logfile= 'log_events.txt', module='Events.py', log_level = 1)
logger.Reset()

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
    self.doubleClickTiming = 0.5
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
    
  def Update(self):
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


  def ClearClickables(self):
    self.clickables = []

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
      self.HandleSingleClickEvents(1)
    #if (self.LeftMouseButtonDoubleClicked):
    #  self.HandleDoubleClickEvents(1)


  def HandleKeyboardEvents(self, event, game):
    if (event.type == pygame.KEYDOWN):
      if (event.key == pygame.K_HOME):
        if (game.screenCenter != game.cameraCenter):
          game.screenCenter = game.cameraCenter
        else:
          game.systemScale = game.systemScaleStart
        game.reDraw = True


  def HandleMouseDownEvents(self, event,game):
    current_time = self.GetTimeinSeconds()
    if (event.button == 1):
      logger.write('Button %d down at: %d,%d'%(event.button,event.pos[0], event.pos[1]))
      #print('LMB')
      if(not self.LeftMouseButtonDown):
        game.screenCenterBeforeDrag = game.screenCenter
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
      print('unhandled event for mouse button 2')
      print(event)
      logger.write('Unhandled Button %d down'%event.button)


  def HandleMouseUpEvents(self, event):
    current_time = self.GetTimeinSeconds()
    if (event.button == 1):
      logger.write('Button %d up'%event.button)
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
      logger.write('Button %d up'%event.button)
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
    if (self.LeftMouseButtonDown):
      if (self.TimeSinceLeftMouseButtonPressed > 0.3):
        mousePosDelta2 = Utils.SubTuples(game.mousePos, self.LeftMousePressPosition)
        game.mouseDragged = mousePosDelta2
        game.screenCenter = Utils.AddTuples(game.screenCenterBeforeDrag, mousePosDelta2)
        game.reDraw = True


  def HandleSingleClickEvents(self, button):
    clicked_clickable = -1
    self.LeftMouseButtonClicked = False
    self.RightMouseButtonClicked = False
    index = 0
    for clickable in self.clickables:
      if (clickable.rect) and (clickable.enabled):
        if (clickable.LeftClickCallBack is not None and button == 1):
          if (     (self.LeftMouseClickPosition[0]  > clickable.rect[0])
               and (self.LeftMouseClickPosition[0] <  clickable.rect[0]+clickable.rect[2])
               and (self.LeftMouseClickPosition[1]  > clickable.rect[1])
               and (self.LeftMouseClickPosition[1] <  clickable.rect[1]+clickable.rect[3]) ):
            clicked_clickable = index
            clickable.LeftClick()
        elif (clickable.RightClickCallBack is not None and button == 3):
          if (     (self.LeftMouseClickPosition[0]  > clickable.rect[0])
               and (self.LeftMouseClickPosition[0] <  clickable.rect[0]+clickable.rect[2])
               and (self.LeftMouseClickPosition[1]  > clickable.rect[1])
               and (self.LeftMouseClickPosition[1] <  clickable.rect[1]+clickable.rect[3]) ):
            clicked_clickable = index
            clickable.RightClick()
      index += 1


  def HandleDoubleClickEvents(self):
    self.LeftMouseButtonClicked = False
    self.RightMouseButtonClicked = False
    self.LeftMouseButtonDoubleClicked = False
    for clickable in self.clickables:
      if (clickable.rect) and (clickable.enabled) and (clickable.DoubleClickCallBack is not None):
        if (     (self.LeftMouseClickPosition[0]  > clickable.rect[0])
             and (self.LeftMouseClickPosition[0] <  clickable.rect[0]+clickable.rect[2])
             and (self.LeftMouseClickPosition[1]  > clickable.rect[1])
             and (self.LeftMouseClickPosition[1] <  clickable.rect[1]+clickable.rect[3]) ):
          clickable.DoubleClick()

  def HandleMouseWheelEvents(self, event, game):
    # The button will be set to 4 when the wheel is rolled up, and to button 5 when the wheel is rolled down
    current_time = self.GetTimeinSeconds()
    if (game.window_info_rect.collidepoint(event.pos)):
      # scrool the info window instead of zooming
      if (event.button == 4):
        if (game.window_info_scoll_pos < 0):
          game.window_info_scoll_pos+=1
      else:
        game.window_info_scoll_pos-=1
      game.reDraw_InfoWindow = True
    else:
      if (event.button == 4):
        if (game.systemScale < 1000000000):
          game.systemScale *= 2
          delta = Utils.SubTuples(game.screenCenter, event.pos)# game.cameraCenter)
          #zoomed_delta = Utils.MulTuples(delta, 2)
          game.screenCenter=Utils.AddTuples(game.screenCenter, delta)
          game.reDraw = True
      else:
        if (game.systemScale > 0.01):
          game.systemScale /= 2
          delta = Utils.SubTuples(game.screenCenter, event.pos)#, game.cameraCenter)
          zoomed_delta = Utils.DivTuples(delta, 2)
          game.screenCenter=Utils.SubTuples(game.screenCenter, zoomed_delta)
          game.reDraw = True


  def ProcessClickablesEvents(self, game):
    for clickable in self.clickables:
      if (clickable.toBeProcessed):
        if (not clickable.doubleClicked):
          clickable.Process()
          