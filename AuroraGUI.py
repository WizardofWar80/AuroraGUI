import pygame
import time
import os
from datetime import datetime
import logger as lg
from _thread import *
import logger as lg
import Events as Ev
import Utils
import Button as Btn
import MainModule

EDITOR_ENABLED = True

screen_width  = 1850
screen_height = 1000

logger = lg.Logger(logfile= 'log.txt', module='AuroraGUI.py', log_level = 1)

def CheckReDrawFramerate():
  return True

def main():
  # initialize the pygame module
  pygameinstance = pygame.init()
  myEvents = Ev.Events()

  game = MainModule.Game()
  
  # define a variable to control the main loop
  running = True
  # main loop
  while running:
    # event handling, gets all event from the event queue
    for event in pygame.event.get():
      myEvents.Update()
      myEvents.HandleMouseEvents(event)
      # only do something if the event is of type QUIT
      if event.type == pygame.QUIT:
        # change the value to False, to exit the main loop
        running = False
    #ProcessClickablesEvents(myEvents, plot, ac)

    #recalc = False
    if CheckReDrawFramerate():
    #  data.SetCurrentPricing()
      game.Draw()
      
      # push the data to the display for displaying
      pygame.display.flip()


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
  # call the main function
  main()

