import Utils
import pygame
import math
import random
import Fleets
import Systems
import Bodies
import json

todo_types = {'Geosurvey':    {'std_prio':1,'text_tokens':['Geosurvey ', ' bodies in ']                  , 'value_indexes':['other', 'systemName'],},
              'Gravsurvey':   {'std_prio':2,'text_tokens':['Gravsurvey ', ' survey locations in ']       , 'value_indexes':['other', 'systemName'],},
              'Groundsurvey': {'std_prio':1,'text_tokens':['Groundsurvey ', ' in ']                      , 'value_indexes':['bodyName', 'systemName'],},
              'Archeology':   {'std_prio':1,'text_tokens':['Analyze ruins on ', ' in ']                  , 'value_indexes':['bodyName', 'systemName'],},
              'Excavate':     {'std_prio':1,'text_tokens':['Excavate ', ' ruins on ', ' in ']            , 'value_indexes':['other', 'bodyName', 'systemName'],},
              'ResearchBonus':{'std_prio':1,'text_tokens':['Establish ', ' research on ', ' in ']        , 'value_indexes':['other', 'bodyName', 'systemName'],},
              'Jumpgate':     {'std_prio':1,'text_tokens':['Build jump gate from ', ' to ']              , 'value_indexes':['systemName', 'target'],},
              'Jumpship':     {'std_prio':1,'text_tokens':['Place jump ship at jump point from ', ' to '], 'value_indexes':['systemName', 'target'],},
              'Explore JP':   {'std_prio':1,'text_tokens':['Explore jump point ', ' in ']                , 'value_indexes':['target', 'systemName'],},
              'Colonize':     {'std_prio':1,'text_tokens':['Colonize ', ' in ']                          , 'value_indexes':['bodyName', 'systemName'],}, 
              'Industrialize':{'std_prio':1,'text_tokens':['Industrialize ', ' in ']                     , 'value_indexes':['bodyName', 'systemName'],}, 
              'Harvest':      {'std_prio':1,'text_tokens':['Harvest Sorium at ', ' in ']                 , 'value_indexes':['bodyName', 'systemName'],}, 
              'Police':       {'std_prio':1,'text_tokens':['Increase police force in ']                  , 'value_indexes':['systemName'],},
              'Wealth':       {'std_prio':1,'text_tokens':['Increase wealth production']                 , 'value_indexes':[],},
              'Fuel':         {'std_prio':1,'text_tokens':['Increase fuel on ', ' in ']                  , 'value_indexes':['bodyName', 'systemName'],},
              'Supplies':     {'std_prio':1,'text_tokens':['Increase supplies production on ', ' in ']   , 'value_indexes':['bodyName', 'systemName'],},
              'Terraform':    {'std_prio':1,'text_tokens':['Terraform ', ' in ']                         , 'value_indexes':['bodyName', 'systemName'],},
              'Stabilize':    {'std_prio':1,'text_tokens':['Stabilize LP ', ' in ']                      , 'value_indexes':['bodyName', 'systemName'],}
              }

class Todo():
  def __init__(self, game):
    self.game = game
    self.todo = {}
    self.last_index = 0
  #{'systemID':id, 'systemName':systemName, 'priority':priority, 'index':index, 'type':todo_type, 'colonyID':colonyID, 'colonyName':colonyName, 'progress':progress, 'text':text, 'numItems':numItems, 'targetID':targetID, 'targetName':targetName}


  def CheckTodo(self, _todo_type, system=None, body=None, target=None, other=None):
    if _todo_type in todo_types:
      index = self.FindTodoListIndex(_todo_type, system, body, target, other)
      if index:
        self.UpdateTodo(index, progress=None, priority=None)
      else:
        self.AddTodo(_todo_type, system, body, target, other)
    else:
      print('Unknown todo type: %s'%_todo_type)
  

  def FindTodoListIndex(self, _todo_type, sysID, bodyID, targetID, other):
    return None


  def AddTodo(self, _todo_type, system=None, body=None, target=None, other=None):
    self.todo[self.last_index] = {}
    this_todo = self.todo[self.last_index]
    this_todo['type'] = _todo_type
    this_todo['priority'] = todo_types[_todo_type]['std_prio']
    print_in = True
    if system:
      this_todo['systemID'] = system['ID']
      this_todo['systemName'] = system['Name']
      if (body):
        this_todo['bodyID']= body['ID']
        this_todo['bodyName']=body['Name']
        if this_todo['systemName'] in body['Name']:
          print_in = False

    text_tokens = todo_types[_todo_type]['text_tokens']
    value_indexes = todo_types[_todo_type]['value_indexes']
    
    text = text_tokens[0]
    
    for i in range(1,len(text_tokens)+1):
      token = ''
      if i-1 < len(value_indexes):
        if (value_indexes[i-1] == 'other'):
          token = str(other)
        elif (value_indexes[i-1] == 'target'):
          token = target
        elif (value_indexes[i-1] == 'systemName'):
          if print_in:
            token = this_todo[value_indexes[i-1]]
        else:
            token = this_todo[value_indexes[i-1]]
      
        text += token
      if i < len(text_tokens):
        if (print_in):
          text += str(text_tokens[i])

    this_todo['text']=text
    this_todo['checked'] = True

    #item = {'systemID':sysID, 'systemName':systemName, 'priority':priority, 'type':todo_type, 'bodyID':bodyID, 'bodyName':bodyName, 'progress':progress, 'text':text, 'numItems':numItems, 'targetID':targetID, 'targetName':targetName, 'text_values':[]}

    self.last_index += 1

  def UpdateTodo(self, index, priority):
    pass


  def ChangePriority(self):
    pass


  def PurgeList(self):
    for item in self.todo:
      if not item['checked']:
        self.todo.remove(item)


  def ResetList(self):
    for item in self.todo:
      item['checked'] = False


  def Load(self):
    if (self.gameInstance):
      filename = 'todos_game_%d.json'%self.gameInstance.gameID
      try:
        with open(filename, 'r') as f:
          self.todo = json.load(f)
      except:
        print('File %s not found'%filename)  


  def Save(self):
    if (self.gameInstance):
      filename = 'todos_game_%d.json'%self.gameInstance.gameID
      try:
        with open(filename, 'w') as f:
          json.dump(self.todo, f)
      except:
        print('File %s not writeable'%filename)
