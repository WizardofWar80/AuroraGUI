import Table
import pygame
import Utils
import Events
import GUI
from Screen import Screen
from operator import itemgetter
import Utils
import TableScreen
from TableScreen import TableScreen
import Fleets


class FleetScreen(TableScreen):
  pass

  def UpdateTable(self):
    game = self.game
    t1 = pygame.time.get_ticks()
    self.table.Clear()

    text_widths = []
    unsortedIDs = []
    #self.table.max_cell_sizes = []
    index = 1
    systems = {}
    for systemID in game.fleets:
      systemFleets = game.fleets[systemID]
      for fleetID in systemFleets:
        fleet = systemFleets[fleetID]
        if (self.GetDrawConditions(fleet)):
          fleetType = ''
          if (fleet['Harvesters'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'H'
          if (fleet['Terraformers'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'TF'
          if (fleet['Tanker'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'T'
          if (fleet['Refueling Hub'] > 0):
            fleetType += '/' if len(fleetType) > 0 else ''
            fleetType += 'FH'
          unsortedIDs.append([fleet['Name'], fleet['System_Name'], fleet['Admin'], '',fleet['Station'], fleetType])

    index+=1

    id, rev = self.GetTableSortState()
    sortedIDs = sorted(unsortedIDs, key=itemgetter(id), reverse=rev)
    
    row = 0
    header = ['Name', 'System', 'Admin', 'Orders', 'Station', 'Fleet Type']
    
    self.table.AddRow(row, header, [True]*len(header))

    row = 1
    sortedRowIndex = 0
    self.table.maxScroll = min(0,self.table.max_rows-len(sortedIDs)-1)
    self.table.num_rows = 1

    for row_sorted in sortedIDs:
      if (sortedRowIndex + self.table.scroll_position >= 0) and (row < self.table.max_rows):
        #printed_row = [int(Utils.Round(row_sorted[0],0)) if (row_sorted[0]>= 10) else Utils.Round(row_sorted[0],1),# AU
        #               row_sorted[1], # Name
        #               row_sorted[2], # System
        #               row_sorted[3], # Cost
        #               row_sorted[4]  # Terraforming
        #               ]

        self.table.AddRow(row, row_sorted)
        row += 1
        if (row >= self.table.max_rows):
          break
      sortedRowIndex += 1

    self.table.scrollbar.Update(total_range = len(sortedIDs), current_position = -self.table.scroll_position)
    self.table.Realign()

    if (self.GUI_Elements == {}):
      self.InitGUI()
    else:
      self.UpdateGUI()
    #self.reDraw = True
    t2 = pygame.time.get_ticks()
    deltaTime = t2- t1
    print('UpdateTable ',deltaTime)


    def GetDrawConditions(self, fleet, void = None):
      return True