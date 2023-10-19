import pygame
import math

PROFILING = False

LIGHT_GRAY2 = (230,230,230)
LIGHT_GRAY = (220,220,220)
MED_GRAY = (200,200,200)
GRAY = (180,180,180)
DARK_GRAY = (100,100,100)
SUPER_DARK_GRAY = (30,30,30)
WHITE = (255, 255, 255)
LIGHT_GREEN = (0, 255, 0)
MED_GREEN = (0, 209, 0)
GREEN = (0, 100, 0)
LIGHT_BLUE = (50, 130, 191)
BLUE = (0, 0, 255)
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


I2R_Conv = [[1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'],
            [ 100, 'C'], [ 90, 'XC'], [ 50, 'L'], [ 40, 'XL'],
            [  10, 'X'], [  9, 'IX'], [  5, 'V'], [  4, 'IV'],
            [   1, 'I']]

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

MineralNames = {   1:'Duranium' 
                 , 2:'Neutronium'
                 , 3:'Corbomite'
                 , 4:'Tritanium'
                 , 5:'Boronide'
                 , 6:'Mercassium'
                 , 7:'Vendarite'
                 , 8:'Sorium'
                 , 9:'Uridium'
                 , 10:'Corundium'
                 , 11:'Gallicite'
                }

StarTypes = { 'D': 'White Dwarf'
             ,'WR': 'Wolf–Rayet Star'
             ,'Y': 'Y-Dwarf'
             ,'L': 'L-Dwarf'
             ,'T': 'T-Dwarf'
             ,'BH': 'Black Hole'}

SpectralColors = { 'A': 'White'
                  ,'B': 'Blue'
                  ,'D': 'White'
                  ,'F': 'Yellow'
                  ,'G': 'Yellow'
                  ,'K': 'Orange'
                  ,'M': 'Red'
                  ,'O': 'Blue'
                  ,'Y': 'Brown'
                  ,'L': 'Red'
                  ,'T': 'Purple'
                  ,'BH': 'None'
                  }

SafeGasLevels = { 'Hydrogen':{'Safe Level': 0.05, 'CC':2}
                 ,'Methane' :{'Safe Level': 0.05, 'CC':2}
                 ,'Ammonia' :{'Safe Level': 0.005, 'CC':2}
                 ,'Carbon Monoxide' :{'Safe Level': 0.005, 'CC':2}
                 ,'Nitrogen Oxide' :{'Safe Level': 0.005, 'CC':2}
                 ,'Oxygen' :{'Safe Level': 0.3, 'CC':2}
                 ,'Hydrogen Sulphide' :{'Safe Level': 0.002, 'CC':2}
                 ,'Carbon Dioxide' :{'Safe Level': 0.5, 'CC':2}
                 ,'Nitrogen Dioxide' :{'Safe Level': 0.0005, 'CC':2}
                 ,'Sulphur Dioxide' :{'Safe Level': 0.002, 'CC':2}
                 ,'Chlorine' :{'Safe Level': 0.0001, 'CC':3}
                 ,'Fluorine' :{'Safe Level': 0.0001, 'CC':3}
                 ,'Bromine' :{'Safe Level': 0.0001, 'CC':3}
                 ,'Iodine' :{'Safe Level': 0.0001, 'CC':2}
                 }

star_suffixes = ['A', 'B', 'C', 'D']

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


def DrawSizedTriangle(surface, pos, color, size, thickness):
  points = [( pos[0]-size, pos[1]+size*0.5),
            ( pos[0]+size, pos[1]+size*0.5),
            ( pos[0]     , pos[1]-size*1.5)]
  pygame.draw.polygon(surface,color, points, thickness)
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
  t1 = pygame.time.get_ticks()
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
  t2 = pygame.time.get_ticks()
  if (PROFILING):
    dt = t2-t1
    print('MyDrawEllipse: %d ms'%dt)
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


def DrawExpander(surface, position, textSize, color):
  bounding_box = pygame.Rect(position[0]+1,position[1]+1, textSize-2,textSize-2 )
  center = bounding_box.center
  size = 8
  pygame.draw.rect(surface, color, bounding_box, 1)
  x1 = center[0]-size/2
  x2 = center[0]+size/2
  y1 = center[1]
  y2 = center[1]
  pygame.draw.line(surface, color, (x1,y1), (x2,y2), 1)
  x1 = center[0]
  x2 = center[0]
  y1 = center[1]-size/2
  y2 = center[1]+size/2
  pygame.draw.line(surface, color, (x1,y1), (x2,y2), 1)
  
  return bounding_box


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


def IsOnScreen(screen, rect):
  return screen.get_rect().colliderect(rect)


def Int2Roman(number):
  roman = ''
  i = 0 #initiate i = 0
  while number > 0:
    while I2R_Conv[i][0] > number: i+=1 #increments i to largest value greater than current num
    roman += I2R_Conv[i][1] #adds the roman numeral equivalent to string
    number -= I2R_Conv[i][0] #decrements your num
  return roman


def Sqr(x):
  return x*x


def CalcSqrDistBetweenPoints(p1, p2):
  return Sqr(p1[0]-p2[0]) + Sqr(p1[1]-p2[1])


def GetRectCorners(rect):
  rect_corners=[]
  rect_corners.append((rect[0]        ,rect[1]))
  rect_corners.append((rect[0]+rect[2],rect[1]))
  rect_corners.append((rect[0]        ,rect[1]+rect[3]))
  rect_corners.append((rect[0]+rect[2],rect[1]+rect[3]))

  return rect_corners


def RectIntersectsRadius(rect, center, radius):
  radius_sqr = Sqr(radius)
  rect_corners = GetRectCorners(rect)

  point_inside_circle = False
  point_outside_circle = False
  for point in rect_corners:
    d_sqr = CalcSqrDistBetweenPoints(point, center)
    if (d_sqr < radius_sqr):
      point_inside_circle = True
    else:
      point_outside_circle = True
  if (point_inside_circle and point_outside_circle):
    return True
  #elif (point_outside_circle):
  #  cr = pygame.Rect(rect)
  #  if (cr.collidepoint(center)):
  #    return True, False
  #  else:
  #    # check if circle intersects with screen borders
  #    rect_vertices = []
  #    rect_vertices.append((rect[0]        ,rect[1], rect[2], 1))       # Top vertex
  #    rect_vertices.append((rect[0]        ,rect[1], 1,       rect[3])) # Left vertex
  #    rect_vertices.append((rect[0]+rect[2],rect[1], 1,       rect[3])) # Right vertex
  #    rect_vertices.append((rect[0]        ,rect[1], rect[2], rect[3])) # bottom vertex

  #    radius_vertices = []
  #    radius_vertices.append(pygame.Rect(center[0]        ,center[1], radius, 1))       # right vertex
  #    radius_vertices.append(pygame.Rect(center[0]        ,center[1], 1,       radius)) # down vertex
  #    radius_vertices.append(pygame.Rect(center[0]        ,center[1]- radius, 1,radius)) # up vertex
  #    radius_vertices.append(pygame.Rect(center[0]- radius,center[1],radius, 1))      # left vertex
  #    for rect_v in rect_vertices:
  #      for rad_v in radius_vertices:
  #        if (rad_v.colliderect(rect_v)):
  #          return True, False

  return False


def GetAnglesEncompassingRectangle(rect, center):
  rect_corners = GetRectCorners(rect)
  angles = []
  for point in rect_corners:
    angles.append(math.atan2(point[1]-center[1],point[0]-center[0]))

  min_angle = min(angles)
  max_angle = max(angles)

  return min_angle, max_angle


def DrawArc(surface, color, center, r, angle_start, angle_end, width):
  N = 60
  points = []
  end = False
  delta_angle = angle_end - angle_start
  for i in range(N):
    angle =  i/N*delta_angle+angle_start
    if (angle > angle_end):
      angle = angle_end
      end = True
    points.append((center[0]+math.cos(angle)*r,center[1]+math.sin(angle)*r))
    if end:
      break
  pygame.draw.lines(surface,color, False, points, width)
  

def DrawEllipticalOrbit(surface, color, pos, orbit, E, angle1, angle2, min_orbit):
  # draw orbit
  if (E > 0):
    a = orbit
    b = a * math.sqrt(1-E*E)
    #b = body['Orbit'] * self.systemScale
    #a = b*1/math.sqrt(1-E*E)
    c = E * a
    N = 60
    if (E > 0.9):
      N = 240
    x_offset = c * math.cos(angle1*DEGREES_TO_RADIANS)
    y_offset = c * math.sin(angle1*DEGREES_TO_RADIANS)
    offsetPos = AddTuples(pos, (x_offset,y_offset))

    MyDrawEllipse(surface, color, offsetPos[0],offsetPos[1], a, b,angle1,angle2, N)
  else:
    if (orbit < 50000 and orbit > min_orbit):
      pygame.draw.circle(surface, color, pos, orbit,1)


def GetStarDescription(star):
  # Neutron Stars:
  # 1.4 M☉ and 2.16 M
  # r <= 0.01
  description = star['BodyClass'] + '-Type Star'
  if (star['BodyClass'] in StarTypes):
    description = StarTypes[star['BodyClass']]
  else:
    if (star['Radius'] <= 0.01):
      description = 'Neutron Star'
    else:
      if (star['Mass'] <= 1):
        if (star['BodyClass'] in SpectralColors):
            color = SpectralColors[star['BodyClass']]
            description = color + ' Dwarf'
      elif (star['Mass'] < 10):
        if (star['Radius'] > 10):
          if (star['BodyClass'] in SpectralColors):
            color = SpectralColors[star['BodyClass']]
            description = color + ' Giant'
      else:
        if (star['BodyClass'] in SpectralColors):
          color = SpectralColors[star['BodyClass']]
          description = color + ' Supergiant'

  return description


def GetTimeScale(hours):
  timeframe = hours
  unit = 'h'
  if (timeframe > 72):
    timeframe /= 24
    unit = 'd'
  if (timeframe > 3*365.2):
    timeframe /= 365.2
    unit = 'a'
  fraction = abs(round(timeframe,1)-timeframe)
  if (fraction < 0.1):
    return '%d %s'%(round(timeframe,0), unit)
  else:
    return '%2.1f %s'%(round(timeframe,1), unit)


def GetFormattedNumber(number):
  if number is None:
    return '-'
  if (abs(number) > 0.99):
    fraction = abs(round(number,1)-number)
    if (abs(fraction) < 0.1):
      return '%d'%(round(number,0))
    else:
      return '%2.1f'%(round(number,1))
  else:
    if number == 0.0:
      return '0'
    if (abs(number) < 0.001):
      return '{:.1e}'.format(number)
    elif (abs(number) < 0.01):
      return '%1.3f'%(round(number,3))
    elif (abs(number) < 0.1):
      return '%1.2f'%(round(number,2))
    else:
      return '%1.1f'%(round(number,1))


def ConvertNumber2kMGT(value):
  if (type(value) is int) or (type(value) is float):
    if value > 999999999999.5:
      return '%d T'%(int(round(value / 1000000000000,0)))
    if value > 999999999.5:
      return '%d G'%(int(round(value / 1000000000,0)))
    if value > 999999.5:
      return '%d M'%(round(value / 1000000,0))
    elif value > 999.5:
      return '%d k'%(round(value / 1000,0))
    elif value > 9.99:
      return '%d'%(int(round(value,0)))
    elif value > 0.01:
      return '%d'%(round(value,2))
    else:
      return '0'
  else:
    return value