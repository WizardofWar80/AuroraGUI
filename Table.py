import Utils
import pygame

class Cell():
  def __init__(self, pos, width, height, value = None, type = None, x = -1, y = -1, text_color = (255,255,255), bg_color = (0,0,0), text_size = 20, border_color = (120,120,120)):
    self.value = value
    self.type = type
    self.x = x
    self.y = y
    self.screenpos = pos
    self.text_color = text_color
    self.border_color = border_color
    self.bg_color = bg_color
    self.text_size = text_size
    self.font = pygame.font.SysFont("Times New Roman", text_size)
    self.width = width
    self.height = height
    self.rect = (pos[0], pos[1], width, height)


class Table():
  def __init__(self, context, rows, cols, header = True, row_height = 20, col_widths = 150, anchor = (0,0)):
    self.context = context
    self.header = header
    self.cells = []
    self.row_height = row_height
    self.col_widths = col_widths
    self.num_rows = rows
    self.num_cols = cols
    self.anchor = anchor
    self.InitTable()
    self.in_cell_pad_x = 4
    self.in_cell_pad_y = 3


  def InitTable(self):
    for r in range(self.num_rows):
      self.cells.append([])
      current_lat_pos = 0
      for c in range(self.num_cols):
        col_width = self.GetWidth(c)
        screenpos = Utils.AddTuples(self.anchor, (current_lat_pos, r * self.row_height))

        self.cells[-1].append(Cell(screenpos, col_width, self.row_height, value = '%d,%d'%(c,r), type = 'string', x = c, y = r))
        current_lat_pos += col_width

  def GetWidth(self, col_index):
    if(len(self.col_widths) == self.num_cols):
      return self.col_widths[col_index]
    elif (len(self.col_widths) == 1):
      return self.col_widths


  def Draw(self):
    # draw the grid:
    for row in self.cells:
      for cell in row:
        pygame.draw.rect(self.context.surface, cell.border_color, cell.rect, 1)

        if (cell.value):
          Utils.DrawText2Surface(self.context.surface, str(cell.value), textPos, 12, cell.text_color)
          textPos = Utils.AddTuples(cell.screenpos, (self.in_cell_pad_x, self.in_cell_pad_y))

    return True
    #if(len(self.col_widths) == self.num_cols):
    #  pass
    #elif (len(self.col_widths) == 1):
    #  width = self.col_widths
    #  self.col_widths = []
    #  for i in self.num_cols:
        
    
