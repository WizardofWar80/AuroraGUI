import Utils
import pygame


def DrawStars(game):
  system = game.starSystems[game.currentSystem]

  for starID in system['Stars']:
    star = system['Stars'][starID]
    screen_star_pos = game.WorldPos2ScreenPos(star['Pos'])
    star_name = star['Name'] + ' ' + star['Suffix']
    # draw star
      
    # draw orbit
    ############
    screen_parent_pos = game.WorldPos2ScreenPos(star['ParentPos'])
    if (game.showOrbits_Stars):
      orbitRadiusOnScreen = star['OrbitDistance']*game.systemScale
      if (orbitRadiusOnScreen > 0):
        Utils.DrawEllipticalOrbit(game.surface, game.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, star['Eccentricity'], star['EccentricityAngle'],star['Bearing'], 10)
        #if (orbitRadiusOnScreen < game.width):
        #  pygame.draw.circle(game.surface, game.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, 1)
        #else:
        #  if Utils.RectIntersectsRadius((0,0,game.width, game.height), screen_parent_pos, orbitRadiusOnScreen):
        #    min_angle, max_angle = Utils.GetAnglesEncompassingRectangle((0,0,game.width, game.height), screen_parent_pos)
        #    Utils.DrawArc(game.surface, game.color_Orbit_Star, screen_parent_pos, orbitRadiusOnScreen, min_angle, max_angle, 1)
      
    # draw Star, either as image or as simple filled circle
    ####################
    radius = (Utils.AU_INV*game.systemScale)*star['Radius']*game.radius_Sun
    star_color = game.stellarTypes[star['StellarTypeID']]['RGB']
    if (radius < game.minPixelSize_Star):
      radius = game.minPixelSize_Star

    if (star['Image'] is not None):
      if (screen_star_pos[0]-radius < game.width and screen_star_pos[0]+radius > 0 and 
          screen_star_pos[1]-radius < game.height and screen_star_pos[1]+radius > 0 ):
        scale = (radius*2,radius*2)
        if (scale[0] > 2*game.width):
          #todo: fix bug where the scaled surface moves when zooming in too much
          scale = (2*game.width,2*game.width)
        scaledSurface = pygame.transform.smoothscale(star['Image'],scale)
        image_offset = Utils.SubTuples(screen_star_pos,scaledSurface.get_rect().center)
        game.surface.blit(scaledSurface,image_offset)
    else:
      if (not star['Black Hole']):
        pygame.draw.circle(game.surface,star_color,screen_star_pos,radius,Utils.FILLED)
      else:
        pygame.draw.circle(game.surface,Utils.RED,screen_star_pos,radius,5)
    bb = (screen_star_pos[0]-radius,screen_star_pos[1]-radius,2*radius,2*radius)
    if (game.CheckClickableNotBehindGUI(bb)):
      game.MakeClickable(star_name, bb, left_click_call_back = game.Select_Body, par=starID)

    # Label Star
    ################
    if (game.highlighted_body_ID == starID):
      color = Utils.CYAN
    else:
      color = game.color_Label_Star
    labelPos = Utils.AddTuples(screen_star_pos, (0,radius))
    Utils.DrawText2Surface(game.surface,star_name,labelPos,14,color)


def DrawBodies(game):
  system = game.starSystems[game.currentSystem]

  for bodyID in game.systemBodies:
    body = game.systemBodies[bodyID]

    body_draw_cond, draw_color_body, body_min_size, body_min_dist = GetDrawConditions(game, 'Body', body)
    if (body_draw_cond):
      screen_body_pos = game.WorldPos2ScreenPos(body['Pos'])
      radius_on_screen = Utils.AU_INV * game.systemScale * body['RadiusBody']
      if (radius_on_screen < body_min_size):
        radius_on_screen = body_min_size

      orbit_draw_cond, draw_color_orbit, void, min_orbit = GetDrawConditions(game, 'Orbit', body)
      orbitOnScreen = body['Orbit']*game.systemScale

      if (orbit_draw_cond) and (orbitOnScreen > body_min_dist):
        E = body['Eccentricity']
        parentID = body['ParentID']

        if parentID in system['Stars']:
          screen_parent_pos = game.WorldPos2ScreenPos(system['Stars'][parentID]['Pos'])
        elif parentID in game.systemBodies:
          screen_parent_pos = game.WorldPos2ScreenPos(game.systemBodies[parentID]['Pos'])
        else:
          screen_parent_pos = game.WorldPos2ScreenPos((0,0))
        Utils.DrawEllipticalOrbit(game.surface, draw_color_orbit, screen_parent_pos, orbitOnScreen, E, body['EccentricityAngle'],body['Bearing'], min_orbit)
        
      # check if we want to draw the object
      ################
      if (screen_body_pos[0] > -50 and screen_body_pos[1] > -50 and screen_body_pos[0] < game.width+50 and screen_body_pos[1] < game.height+50 ):
        pass
      else:
        body_draw_cond = False  
      if (body_draw_cond) and (orbitOnScreen > body_min_dist):
        # draw body
        if (body['Image'] is not None):
          if (screen_body_pos[0]-radius_on_screen < game.width and screen_body_pos[0]+radius_on_screen > 0 and 
              screen_body_pos[1]-radius_on_screen < game.height and screen_body_pos[1]+radius_on_screen > 0 ):
            scale = (radius_on_screen*2,radius_on_screen*2)
            if (scale[0] > 2*game.width):
              #todo: fix bug where the scaled surface moves when zooming in too much
              scale = (2*game.width,2*game.width)
            scaledSurface = pygame.transform.smoothscale(body['Image'],scale)
            image_offset = Utils.SubTuples(screen_body_pos,scaledSurface.get_rect().center)
            game.surface.blit(scaledSurface,image_offset)
        else:
          pygame.draw.circle(game.surface,draw_color_body,screen_body_pos,radius_on_screen,Utils.FILLED)
          
        # Make object clickable
        bb = (screen_body_pos[0]-radius_on_screen,screen_body_pos[1]-radius_on_screen,2*radius_on_screen,2*radius_on_screen)
        if (game.CheckClickableNotBehindGUI(bb)):
          game.MakeClickable(body['Name'], bb, left_click_call_back = game.Select_Body, par=bodyID)

        # Check if we want to draw the label
        draw_cond, draw_color_label, void, min_dist = GetDrawConditions(game, 'Label', body)
        if (draw_cond) and (orbitOnScreen > min_dist):
          labelPos = Utils.AddTuples(screen_body_pos, (0,radius_on_screen))

          if (game.highlighted_body_ID == bodyID):
            color = Utils.CYAN
          else:
            color = draw_color_label
          # draw the label
          Utils.DrawText2Surface(game.surface, body['Name'], labelPos, 14, color)


def GetDrawConditions(game, thing2Draw, body):
  draw = False
  color = (0,0,0)
  min_size = 5
  min_dist = 5
  if (body['Type'] == 'Stellar'):
    filter = False
  else:
    filter = (body['Colonized'] and game.showColonizedBodies) or (body['Resources'] and game.showResourcefulBodies) or (body['Industrialized'] and game.showIndustrializedBodies) or (body['Xenos'] and game.showXenosBodies)  or (body['Enemies'] and game.showEnemyBodies)  or (body['Unsurveyed'] and game.showUnsurveyedBodies) or (body['Artifacts'] and game.showArtifactsBodies)

  if (thing2Draw == 'Body'):
    if (body['Class'] == 'Moon'):
      if (game.show_Moons or filter):
        draw = True
        color = game.color_Moon
        min_size = game.minPixelSize_Moon
        min_dist = 10
    elif (body['Class']  == 'Comet'):
      if (game.show_Comets or filter):
        draw = True
        color = game.color_Comet
        min_size = game.minPixelSize_Small
        min_dist = 10
    elif (body['Class']  == 'Asteroid'):
      if (game.show_Asteroids or filter):
        draw = True
        color = game.color_Asteroid
        min_size = game.minPixelSize_Small
        min_dist = 10
    elif (body['Type'] == 'Planet Small'):
      if (game.show_DwarfPlanets or filter):
        draw = True
        color = game.color_DwarfPlanet
        min_size = game.minPixelSize_Planet
        min_dist = 10
    elif (body['Class'] == 'Planet' and body['Type'] != 'Planet Small' ):
      if (game.show_Planets or filter):
        draw = True
        color = game.color_Planet
        min_size = game.minPixelSize_Planet
        min_dist = 10
  elif (thing2Draw == 'Orbit'):
    if (body['Class'] == 'Moon'):
      if (game.showOrbits_Moons and (game.show_Moons or filter)):
        draw = True
        color = game.color_Orbit_Moon
        min_dist = 10
    elif (body['Class']  == 'Comet'):
      if (game.showOrbits_Comets and (game.show_Comets or filter)):
        draw = True
        color = game.color_Orbit_Comet
        min_dist = 10
    elif (body['Class']  == 'Asteroid'):
      if (game.showOrbits_Asteroids and (game.show_Asteroids or filter)):
        draw = True
        color = game.color_Orbit_Asteroid
        min_dist = 10
    elif (body['Type'] == 'Planet Small'):
      if (game.showOrbits_DwarfPlanets and (game.show_DwarfPlanets or filter)):
        draw = True
        color = game.color_Orbit_DwarfPlanet
        min_dist = 10
    elif (body['Class'] == 'Planet' and body['Type'] != 'Planet Small' ):
      if (game.showOrbits_Planets and (game.show_Planets or filter)):
        draw = True
        color = game.color_Orbit_Planet
        min_dist = 10
  elif (thing2Draw == 'Label'):
    if (body['Class'] == 'Moon'):
      if (game.showLabels_Moons and (game.show_Moons or filter)):
        draw = True
        color = game.color_Label_Moon
        min_dist = 50
    elif (body['Class']  == 'Comet'):
      if (game.showLabels_Comets and (game.show_Comets or filter)):
        draw = True
        color = game.color_Label_Comet
        min_dist = 200
    elif (body['Class']  == 'Asteroid'):
      if (game.showLabels_Asteroids and (game.show_Asteroids or filter)):
        draw = True
        color = game.color_Label_Asteroid
        min_dist = 200
    elif (body['Type'] == 'Planet Small'):
      if (game.showLabels_DwarfPlanets and (game.show_DwarfPlanets or filter)):
        draw = True
        color = game.color_Label_DwarfPlanet
        min_dist = 5
    elif (body['Class'] == 'Planet' and body['Type'] != 'Planet Small' ):
      if (game.showLabels_Planets and (game.show_Planets or filter)):
        draw = True
        color = game.color_Label_Planet
        min_dist = 5
  return draw, color, min_size, min_dist
