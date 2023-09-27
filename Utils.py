import pygame
import math

LIGHT_GRAY2 = (230,230,230)
LIGHT_GRAY = (220,220,220)
MED_GRAY = (200,200,200)
GRAY = (180,180,180)
DARK_GRAY = (100,100,100)
SUPER_DARK_GRAY = (30,30,30)
WHITE = (255, 255, 255)
LIGHT_GREEN = (0, 255, 0)
MED_GREEN = (186, 209, 198)
GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
MED_YELLOW = (255, 216, 0)
ORANGE = (255, 168, 54)
LIGHT_CYAN = (0, 235, 250)
CYAN = (19, 211, 214)
TEAL = (19, 214, 162)
PURPLE = (128, 0, 128)
GREENSCREEN = (255, 0, 255)
BLUE = (0, 0, 255)

BodyClasses = {  1:'Planet'
               , 2:'Moon'
               , 3:'Asteroid'
               , 4:'???'
               , 5:'Comet'}

BodyTypes = {    1:'Asteroid' 
               , 2:'Planet Terrestrial'
               , 3:'Planet Small'
               , 4:'Planet Gas Giant'
               , 5:'Planet Super Jovian'
               , 6:'???'
               , 7:'Moon Small'
               , 8:'Moon'
               , 9:'Moon Large'
               , 10:'Moon Small Terrestrial'
               , 11:'Moon Terrestrial'
               , 12:'??? Moon Large Terrestrial'
               , 13:'???'
               , 14:'Comet' }
FILLED = 0
AU = 149597870.7
AU_INV = 6.6845871222684454959959533702106E-9
DEGREES_TO_RADIANS = 0.0174533
RADIANS_TO_DEGREES = 57.2957795

def Sqr(x):
  return x*x


def DrawTextAt(window, text, x, y, fonttype, fg):
  if (x > 0 and y > 0 and x < window.get_rect()[2] and y < window.get_rect()[3]):
    fonttype.render_to(window, (x, y), text, (fg[0], fg[1], fg[2], 128))

#def DrawTextCenteredAt(surface, text, x, y, fonttype, bg, fg):
#  rendered_text = fonttype.render(text, True, fg, bg)
#  textRect = rendered_text.get_rect()
#  textRect.center = (x, y)
#  surface.blit(rendered_text, textRect)

def DrawText2Surface(window, text, pos, textsize, textcolor, centered = False, transparent = True):
  if (pos[0] > 0 and pos[1] > 0 and pos[0] < window.get_rect()[2] and pos[1] < window.get_rect()[3]):
    font = pygame.font.SysFont("Times New Roman", textsize)
    label = font.render(text, 0, textcolor)
    label_size = label.get_rect().size
    if (transparent):
      label.set_alpha(255)
      window.blit(label, pos)
    else:
      sf = pygame.Surface(label_size)
      sf.fill(BLACK)
      sf.blit(label, (0,0))
      window.blit(sf,pos)
    return pos, label_size
  else:
    return None, None


def DrawText2Screen(screen, text, pos, textsize, textcolor, transparent = True):
  if (pos[0] > 0 and pos[1] > 0 and pos[0] < screen.get_rect()[2] and pos[1] < screen.get_rect()[3]):
    font = pygame.font.SysFont("Times New Roman", textsize)
    label = font.render(text, 0, textcolor)
    sf = pygame.Surface(label.get_rect().size)
    if (not transparent):
      sf.fill(BLACK)
    sf.blit(label, (0,0))
    screen.blit(sf,pos)


def DrawTextCenteredAt(window, text, x, y, fonttype, fg):
  if (x > 0 and y > 0 and x < window.get_rect()[2] and y < window.get_rect()[3]):
    sf = pygame.Surface((200,200))
    ft_render_to_rect = fonttype.render_to(sf, (x, y), text, (fg[0], fg[1], fg[2], 128))
    fonttype.render_to(window, (x-ft_render_to_rect[2]*.5, y-ft_render_to_rect[3]*.5), text, (fg[0], fg[1], fg[2], 128))


def draw_ellipse_angle(surface, color, rect, angle, width=0):
  if (rect[1][0]*rect[1][1] < 5000000):
    target_rect = pygame.Rect(rect)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(shape_surf, color, (0, 0, *target_rect.size), width)
    rotated_surf = pygame.transform.rotate(shape_surf, -angle)
    r = rotated_surf.get_rect(center = target_rect.center)
    position = (rect[0][0],rect[0][1])
    surface.blit(rotated_surf, (position[0]-r.center[0]+r[0],position[1]-r.center[1]+r[1]))


def GetXYFromPolCoord(screen_anchor, parent_pos, distance, bearing, scale):
  x = parent_pos[0]+math.sin(angle*0.0174533)*distance
  y = parent_pos[1]+math.cos(angle*0.0174533)*distance
  pos_x = screen_anchor[0]+x*scale
  pos_y = screen_anchor[1]+y*scale

  return (pos_x, pos_y)


def DrawTriangle(surface,position, color, heading=0):
  target_rect = pygame.Rect(0,0,10,8)
  shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
  points = [( 6+4, 0+4),
            (-4+4, 4+4),
            (-4+4,-4+4)]
  pygame.draw.polygon(shape_surf,color, points, 0)
  rotated_surf = pygame.transform.rotate(shape_surf, -heading)
  r = rotated_surf.get_rect(center = target_rect.center)
  surface.blit(rotated_surf,(position[0]-r.center[0]+r[0],position[1]-r.center[1]+r[1]))
  bounding_box = pygame.Rect(position[0]-r.center[0]+r[0],position[1]-r.center[1]+r[1], r.size[0],r.size[1])
  return bounding_box
  #pygame.draw.rect(surface,(255,255,255), ((position[0]-6,position[1]-6),(12,12)), 1)


def DrawArrow(surface,position, color, heading=0):
  heading_deg = -heading*RADIANS_TO_DEGREES
  position = (position[0],position[1]-0)
  target_rect = pygame.Rect(0,0,15,2*28)
  shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
  points = [(0 ,15),
            (8 ,15),
            (8 ,0),
            (14 ,28),
            (14 ,29),
            (8 ,56),
            (8 ,41),
            (0 ,41),
            (0 ,15)]
  pygame.draw.polygon(shape_surf,color, points, 0)
  rotated_surf = pygame.transform.rotate(shape_surf, heading_deg)
  r = rotated_surf.get_rect(center = target_rect.center)
  offset_x = 25 * math.cos(-heading)
  offset_y = 25 * math.sin(-heading)
  surface.blit(rotated_surf,(position[0]-r.center[0]+r[0]+offset_x,position[1]-r.center[1]+r[1]-offset_y))
  bounding_box = pygame.Rect(position[0]-r.center[0]+r[0]+offset_x ,position[1]-r.center[1]+r[1]-offset_y, r.size[0],r.size[1])
  return bounding_box
  #pygame.draw.rect(surface,RED,bounding_box,1)

def AddTuples(t1,t2):
  if isinstance(t1, (list, tuple)):
    if isinstance(t2, (list, tuple)):
      return ((t1[0]+t2[0]),(t1[1]+t2[1]))
    else:
      return ((t1[0]+t2),(t1[1]+t2))
  else:
    if isinstance(t2, (list, tuple)):
      return ((t1+t2[0]),(t1+t2[1]))
    else:
      return ((t1+t2),(t1+t2))


def SubTuples(t1,t2):
  if isinstance(t1, (list, tuple)):
    if isinstance(t2, (list, tuple)):
      return ((t1[0]-t2[0]),(t1[1]-t2[1]))
    else:
      return ((t1[0]-t2),(t1[1]-t2))
  else:
    if isinstance(t2, (list, tuple)):
      return ((t1-t2[0]),(t1-t2[1]))
    else:
      return ((t1-t2),(t1-t2))


def MulTuples(t1,t2):
  if isinstance(t1, (list, tuple)):
    if isinstance(t2, (list, tuple)):
      return ((t1[0]*t2[0]),(t1[1]*t2[1]))
    else:
      return ((t1[0]*t2),(t1[1]*t2))
  else:
    if isinstance(t2, (list, tuple)):
      return ((t1*t2[0]),(t1*t2[1]))
    else:
      return ((t1*t2),(t1*t2))


def DivTuples(t1,t2):
  if isinstance(t1, (list, tuple)):
    if isinstance(t2, (list, tuple)):
      return ((t1[0]/t2[0]),(t1[1]/t2[1]))
    else:
      return ((t1[0]/t2),(t1[1]/t2))
  else:
    if isinstance(t2, (list, tuple)):
      return ((t1/t2[0]),(t1/t2[1]))
    else:
      return ((t1/t2),(t1/t2))


def MyDrawEllipse(surface, color, x_c,y_c, a, b, beta=0, startAngle = 0, N = 60):
  beta *= DEGREES_TO_RADIANS
  startAngle *= DEGREES_TO_RADIANS
  cos_beta = math.cos(beta)
  sin_beta = math.sin(beta)
  x = y = 0
  points = []
  points_on_screen = []
  num_points_on_screen = 0
  surf_rect = surface.get_rect()
  for i in range(N):
    angle =  i/N*2*math.pi+startAngle
    x,y = GetEllipseXY(x_c, y_c, a, b, angle, beta, cos_beta, sin_beta)
    points.append((x,y))
    points_on_screen.append(surf_rect.collidepoint((x,y)))
    if (points_on_screen[-1]):
      num_points_on_screen+=1
  pygame.draw.polygon(surface,color, points, 1)
  #if (num_points_on_screen > 1):
  #  
  #  if (num_points_on_screen < 0.5 * N):
  #    points = []
  #    angle = beta
  #    x2,y2 = GetEllipseXY(x_c, y_c, a, b, angle, beta, cos_beta, sin_beta)
  #    while (angle - beta <= 2*math.pi):
  #      x1,y1 = GetEllipseXY(x_c, y_c, a, b, angle, beta, cos_beta, sin_beta)
  #      if surf_rect.collidepoint((x1,y1)) or surf_rect.collidepoint((x2,y2)):
  #        points.append((x1,y1))
  #        angle += 360/N*DEGREES_TO_RADIANS/4
  #      else:
  #        angle += 360/N*DEGREES_TO_RADIANS*4
  #      x2 = x1
  #      y2 = y1
  #    pygame.draw.polygon(surface,color, points, 1)
  #  else:
  #    pygame.draw.polygon(surface,color, points, 1)


def GetEllipseXY(x_c, y_c, a, b, angle, beta, cos_beta, sin_beta):
  if (beta == 0):
    x = a * math.cos(angle)
    y = b * math.sin(angle)
  else:
    a_cos_alpha = a * math.cos(angle)
    b_sin_alpha = b * math.sin(angle)
    x = a_cos_alpha * cos_beta - b_sin_alpha * sin_beta
    y = a_cos_alpha * sin_beta + b_sin_alpha * cos_beta
  return x_c+x,y_c+y


  #i_N = 0
  #a_cos_alpha = a * math.cos(i_N)
  #b_sin_alpha = b * math.sin(i_N)
  #x = x_c+a_cos_alpha * cos_beta - b_sin_alpha * sin_beta
  #y = y_c+a_cos_alpha * sin_beta + b_sin_alpha * cos_beta

  #i_N = math.pi
  #a_cos_alpha = a * math.cos(i_N)
  #b_sin_alpha = b * math.sin(i_N)
  #x2 = x_c+a_cos_alpha * cos_beta - b_sin_alpha * sin_beta
  #y2 = y_c+a_cos_alpha * sin_beta + b_sin_alpha * cos_beta

  pygame.draw.polygon(surface,color, points, 1)
  #pygame.draw.line(surface,WHITE, (x,y),(x2,y2), 1)
  #pygame.draw.rect(surface,RED, ((x_c-1,y_c-1),(3,3)), 0)
  #pygame.draw.rect(surface,YELLOW, ((x_c+x,y_c+y),(1,1)), 1)
  #pygame.draw.rect(surface,YELLOW, ((x_c-x,y_c-y),(1,1)), 1)

def DrawPercentageFilledImage(window, image, pos, percentage, color_unfilled = WHITE, color = LIGHT_GREEN, color_low = None, perc_low = None, color_high = None, perc_high = None):
  if (percentage > 1):
    percentage /= 100
  if (percentage > 1):
    percentage = 1
  use_color = color
  if (perc_low and color_low):
    if (percentage <= perc_low):
      use_color = color_low
  if (perc_high and color_high):
    if (percentage >= perc_high):
      use_color = color_high

  image_size = image.get_rect().size
  image_height_white = int((1-percentage) * image_size[1])
  image_height_green = image_size[1] - image_height_white
  white_image = pygame.Surface((image_size[0],image_height_white))
  white_image.fill(color_unfilled)
  green_image = pygame.Surface((image_size[0],image_height_green))
  green_image.fill(use_color)
  window.blit(white_image,pos)
  window.blit(green_image,(pos[0],pos[1]+image_height_white))
  window.blit(image,pos)

  return (pos[0],pos[1],image_size[0], image_size[1])