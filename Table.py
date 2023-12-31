import Utils
import pygame
import Scrollbar

class Cell():
  def __init__(self, pos, width, height, value = None, sortvalue = None, type = None, x = -1, y = -1, text_color = (255,255,255), bg_color = (0,0,0), text_size = 14, border_color = (120,120,120), align = 'left', bold = False, second_value = None):
    self.value = value
    self.prefix = ''
    self.suffix = ''
    self.sortvalue = sortvalue
    self.type = type
    self.x = x
    self.y = y
    self.screenpos = pos
    self.text_color = text_color
    self.default_text_color = text_color
    self.border_color = border_color
    self.bg_color = bg_color
    self.text_size = text_size
    self.bold = bold
    self.font = pygame.font.SysFont("Times New Roman", text_size, bold = bold)
    self.width = width
    self.height = height
    self.rect = (pos[0], pos[1], width, height)
    self.text_render = None
    self.text_size = None
    self.align = align
    #self.format = {}
    self.Render()


  def SetValue(self, value):
    self.value = value
    self.prefix = ''
    self.suffix = ''


  def Render(self):
    self.text_render = self.font.render(str(self.prefix)+str(self.value)+str(self.suffix), 0, self.text_color)
    self.text_size = self.text_render.get_rect().size


  def SetWidth(self, width):
    self.width = width
    self.rect = (self.screenpos[0], self.screenpos[1], width, self.height)


  def SetPos(self, pos):
    self.screenpos = pos
    self.rect = (self.screenpos[0], self.screenpos[1], self.width, self.height)

  def SetAlignment(self, align):
    self.align = align


  def Format(self, f):
    if ('Format' in f):
      if (f['Format'] == 'Percent'):
        if (self.value is not None) and (self.value is not ''):
          self.suffix='%'
    if ('Suffix' in f):
      if (self.value is not None) and (self.value is not ''):
        self.suffix= f['Suffix']
    if ('Operation' in f):
      if (f['Operation'] == 'Above'):
        if (self.value is not None) and (self.value is not ''):
          if (self.type is not 'string' ):
            if (self.value > f['threshold']):
              self.text_color=f['text_color']
              self.Render()
            elif ('else_color' in f):
              self.text_color=f['else_color']
              self.Render()
      if (f['Operation'] == 'Above+'):
        if (self.value is not None) and (self.value is not ''):
          if (self.type is not 'string' ):
            if (self.value > f['threshold']):
              self.text_color=f['text_color']
              self.suffix=' ^'
              self.Render()
            elif ('else_color' in f):
              self.text_color=f['else_color']
              self.Render()
      elif (f['Operation'] == 'Below'):
        if (self.value is not None) and (self.value is not ''):
          if (self.type is not 'string' ):
            if (self.value < f['threshold']):
              self.text_color=f['text_color']
              self.Render()
            elif ('else_color' in f):
              self.text_color=f['else_color']
              self.Render()
      elif (f['Operation'] == 'Below-'):
        if (self.value is not None) and (self.value is not ''):
          if (self.type is not 'string' ):
            if (self.value < f['threshold']):
              self.text_color=f['text_color']
              self.suffix=' v'
              self.Render()
            elif ('else_color' in f):
              self.text_color=f['else_color']
              self.Render()
      elif (f['Operation'] == 'Between'):
        if (self.value is not None) and (self.value is not ''):
          if (self.type is not 'string' ):
            if (self.value >= f['threshold_low']) and (self.value <= f['threshold_high']):
              self.text_color=f['text_color']
              self.Render()
            else:
              if (self.value <= f['threshold_low']):
                if ('too_low_color' in f):
                  self.text_color=f['too_low_color']
                self.Render()
              else:
                if ('too_high_color' in f):
                  self.text_color=f['too_high_color']
                self.Render()
      elif (f['Operation'] == 'Between+-'):
        if (self.value is not None) and (self.value is not ''):
          if (self.type is not 'string' ):
            if (self.value > f['threshold_low']) and (self.value < f['threshold_high']):
              self.text_color=f['text_color']
              self.Render()
            else:
              if (self.value <= f['threshold_low']):
                if ('too_low_color' in f):
                  self.text_color=f['too_low_color']
                self.suffix=' v'
                self.Render()
              else:
                if ('too_high_color' in f):
                  self.text_color=f['too_high_color']
                self.suffix=' ^'
                self.Render()
      elif (f['Operation'] == 'Align'):
        self.SetAlignment(align = f['value'])      


class Table():
  def __init__(self, context, rows, cols, header = True, row_height = 20, col_widths = 50, anchor = (0,0), align = 'left', max_rows = 25):
    self.context = context
    self.header = header
    self.cells = []
    self.row_height = row_height
    self.col_widths = col_widths
    self.anchor = anchor
    self.max_rows = max_rows
    self.num_rows = rows
    self.num_cols = cols
    self.align = align
    self.rect = pygame.Rect(anchor[0], anchor[1], 50*cols,row_height*(min(rows, self.max_rows)))
    self.scroll_position = 0
    #self.InitTable()
    self.in_cell_pad_x = 4
    self.in_cell_pad_y = 3
    self.max_cell_sizes = []
    self.hideEmptyColumns = True
    self.dataColumns = []
    self.maxScroll = min(0,self.max_rows-self.num_rows)
    #self.colFormats = [[],[],[],[],[],
    #                   [],[],[],[],[],
    #                   [],[],[],[],[],
    #                   [],[],[],[],[]
    #                   ]
    self.colFormats = []
    for i in range(self.num_cols):
      self.colFormats.append([])
      self.dataColumns.append(False)
    self.scrollbar = None


  def ToggleHideCells(self):
    self.hideEmptyColumns = not self.hideEmptyColumns


  def Scrollbar(self):
    # pos, height, visible_range, total_range, parent
    self.scrollbar = Scrollbar.Scrollbar(self.context.surface, (self.rect[0]+self.rect[2],self.rect[1]), self.rect[3], min(self.num_rows, self.max_rows), self.num_rows, self, self.context.game)


  def InitTable(self):
    pass
    #table_width = 0
    #table_height = 0

    #for r in range(self.num_rows):
    #  self.cells.append([])
    #  current_lat_pos = 0
    #  for c in range(self.num_cols):
    #    col_width = self.GetWidth(c)
    #    screenpos = Utils.AddTuples(self.anchor, (current_lat_pos, r * self.row_height))

    #    self.cells[-1].append(Cell(screenpos, col_width, self.row_height, x = c, y = r))
    #    current_lat_pos += col_width
    #  table_width = current_lat_pos
    #  table_height = screenpos[1]+self.row_height
    #  self.rect = (anchor[0], anchor[1], anchor[0]+table_width, anchor[1]+table_height)


  def AddFormat(self, column, cell_format):
    self.colFormats[column].append(cell_format)


  def GetWidth(self, col_index):
    if (self.max_cell_sizes):
      if(col_index < len(self.max_cell_sizes)):
        return self.max_cell_sizes[col_index]

    if(col_index < len(self.col_widths)):
      return self.col_widths[col_index]
    elif (len(self.col_widths) == 1):
      return self.col_widths
    else:
      return  self.col_widths[-1]


  def GetType(self, value):
    if (not value):
      return None
    elif (type(value) is str):
      return 'string'
    elif (type(value) is int):
      return 'int'
    elif (type(value) is float):
      return 'float'


  def AddRow(self, row, data, row_format = []):
    updateCells = False
    cell_text_sizes = []
    if (len(self.cells) <= row):
      self.cells.append([])
      index = -1
      self.num_rows += 1
    else:
      index = row
      updateCells = True
      self.num_rows += 1
      #self.cells[index] = []

    current_lat_pos = 0
    for c in range(self.num_cols):
      if (c < len(data)):
        bold = False
        if c < len(row_format):
          bold = row_format[c]
        col_width = self.GetWidth(c)
        screenpos = Utils.AddTuples(self.anchor, (current_lat_pos, row * self.row_height))
        if (updateCells):
          self.cells[index][c].screenpos = screenpos
          self.cells[index][c].value = data[c]
          self.cells[index][c].prefix = ''
          self.cells[index][c].suffix = ''
          self.cells[index][c].type = self.GetType(data[c])
          self.cells[index][c].SetWidth(col_width)
          self.cells[index][c].bold = bold
          self.cells[index][c].Render()
          self.cells[index][c].text_color = self.cells[index][c].default_text_color
          cell_text_sizes.append(self.cells[index][c].text_size[0])
        else:
          self.cells[index].append(Cell(screenpos, col_width, self.row_height, value = data[c], type = self.GetType(data[c]), x = c, y = row, bold = bold, align = ('left' if row == 0 else self.align)))
          cell_text_sizes.append(self.cells[index][-1].text_size[0])
        if (self.header and row == 0):
          cell_text_sizes[-1] += 10
        else:
          for f in self.colFormats[c]:
            self.cells[index][c].Format(f)
          if (self.cells[index][c].value != '' and self.cells[index][c].value != None):
            self.dataColumns[c] = True
        current_lat_pos += col_width

    self.UpdateMaxCellWidths(cell_text_sizes)


  def UpdateMaxCellWidths(self, cell_text_sizes):
    for i in range(len(cell_text_sizes)):
      if (i < len(self.max_cell_sizes)):
        if (cell_text_sizes[i]+self.in_cell_pad_x*2 > self.max_cell_sizes[i]):
          self.max_cell_sizes[i] = cell_text_sizes[i]+self.in_cell_pad_x*2
      else:
        self.max_cell_sizes.append(cell_text_sizes[i]+self.in_cell_pad_x*2)


  def Realign(self):
    offset = 0
    if (self.num_rows > 0):
      for col in range(self.num_cols):
        shrink = False
        if (col < len(self.cells[0])):
          if (self.hideEmptyColumns and self.dataColumns[col] == False):
            self.cells[0][col].col_width=0
            self.max_cell_sizes[col]=0
            shrink = True
          col_width = self.cells[0][col].width
          delta = self.max_cell_sizes[col] - col_width
          if (delta < 0) and (not shrink):
            delta = 0
          if (delta > 0) or (offset > 0) or (shrink):
            self.FormatColumn(col, column_width=col_width+delta, latPos = offset+self.anchor[0])
          offset+=col_width+delta


  def FormatCell(self, r, c, text_color = None, bg_color = None, text_size = None, border_color = None, bold = False, column_width = None, latOffset = None, latPos = None, align = None):
    rerender = False
    if text_color:
      self.cells[r][c].text_color=text_color
      rerender = True
    if bg_color:
      self.cells[r][c].bg_color=bg_color
      rerender = True
    if text_size:
      self.cells[r][c].text_size=text_size
      rerender = True
    if border_color:
      self.cells[r][c].border_color=border_color
      rerender = True
    if column_width:
      self.cells[r][c].SetWidth(column_width)
      rerender = True
    if latOffset:
      self.cells[r][c].SetPos((self.cells[r][c].screenpos[0]+latOffset+self.anchor[0], self.cells[r][c].screenpos[1]))
      rerender = True
    if latPos:
      self.cells[r][c].SetPos((latPos, self.cells[r][c].screenpos[1]))
      rerender = True
    if align:
      if (not self.header or r > 0):
        self.cells[r][c].SetAlignment(align = align)      
    if (rerender):
      self.cells[r][c].Render()


  def FormatColumn(self, column, text_color = None, bg_color = None, text_size = None, border_color = None, bold = False, column_width = None, latOffset = None, latPos = None, align = None):
    for r in range(min(self.num_rows, len(self.cells))):
      if column < self.num_cols:
        self.FormatCell(r, column, text_color, bg_color, text_size, border_color, bold, column_width, latOffset, latPos, align)


  def FormatColumnIfValuesAbove(self, column, threshold, text_color = None, bg_color = None, text_size = None, border_color = None, bold = False):
    for r in range(min(self.num_rows, len(self.cells))):
      if column < self.num_cols:
        if (self.cells[r][column].value is not None):
          if (self.cells[r][column].type is not 'string' ):
            if (self.cells[r][column].value > threshold):
              self.FormatCell(r, column, text_color, bg_color, text_size, border_color, bold)


  def FormatColumnIfValuesBelow(self, column, threshold, text_color = None, bg_color = None, text_size = None, border_color = None, bold = False):
    for r in range(min(self.num_rows, len(self.cells))):
      if column < self.num_cols:
        if (self.cells[r][column].value is not None):
          if (self.cells[r][column].type is not 'string' ):
            if (self.cells[r][column].value < threshold):
              self.FormatCell(r, column, text_color, bg_color, text_size, border_color, bold)


  def FormatColumnIfValuesBetween(self, column, threshold_low, threshold_high, text_color = None, bg_color = None, text_size = None, border_color = None, bold = False):
    for r in range(min(self.num_rows, len(self.cells))):
      if column < self.num_cols:
        if (self.cells[r][column].value is not None):
          if (self.cells[r][column].type is not 'string' ):
            if (self.cells[r][column].value > threshold_low and self.cells[r][column].value < threshold_high):
              self.FormatCell(r, column, text_color, bg_color, text_size, border_color, bold)


  def Draw(self):
    t1 = pygame.time.get_ticks()
    table_width = 0
    table_height = 0
    # draw the grid:
    rowIndex = 0
    for row in self.cells:
      colIndex = 0
      for cell in row:
        if (self.hideEmptyColumns == False or self.dataColumns[colIndex]):
          pygame.draw.rect(self.context.surface, cell.border_color, cell.rect, 1)

          if (cell.value is not None):
            textPos = Utils.AddTuples(cell.screenpos, (self.in_cell_pad_x, self.in_cell_pad_y))
            if (cell.align == 'right'):
              textPos = (cell.screenpos[0] + cell.width - cell.text_size[0] - self.in_cell_pad_x, textPos[1])
            elif (cell.align == 'center'):
              textPos = (cell.screenpos[0] + cell.width/2 - cell.text_size[0]/2 , textPos[1])
            self.BlitRenderToSurface(cell, textPos)
        colIndex += 1
      table_width = cell.rect[0]+cell.rect[2]
      table_height = cell.rect[1]+cell.rect[3]
      self.rect = pygame.Rect(self.anchor[0], self.anchor[1], table_width, table_height)
      rowIndex += 1
      if (rowIndex >= self.num_rows):
        break
    t2 = pygame.time.get_ticks()
    print(t2- t1)
    if (self.context.game.Debug):
      pygame.draw.rect(self.context.surface, Utils.RED, self.rect, 1)
    self.scrollbar.Update(pos=(self.rect[0]+self.rect[2],self.rect[1]), height = self.rect[3], visible_range = min(self.num_rows-1, self.max_rows-1))
    self.scrollbar.Draw()

    return True
    #if(len(self.col_widths) == self.num_cols):
    #  pass
    #elif (len(self.col_widths) == 1):
    #  width = self.col_widths
    #  self.col_widths = []
    #  for i in self.num_cols:
        
    
  def BlitRenderToSurface(self, cell, textPos, transparent = True):
    surface = self.context.surface
    if (textPos[0] > 0 and textPos[1] > 0 and textPos[0] < surface.get_rect()[2] and textPos[1] < surface.get_rect()[3]):
      if (transparent):
        cell.text_render.set_alpha(255)
        surface.blit(cell.text_render, textPos)
      else:
        sf = pygame.Surface(cell.text_size)
        sf.fill(cell.bg_color)
        sf.blit(cell.text_render, (0,0))
        surface.blit(sf, textPos)
  
        
  def Clear(self):
    colIndex = 0
    for row in self.cells:
      for cell in row:
        cell.value = None
        self.dataColumns[colIndex] = False



  def GetLocationInsideTable(self, mouse_pos):
    row = None
    col = None
    value = None
    for i in range(len(self.cells[0])):
      cell = self.cells[0][i]
      if (mouse_pos[0] > cell.rect[0] and mouse_pos[0] < cell.rect[0]+cell.rect[2]):
        col = i
        break
    
    if (col is not None):
      for i in range(len(self.cells)):
        cell = self.cells[i][0]
        if (mouse_pos[1] > cell.rect[1] and mouse_pos[1] < cell.rect[1]+cell.rect[3]):
          row = i
          break
      if (row is not None):
        value = self.cells[row][col].value

    return row, col, value
