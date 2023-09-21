import time
import pygame
import logger as lg

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
    
  def Update(self):
    current_time = self.GetTimeinSeconds()
    if (self.TimeLeftMouseButtonReleased > self.TimestampInit):
      self.TimeSinceLeftMouseButtonReleased = current_time - self.TimeLeftMouseButtonReleased
    if (self.TimeLeftMouseButtonPressed > self.TimestampInit):
      self.TimeSinceLeftMouseButtonPressed = current_time - self.TimeLeftMouseButtonPressed
    if (self.TimeLeftMouseButtonDoubleClick > self.TimestampInit):
      self.TimeSinceLeftMouseButtonDoubleClick = current_time - self.TimeLeftMouseButtonDoubleClick

  def Bind(self, clickable):
    self.clickables.append(clickable)

  def GetTimeinSeconds(self):
    return pygame.time.get_ticks()/1000

  def HandleMouseEvents(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
      self.HandleMouseDownEvents(event)
    if event.type == pygame.MOUSEBUTTONUP:
      self.HandleMouseUpEvents(event)
    if event.type == pygame.MOUSEMOTION:
      self.HandleMouseMotionEvents(event)
    if (self.LeftMouseButtonClicked):
      self.HandleSingleClickEvents()
    if (self.LeftMouseButtonDoubleClicked):
      self.HandleDoubleClickEvents()


  def HandleMouseDownEvents(self, event):
    current_time = self.GetTimeinSeconds()
    if (event.button == 1):
      logger.write('Button %d down at: %d,%d'%(event.button,event.pos[0], event.pos[1]))
      #print('LMB')
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
    #print(event.pos)
    #print(event.button)
    #print(event.touch)


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
      print('unhandled event for mouse button 2')
      print(event)
      logger.write('Unhandled Button %d up'%event.button)
    #print(event.pos)
    #print(event.button)
    #print(event.touch)
    pass

  def HandleMouseMotionEvents(self, event):
    #print(event.pos)
    #print(event.buttons)
    #print(event.touch)
    pass

  def HandleSingleClickEvents(self):
    clicked_clickable = -1
    clicked_group = -1
    self.LeftMouseButtonClicked = False
    index = 0
    for clickable in self.clickables:
      if (clickable.rect) and (clickable.enabled):
        if (     (self.LeftMouseClickPosition[0]  > clickable.rect[0])
             and (self.LeftMouseClickPosition[0] <  clickable.rect[0]+clickable.rect[2])
             and (self.LeftMouseClickPosition[1]  > clickable.rect[1])
             and (self.LeftMouseClickPosition[1] <  clickable.rect[1]+clickable.rect[3]) ):
          clicked_clickable = index
          clicked_group = clickable.group
          clickable.clickedAt = self.LeftMouseClickPosition
          clickable.Press()
      index += 1
      # if a clickable item was clicked and it is part of a group, look for all other items in the group and unpress them
      if (clickable.radiobutton == True):
        if (clicked_group > -1) and (clicked_clickable > -1):
          index = 0
          for clickable in self.clickables:
            if (clicked_group == clickable.group) and (index != clicked_clickable):
              clickable.pressed = False
            index += 1

  def HandleDoubleClickEvents(self):
    self.LeftMouseButtonClicked = False
    self.LeftMouseButtonDoubleClicked = False
    for clickable in self.clickables:
      if (clickable.rect) and (clickable.enabled):
        if (     (self.LeftMouseClickPosition[0]  > clickable.rect[0])
             and (self.LeftMouseClickPosition[0] <  clickable.rect[0]+clickable.rect[2])
             and (self.LeftMouseClickPosition[1]  > clickable.rect[1])
             and (self.LeftMouseClickPosition[1] <  clickable.rect[1]+clickable.rect[3]) ):
          clickable.DoubleClick()