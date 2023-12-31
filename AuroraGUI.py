import pygame
import time
import os
from datetime import datetime
import logger as lg
from _thread import *
import logger as lg
import Events as Ev
import Utils
#import Button as Btn
import MainModule

EDITOR_ENABLED = True

screen_width  = 1850
screen_height = 1000

logger = lg.Logger(logfile= 'log.txt', module='AuroraGUI.py', log_level = 1)
img_path = "Images"
lastTimestamp = pygame.time.get_ticks()
lastTimestampOptions = pygame.time.get_ticks()

def CheckReDrawFramerate():
  return True


def CheckReFreshRate():
  global lastTimestamp
  currentTimestamp = pygame.time.get_ticks()
  if (currentTimestamp - lastTimestamp > 1000):
    lastTimestamp = currentTimestamp
    return True
  else:
    return False


def CheckOptionsSaveRate():
  global lastTimestampOptions
  currentTimestamp = pygame.time.get_ticks()
  if (currentTimestamp - lastTimestampOptions > 5000):
    lastTimestampOptions = currentTimestamp
    return True
  else:
    return False


def main():
  # initialize the pygame module
  pygameinstance = pygame.init()
  myEvents = Ev.Events()

  file_list = []
  for (dirpath, dirs, files) in os.walk(img_path):
    for filename in files:
      index_slash = dirpath.rfind('\\')
      if (index_slash > -1):
        subfolder = dirpath[index_slash+1:]
      else:
        subfolder = 'Sol'
      file_list.append([subfolder, filename, os.path.join(dirpath, filename).lower()])


  game = MainModule.Game(myEvents, file_list)

  # define a variable to control the main loop
  running = True
  # main loop
  while running:
    # event handling, gets all event from the event queue
    myEvents.Update(game)
    for event in pygame.event.get():
      #myEvents.Update()
      myEvents.HandleMouseEvents(event, game)
      myEvents.HandleKeyboardEvents(event, game)
      myEvents.ProcessClickablesEvents(game)
      # only do something if the event is of type QUIT
      if event.type == pygame.QUIT:
        running = False


    if CheckReFreshRate():
      game.CheckForNewDBData()

    if CheckReDrawFramerate():
      game.Draw()
      
      # push the data to the display for displaying
      pygame.display.flip()

    game.MusicTick()

    if (CheckOptionsSaveRate()):
      game.SaveOptions()


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
  # call the main function
  main()

