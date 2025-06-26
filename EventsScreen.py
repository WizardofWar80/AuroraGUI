import Table
import pygame
import Utils
import Events
import Clickable
import GUI
from Screen import Screen
from operator import itemgetter


class EventsScreen(Screen):
  #self.clickedEvent = {}

  def Draw(self):
    reblit = False
    # clear screen
    if (self.reDraw):
      #if (self.Events):
      #  self.Events.ClearClickables()
      self.reDraw_GUI = True
      self.surface.fill(self.bg_color)
      reblit |= self.DrawGameEvents()

    reblit |= self.DrawGUI()

    if (reblit):
      #self.DebugDrawClickables()
      self.screen.blit(self.surface,(0,0))

    self.reDraw = False
    
    return reblit


  def DrawGameEvents(self):
    game_event_table = [list(x) for x in self.game.db.execute('''SELECT * from FCT_Gamelog WHERE Time > %d 
   AND GameID = %d AND RaceID = %d;'''%(int(self.game.lastGameTime), self.game.gameID,self.game.myRaceID))]
    #IncrementID	GameID	RaceID	SMOnly	Time	EventType	MessageText SystemID	Xcor	Ycor	IDType	PopulationID
    lineNr = 0
    line_height = 20
    for game_event in game_event_table:
      cursorPos = (50,(100+lineNr*line_height))
      line = game_event[6]
      texts, links, links_to = self.DeconstructEventMessage(game_event[5], line)
      link_index = 0
      if (game_event[8]== game_event[9]):
        game_event[8] = game_event[9] = 0
      parameters = [game_event[7], game_event[8], game_event[9], game_event[10], game_event[11]]
      printed = False
      for i in range(len(texts)):
        if (links[i]):
          cursorPos, label_size = Utils.DrawText2Surface(self.surface, texts[i], cursorPos, 15, Utils.DODGER_BLUE)
          if (cursorPos == None):
            break
          pygame.draw.line(self.surface, Utils.DODGER_BLUE, (cursorPos[0],cursorPos[1]+15), (cursorPos[0]+label_size[0],cursorPos[1]+15))
          #print(texts[i]+' - '+ links_to[link_index])
          bb = (cursorPos,label_size)
          gui_cl = self.game.MakeClickable(links_to[link_index], bb, self.game.FollowEvent, par=[texts[i]]+parameters, parent=links_to[link_index])
          link_index += 1
          #['Ship', 'Body', 'Fleet','Missile', 'Contact','Research', 'Xenos', 'System']
          printed = True
        else:
          cursorPos, label_size = Utils.DrawText2Surface(self.surface, texts[i], cursorPos, 15, (255,255,255))
          if (cursorPos == None):
            break
          printed = True
        
        cursorPos = (cursorPos[0]+label_size[0], cursorPos[1])
      if (printed):
        lineNr += 1
    return True


  def DeconstructEventMessage(self, id, text):
    results = []
    links = []
    links_to = []
    if (id == 1):
      #1	Production of TS Tycho Brahe completed at Earth
      results, links = self.SplitData(text, searchTokens = ['Production of ', ' completed at '])
      links_to = ['Ship', 'Body']
      pass
    elif (id == 2):
      #2	#Tycho Brahe 042 constructed at Earth and assigned to Space Station
      results, links = self.SplitData(text, searchTokens = [' constructed at ', ' and assigned to '])
      links_to = ['Ship', 'Body', 'Fleet']
      pass
    elif (id == 3):
      #3	Napoleon Mk.2 001 repaired at Earth
      results, links = self.SplitData(text, searchTokens = [' repaired at '])
      links_to = ['Ship', 'Body',]
      pass
    elif (id == 4):
      #4	Bavaria 004 refitted to Bavaria Mk.2 class at Earth. 10 additional crew required, changing grade points to 100
      results, links = self.SplitData(text, searchTokens = [' refitted to ', ' at ', '. '])
      links_to = ['Ship', 'Body']
      links[2] = False
      links[-1] = False
      pass
    elif (id == 10):
      #10	Wimpie Trichardt escaped to a lifepod before the destruction of Mantis Shrimp Mk.2 001
      results, links = self.SplitData(text, searchTokens = [' escaped to a lifepod before the destruction of '])
      links_to = ['Ship']
      links[0] = False
      pass
    elif (id == 15):
      #15	ODB-01 Allosaurus 001 has launched 45x Khristina Tiyahahu Anti-Ship Missile from Size 5 Missile Launcher (60.0% Reduction) targeted on XX Pachaug Victory 001.   Range 41,196,979 km   Estimated Chance to Hit 375%
      results, links = self.SplitData(text, searchTokens = [' has launched ', ' targeted on ' , '. '])
      links_to = ['Ship', 'Missile', 'Contact']
      links[-1] = False
      pass
    elif (id == 27):
      #27	SO-09 Mantis Shrimp Mk.2 001 has suffered a catastrophic failure and exploded!
      results, links = self.SplitData(text, searchTokens = [' has suffered a catastrophic failure and exploded!'])
      links_to = ['Ship']
      pass
    elif (id == 28):
      #28	SO-09 Mantis Shrimp Mk.2 001 Damage Report:   Ship Destroyed
      tokens = [' Damage Report:   Ship Destroyed']
      if (self.CheckTokensInText(text, tokens)):
        results, links = self.SplitData(text, searchTokens = tokens)
        links_to = ['Ship']
        links[1] = False
        links[-1] = False
      else:
        tokens = ['A ', ' on ', ' has ']
        if (self.CheckTokensInText(text, tokens)):
          results, links = self.SplitData(text, searchTokens = tokens)
          links_to = ['Ship']
          links[1] = False
          links[-1] = False
      ##28	A 10cm Railgun V10/C1 on PDC-12 Napoleon Mk.2 004 (PDC Alpha Centauri) has been damaged due to a maintenance failure. Insufficient maintenance supplies were available to effect an immediate repair. The ship has 1 maintenance supplies remaining. Current Maintenance Clock: 11,86 years
      pass
    elif (id == 42):
      #42	FT-06 Berlin 006 cannot cycle order LP1  (Earth): Intra-system Jump to LP2  (Jupiter) as it does not start in the same system as the last current order ends. The cycle orders request has been removed
      #42	FT-32 Dresden 009 has cycle orders set but only has one order set up. As this can lead to an endless loop the cycle orders request has been removed
      tokens = [' cannot cycle order ']
      if (self.CheckTokensInText(text, tokens)):
        results, links = self.SplitData(text, searchTokens = tokens)
        links_to = ['Ship']
        links[-1] = False
      else:
        tokens = [' has cycle orders ']
        if (self.CheckTokensInText(text, tokens)):
          results, links = self.SplitData(text, searchTokens = tokens)
          links_to = ['Ship']
          links[-1] = False
    elif (id == 45):
      #45	FT EE 01 has completed orders. Orbiting Epsilon Eridani II
      #45 'FT-01 Allosaurus 001 has completed orders. 305m km from Ceres at bearing 162°'
      tokens = [' has completed orders.', ' Orbiting ']
      if (self.CheckTokensInText(text, tokens)):
        results, links = self.SplitData(text, searchTokens = tokens)
        links_to = ['Ship', 'Body']
      else:
        tokens = [' has completed orders.', ' km from ', ' at bearing ']
        if (self.CheckTokensInText(text, tokens)):
          results, links = self.SplitData(text, searchTokens = tokens)
          links_to = ['Ship', 'Body']
          links[2] = False
          links[-1] = False
      pass
    elif (id == 46):
      #46	Dresden 009 has insufficient fuel to complete the orders of its parent fleet
      results, links = self.SplitData(text, searchTokens = [' has insufficient fuel '])
      links_to = ['Ship']
      links[-1] = False
      pass
    elif (id == 54):
      #54	GSC-01 Karl Schwarzschild  001 cannot carry out a transit as there is no available jump drive capable of allowing the fleet's military-engined ships to enter the jump point
      results, links = self.SplitData(text, searchTokens = [' cannot carry out '])
      links_to = ['Ship']
      links[-1] = False
      pass
    elif (id == 60):
      #60	A science team led by Nogushi Fumie working on Earth has completed research into Compact Electronic Counter-countermeasures - 1
      tokens = [' working on ', ' has completed ', ' into ']
      if (self.CheckTokensInText(text, tokens)):
        results, links = self.SplitData(text, searchTokens = tokens)
        links_to = ['Body', 'Research']
        links[0] = False
        links[-1] = False
      else:
        #A Prototype of Procaccini-Harrigill Aeromarine EP013 Commercial Conventional Engine has been created
        tokens = ['A Prototype of ', ' has been created']
        if (self.CheckTokensInText(text, tokens)):
          results, links = self.SplitData(text, searchTokens = tokens)
          links_to = ['Research']
          #links[0] = False
          #links[-1] = False
    elif (id == 63):
      #63	1 inactive research facilities on Earth
      results, links = self.SplitData(text, searchTokens = [' inactive research facilities on '])
      links_to = ['Body']
      links[0] = False
      pass
    elif (id == 64):
      #64	Shortage of Sorium in fuel production at 36 Ophiuchi-A II
      results, links = self.SplitData(text, searchTokens = [' in fuel production at '])
      links_to = ['Body']
      links[0] = False
      pass
    elif (id == 66):
      #66	Deposits of Vendarite have been exhausted on Earth
      results, links = self.SplitData(text, searchTokens = [' exhausted on '])
      links_to = ['Body']
      links[0] = False
      pass
    elif (id == 71):
      #71	FT-32 Dresden 009 cannot complete its current order due to a fuel shortage
      results, links = self.SplitData(text, searchTokens = [' cannot complete its current order due to a fuel shortage'])
      links_to = ['Ship']
      pass
    elif (id == 76):
      #76	All traces of Methane have been removed from the atmosphere of Pi Ophiuchi II
      results, links = self.SplitData(text, searchTokens = ['All traces of ', ' have been removed from the atmosphere of '])
      links_to = ['Body']
      links[1] = False
      pass
    elif (id == 77):
      #77	Addition of Nitrogen to the atmosphere of Mars has reached the required level
      results, links = self.SplitData(text, searchTokens = ['Addition of ', ' to the atmosphere of ', ' has reached the required level'])
      links_to = ['Body']
      links[1] = False
      pass
    elif (id == 80):
      #80	Fuel storage for harvester Antlion Mk.1 010 is more than 90% full
      results, links = self.SplitData(text, searchTokens = ['Fuel storage for harvester ', ' is more than '])
      links_to = ['Ship']
      links[-1] = False
      pass
    elif (id == 83):
      #83	FT-06 Berlin 006 was unable to load Automated Mine from Epsilon Eridani II
      results, links = self.SplitData(text, searchTokens = [' was unable to load ', ' from '])
      links[2] = False
      links_to = ['Ship', 'Body']
      pass
    elif (id == 88):
      #88	A science team led by Nogushi Fumie on Earth has begun research into Compact Electronic Countermeasures - 1
      results, links = self.SplitData(text, searchTokens = ['A science team led by ', ' on ',' has begun ', ' into '])
      links[1] = False
      links[-1] = False
      links_to = ['Body', 'Research']
      pass
    elif (id == 90):
      #90	Romona Huhtala promoted to Captain
      pass
    elif (id == 98):
      #98	Ishani Acharya   Crew Training 10%    Reaction 5%    Tactical 15%    Production 5%    Communications 5%    Fighter Combat 30%  
      pass
    elif (id == 99):
      # Scientist Fabian Dahlberg has developed a severe medical problem that has forced him to retire. Assignment prior to retirement: Unassigned
      results, links = self.SplitData(text, searchTokens = [' has developed a severe medical problem that has forced him to retire. Assignment prior to retirement: '])
      if (results[-1].find('Unassigned') > -1):
        results = []
        links = []
      else:
        links_to = []
        links[0] = False
        links[2] = False
      pass
    elif (id == 122):
      #122	PDC-09 Napoleon Mk.2 001 has completed her overhaul
      results, links = self.SplitData(text, searchTokens = [' has completed her overhaul'])
      links_to = ['Ship']
      pass
    elif (id == 125):
      tokens = ['Slipway added to ', ' at ']
      if (self.CheckTokensInText(text, tokens)):
        #125	Slipway added to CSY Shenkle Shipbuilding at Earth
        results, links = self.SplitData(text, searchTokens = tokens)
        links_to = ['Body']
        links[1] = False
      else:
        tokens = ['The continual capacity task for ', ' at ',' has reached its target capacity']
        if (self.CheckTokensInText(text, tokens)):
          #125	The continual capacity task for Zillmer Gulf Shipyards Company at Earth has reached its target capacity
          results, links = self.SplitData(text, searchTokens = tokens)
          links_to = ['Body']
          links[1] = False
        else:
          #'Retooling for Allosaurus Mk.2 class completed at CSY Shenkle Shipbuilding at Earth'
          tokens = ['Retooling for ' , 'completed at ', ' at ']
          if (self.CheckTokensInText(text, tokens)):
            results, links = self.SplitData(text, searchTokens = tokens)
            links_to = ['Body']
            links[1] = False
            links[3] = False
    elif (id == 129):
      #129	Commodore Alexandra Bentley assigned as commander of Fuel Logistics Command
      pass
    elif (id == 133):
      #133	Burnam Freight Services has launched a new Burnam Large F6 class Freighter
      pass
    elif (id == 141):
      #141	GEV-01 Proxima Centauri 001 under the command of CDR Santos Larrivee discovered minerals on Tarvos:   Mercassium: 25  Acc 1  
      tokens = [' under the command of ', ' discovered minerals on ',': ']
      if (self.CheckTokensInText(text, tokens)):
        results, links = self.SplitData(text, searchTokens = tokens)
        links_to = ['Ship', 'Body']
        links[2] = False
        links[-1] = False
      else:
        #141	GEV-01 Proxima Centauri 001 discovered minerals on Tarvos:   Mercassium: 25  Acc 1  
        tokens = [' discovered minerals on ',': ']
        if (self.CheckTokensInText(text, tokens)):
          results, links = self.SplitData(text, searchTokens = tokens)
          links_to = ['Ship', 'Body']
          links[-1] = False
      pass
    elif (id == 146):
      #146	A 10cm Railgun V10/C1 on PDC-17 Napoleon Mk.2 009 (PDC Alpha Centauri) has suffered a maintenance failure. Repairs have been carried out that required 1.7 maintenance supplies. The ship has 144 maintenance supplies remaining. Maintenance Clock: 5.61 years. Average Class Maintenance Life: 9.06 years. Current Deployment: 0%
      results, links = self.SplitData(text, searchTokens = ['A ', ' on ', ' has suffered '])
      links_to=['Ship']
      links[1] = False
      links[0] = False
      links[5] = False
      links[-1] = False
      pass
    elif (id == 181):
      #181	New Hostile Ship contact:  [RAM]  XX Pachaug Victory 001   Thermal C64   899 km/s
      results, links = self.SplitData(text, searchTokens = ['New Hostile Ship contact:', ' Thermal '])   
      links_to = ['Contact']
      links[-1] = False
      pass
    elif (id == 182):
      #182	New Neutral Ship contact:  [ALP]  XX AbbÃ© GrÃ©goire 001   AS #1: GPS 19,089   0 km/s
      results, links = self.SplitData(text, searchTokens = ['New Neutral Ship contact:', ' AS '])   
      links_to = ['Contact']
      links[-1] = False
      pass
    elif (id == 195):
      #195	GSC-01 Karl Schwarzschild  001 under the command of LCDR Aaron Lowe has discovered the new system of Epsilon Indi
      tokens = [' under the command of ', ' has discovered the new system of ']
      if (self.CheckTokensInText(text, tokens)):
        results, links = self.SplitData(text, searchTokens = [' under the command of ', ' has discovered the new system of '])   
        links_to = ['Ship', 'System']
        links[2] = False
      else:
        #195	GSC-01 Karl Schwarzschild  001 has discovered the new system of Epsilon Indi
        tokens = [' has discovered the new system of ']
        if (self.CheckTokensInText(text, tokens)):
          results, links = self.SplitData(text, searchTokens = [' under the command of ', ' has discovered the new system of '])   
          links_to = ['Ship', 'System']
      pass
    elif (id == 201):
      #201	As a result of repairs to Napoleon Mk.2 001, her maintenance clock has been reduced by 0.29 years
      results, links = self.SplitData(text, searchTokens = ['As a result of repairs to ', ', her '])   
      links_to = ['Ship']
      links[-1] = False
      pass
    elif (id == 206):
      #206	Updated Hostile Ship contact:  [RAM]  XX Pachaug Victory 001  3,558 tons   Thermal C64   899 km/s
      results, links = self.SplitData(text, searchTokens = ['Updated Hostile Ship contact:', ' tons '])   
      links_to = ['Contact']
      links[-1] = False
      pass
    elif (id == 207):
      #207	Contact re-established with Neutral Ship contact:  [ALP]  XX AbbÃ© GrÃ©goire 001   AS #1: GPS 19,089   0 km/s
      results, links = self.SplitData(text, searchTokens = ['Contact re-established with Neutral Ship contact:', ' AS '])   
      links_to = ['Contact']
      links[-1] = False
      pass
    elif (id == 211):
      #211	Boyle Mines Corporation on Halleys Comet has been expanded to 17  mining complexes
      results, links = self.SplitData(text, searchTokens = [' on ', ' has been expanded '])
      links_to = ['Body']
      links[0] = False
      links[-1] = False
      pass
    elif (id == 212):
      #212	A new shipping line has been established:  Andersson Transport Limited
      pass
    elif (id == 232):
      #232	A new alien ship class of the Rameswaram Aliens #406 has been detected in Rameswaram
      results, links = self.SplitData(text, searchTokens = ['A new alien ship class of the ', ' has been detected in '])   
      links_to = ['Xenos', 'System']
      pass
    elif (id == 233):
      #233	A new alien ship of the Pachaug Victory class from the Rameswaram Aliens #406 has been detected in Rameswaram
      results, links = self.SplitData(text, searchTokens = ['A new alien ship of the ',' from the ', ' has been detected in '])
      links_to = ['Xenos', 'System']
      links[1] = False
      pass
    elif (id == 253):
      #253	The crew of PDC-01 Napoleon 001 has completed shore leave and is fully rested
      results, links = self.SplitData(text, searchTokens = ['The crew of ',' has completed shore leave and is fully rested'])   
      links_to = ['Ship']
      pass
    elif (id == 256):
      #256	Riana Prinsloo   Colony Administration 6    Production 10%    Mining 10%    Population Growth 15%    Terraforming 5%  
      results = ['New administrator: '+text]
      links_to = []
      links = [False]
    elif (id == 257):
      #257	Rocky Lackner   Research Admin 15    Research 10%     Biology / Genetics
      results = ['New scientist: '+text]
      links_to = []
      links = [False]
    elif (id == 280):
      #280	The Mining bonus of LCDR Bret Crittendon has increased to 15%    Current Bonuses:  Crew Training 10%    Engineering 5%    Mining 15%     Current Assignment:  Unassigned
      results, links = self.SplitData(text, searchTokens = ['Current Bonuses:','Current Assignment:'])
      if (results[-1].find('Unassigned') > -1):
        results = []
        links = []
      else:
        links_to = []
        links[0] = False
      pass
    elif (id == 284):
      #284	Due to changes in climate, the dominant terrain on Pi Ophiuchi II has changed from Barren to Ice Fields
      results, links = self.SplitData(text, searchTokens = ['Due to changes in climate, the dominant terrain on ',' has changed '])
      links_to = ['Body']
      links[-1] = False
      pass
    elif (id == 285):
      #285	New Combat Contact:  45x Nuclear Detonation: Strength 7
      pass
    elif (id == 291):
      #291	Lee Mi-Ja   Ground Combat Training 5%    Ground Combat Offence 5%    Ground Combat Defence 5%  
      pass
    elif (id == 292):
      #'Sergeant Carroll Berlingeri has retired from the service at the age of 46. Current Assignment: Unassigned')
      results, links = self.SplitData(text, searchTokens = [' has retired from the service at the age of ', '. Current Assignment: '])
      if (results[-1].find('Unassigned') > -1):
        results = []
        links = []
      else:
        links_to = []
        links[0] = False
        links[2] = False
        links[4] = False
    elif (id == 321):
      #321	GEV-01 Proxima Centauri 001 has exceeded its deployment time.
      results, links = self.SplitData(text, searchTokens = [' has exceeded its deployment time.'])
      links_to = ['Ship']
      pass
    elif (id == 335):
      #335	45x Khristina Tiyahahu Anti-Ship Missile from ODB-01 Allosaurus 001 attacked XX Pachaug Victory 001.    Chance to Hit 375%     Damage per Hit 7    The target was destroyed by 45 hits    New Target Speed 1 km/s
      results, links = self.SplitData(text, searchTokens = [' from ',' attacked ','. '])
      links_to = ['Missile','Ship', 'Contact']
      links[-1] = False
      pass
    elif (id == 345):
      #345	SO-09 Mantis Shrimp Mk.2 001 attacked by missiles.   Damage per Hit 7    Penetrating Hits 3
      results, links = self.SplitData(text, searchTokens = [' attacked by '])
      links_to = ['Ship']
      links[-1] = False
      pass
    #if (len(links) > 0):
    #  if (links[-1] == False):
    #    results[-2]+=results[-1]
    #    del results[-1]
    #    del links[-1]
    return results, links, links_to


  def GetSubText(self, line, search1 = None, search2 = None):
    index1 = -1
    if (search1):
      index1 = line.find(search1)
      if (index1 > -1):
        index1 += len(search1)
    index2 = -1
    if (search2):
      index2 = line.find(search2)
    if (index1 > -1):
      if (index2 > -2):
        subtext = line[index1:index2]
      else:
        subtext = line[index1:]
    else:
      if (index2 > -2):
        subtext = line[:index2]
      else:
        subtext = line
    return subtext


  def SplitData(self, line, searchTokens = []):
    split_line = []
    links = []
    remaining_text = line
    for token in searchTokens:
      values = remaining_text.split(token)
      if (len(values[0]) > 0):
        split_line.append(values[0])
        links.append(True)
      split_line.append(token)
      links.append(False)
      remaining_text = values[-1]
    if (len(remaining_text) > 0):
      split_line.append(remaining_text)
      links.append(True)

    return split_line, links

  def CheckTokensInText(self, text, tokens):
    for t in tokens:
      if (text.find(t) == -1):
        return False
    else:
      return True
  #def GetClickedEvent(self):
  #  event = self.clickedEvent
  #  self.clickedEvent = {}
  #  return event