
import pygame, sys, random, numpy, math
from pygame.locals import *
from perlin_noise import PerlinNoise

SEPIA = (229,208,157)
ORANGE = (221,141,76)
BROWN = (180,93,63)
LIGHT_BROWN = (196, 164, 132)
BABY_BLUE = (176,205,227)
BLUE_BLACK = (35,40,60)
LIGHT_RED = (208,59,59)

class Game:
    display_size = (1000, 1000)
    initial_time_limit = 2000
    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        pygame.font.init()
        self.window = pygame.display.set_mode((1000,1000))
        self.display = pygame.Surface(Game.display_size)
        self.score_font = pygame.font.Font('Oswald.ttf', 600)
        self.title_font = pygame.font.Font('Oswald.ttf', 150)
        self.info_font = pygame.font.Font('Oswald.ttf', 90)
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.current_time_limit = Game.initial_time_limit
        self.timer = Game.initial_time_limit
        self.particle_manager = ParticleManager()
        self.prev_mpos = (0, 0)
        

        self.running = True
        self.game_state = 0
        self.high_score = 0
        self.score = 0
        self.screen_shake = 0
        self.screen_shake_strength = 5

        self.line_segments = []
        self.bounding_box = None
        self.set_new_bounding_box = False
        self.previous_mpos = None

        pygame.mixer.music.load('MDK - Press Start.mp3')
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.1)
        self.sound_hit1 = pygame.mixer.Sound('hit1.wav')
        self.sound_hit1.set_volume(0.2)
        self.sound_start = pygame.mixer.Sound('start.mp3')
        self.sound_hit2 = pygame.mixer.Sound('hit2.wav')
        self.sound_hit2.set_volume(0.2)
        self.sound_loss = pygame.mixer.Sound('explosion.wav')
        self.sound_loss.set_volume(0.2)

    def run(self):
        while self.running:
            self.main()
    
    def quit(self):
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

    def on_loss(self):
        self.particle_manager.spawn_death_particles(pygame.mouse.get_pos(), 50)
        self.screen_shake = 350
        self.screen_shake_strength = 15
        pygame.mixer.Sound.play(self.sound_loss)
        if self.score > self.high_score:
            print(f"NEW HIGH SCORE: {self.score}")
        else:
            print(f"SCORE: {self.score}")
            print(f"HIGH SCORE: {self.high_score}")
    
    def on_score(self):
        self.score += 1
        self.set_new_bounding_box = True
        self.particle_manager.bulk_spawn(pygame.mouse.get_pos(), 20)
        self.screen_shake = 150
        self.screen_shake_strength = 5
        pygame.mixer.Sound.play(random.choice([self.sound_hit2]))
        if self.score % 10 == 0:
            self.current_time_limit = max(self.current_time_limit - 250, 250)
            pass
        self.timer = self.current_time_limit

    def main(self):
        self.dt = self.clock.tick(60) # milliseconds

        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self.quit()
            
        # Pre-game 
        if self.game_state == 0:
            self.prev_mpos = pygame.mouse.get_pos()
            for event in events:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    #start game
                    print('Game start')
                    self.game_state = 1
                    self.score = 0
                    self.set_new_bounding_box = True
                    self.timer = Game.initial_time_limit
                    self.current_time_limit = Game.initial_time_limit
                    pygame.mixer.Sound.play(self.sound_start)
                    pygame.mouse.set_visible(False)
            self.render_menu()
        
        # Game
        if self.game_state == 1:
            for event in events:
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    self.on_loss()
                    print('let go of buton sadge')
                    self.game_state = 2
            
            if self.timer <= 0:
                self.on_loss()
                print('Ran out of time :(')
                self.game_state = 2
        
            if self.set_new_bounding_box:
                self.set_new_bounding_box = False
                self.bounding_box = BoundingBox()

            

            mpos = pygame.mouse.get_pos()
            dist_to_line = self.bounding_box.min_distance_to_point(mpos)
            x0, y0 = self.bounding_box.start
            x1, y1 = mpos
            dist_to_start = math.sqrt((y1-y0)**2+(x1-x0)**2)
            self.particle_manager.spawn_mouse_trail(self.prev_mpos)
            if dist_to_line > 0 and dist_to_start > 20: # point outside box sadge
                self.on_loss()
                print('mouse outside box sadge')
                self.game_state = 2
        
            dist_to_end = self.bounding_box.point_distance_to_end(mpos)
            if dist_to_end <=0:
                self.on_score()

            self.prev_mpos = mpos
            self.render_game()
        
            
        # Post-game
        if self.game_state == 2:
            self.prev_mpos = pygame.mouse.get_pos()
            for event in events:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    print('main menu')
                    self.game_state = 0
            self.render_score()

        self.timer -= max(self.dt, 0)
        self.screen_shake -= max(self.dt, 0)
        return
    
    @staticmethod
    def basic_render(sub_render):
        def new_render(self, *args, **kwargs):
            self.window.fill(SEPIA)
            self.display.fill(SEPIA)

            sub_render(self, *args, **kwargs)
            
            self.particle_manager.render_particles(self.display, self.dt)
            pygame.draw.circle(self.display,
                           BLUE_BLACK,
                           pygame.mouse.get_pos(),
                           10)
            if self.screen_shake > 0:
                self.window.blit(self.display, (random.randint(-5, 5), random.randint(-5, 5)))
            else:
                self.window.blit(self.display, (0, 0))
            pygame.display.flip()

        return new_render

    @basic_render
    def render_game(self):

        score_text = pygame.Font.render(self.score_font, str(self.score), True, LIGHT_BROWN)
        w, h = score_text.get_size()
        self.display.blit(score_text, (Game.display_size[0]/2 - w/2, 
                                       Game.display_size[1]/2 - h/2))

        # bounding_box_points = get_polyline_points(self.bounding_box.start, self.bounding_box.end, self.bounding_box.width)
        #dist from end
        x0, y0 = self.bounding_box.start
        x1, y1 = self.bounding_box.end
        #percent left
        percent_progressed = self.timer / self.current_time_limit
        x2 = percent_progressed * (x1-x0) + x0
        y2 = percent_progressed * (y1-y0) + y0
        pygame.draw.line(self.display, 
                         ORANGE, 
                         self.bounding_box.start, self.bounding_box.end,
                         width=self.bounding_box.width)
        pygame.draw.line(self.display, 
                         LIGHT_RED, 
                         (x2, y2), self.bounding_box.end,
                         width=self.bounding_box.width)
        pygame.draw.circle(self.display,
                           LIGHT_RED,
                           self.bounding_box.end,
                           self.bounding_box.width/2)
        


    @basic_render
    def render_menu(self):
        title_text = pygame.Font.render(self.title_font, 'WITHIN THE LINES', True, LIGHT_BROWN)
        w, h = title_text.get_size()
        self.display.blit(title_text, (Game.display_size[0]/2 - w/2, 
                                       Game.display_size[1]/2 - h/2))
        info_text = pygame.Font.render(self.info_font, 'HOLD M1 TO PLAY', True, LIGHT_BROWN)
        w, h = info_text.get_size()
        self.display.blit(info_text, (Game.display_size[0]/2 - w/2, 
                                       3* Game.display_size[1]/4 - h/2))
        pass
    
    @basic_render
    def render_score(self):
        score_text = pygame.Font.render(self.score_font, str(self.score), True, LIGHT_BROWN)
        w, h = score_text.get_size()
        self.display.blit(score_text, (Game.display_size[0]/2 - w/2, 
                                       Game.display_size[1]/2 - h/2))
    
        info_text = pygame.Font.render(self.info_font, 'M1 TO CONTINUE', True, LIGHT_BROWN)
        w, h = info_text.get_size()
        self.display.blit(info_text, (Game.display_size[0]/2 - w/2, 
                                       6* Game.display_size[1]/7 - h/2))
        # hs_text = pygame.Font.render(self.title_font, f'{self.high_score}', True, LIGHT_BROWN)
        # w, h = hs_text.get_size()
        # self.display.blit(hs_text, (Game.display_size[0]/2 - w/2, 
        #                                2* Game.display_size[1]/7 - h/2))
        pass

class BoundingBox():
    def __init__(self, width=100) -> None:
        self.width = width
        self.start = pygame.mouse.get_pos()
        self.end = (random.randint(width, Game.display_size[0]-width), 
                    random.randint(width, Game.display_size[1]-width))
    
    def min_distance_to_point(self, point):
        x1, y1 = self.start
        x2, y2 = self.end
        x0, y0 = point
        nominator = abs((x2 - x1)*(y1-y0)-(x1-x0)*(y2-y1))
        denominator = numpy.sqrt((x2-x1)**2+(y2-y1)**2)
        distance = nominator/denominator - self.width/2
        return distance

    def point_distance_to_end(self, point):
        x0, y0 = point
        x1, y1 = self.end
        distance = numpy.sqrt(abs((y1-y0)**2+(x1-x0)**2)) - self.width/2

        return distance

class Particle():
    def __init__(self, position):
        self.velocity = (random.randint(-40, 40)/100,
                         random.randint(-40, 40)/100)
        self.decay_timer = random.randint(100, 500) # milliseconds
        self.radius = random.randint(20, 40)
        self.position = list(position)
        self.destroy = False
    
    def render(self, surface, dt):
        self.position[0] += self.velocity[0]*dt
        self.position[1] += self.velocity[1]*dt
        pygame.draw.circle( surface, 
                            BROWN,
                            self.position,
                            self.radius)
        self.decay_timer -= dt
        self.radius -= 50 * dt/1000
        if self.decay_timer <= 0 or self.radius <= 1:
            self.destroy = True

class DeathParticle():
    def __init__(self, position):
        self.velocity = [random.randint(-80, 80)/100,
                         random.randint(-80, 80)/100]
        self.decay_timer = random.randint(300, 700) # milliseconds
        self.radius = random.randint(20, 40)
        self.position = list(position)
        self.gravity = 5
        self.destroy = False
    
    def render(self, surface, dt):
        self.position[0] += self.velocity[0]*dt
        self.position[1] += self.velocity[1]*dt
        pygame.draw.circle( surface, 
                            LIGHT_RED,
                            self.position,
                            self.radius)
        self.decay_timer -= dt
        self.radius -= 50 * dt/1000
        self.velocity[1] += self.gravity * dt/1000
        if self.decay_timer <= 0 or self.radius <= 1:
            self.destroy = True

class MouseTrailParticle():
    initial_duration = 100
    def __init__(self, start, end):
        self.duration = MouseTrailParticle.initial_duration
        self.start = start
        self.end = end
        self.destroy = False
        self.alpha = 255
        self.width = 20

    def render(self, surface, dt):
        polygon_points = get_polyline_points(self.start, self.end, self.width)
        # pygame.draw.polygon(surface, BLUE_BLACK, polygon_points)
        pygame.draw.line(surface, BLUE_BLACK, self.start, self.end, round(self.width))
        self.duration -= dt
        self.width -=  dt * 20/MouseTrailParticle.initial_duration
        if self.duration <= 0 or self.alpha <= 0:
            self.destroy = True

    

class ParticleManager():
    def __init__(self):
        self.particles = []
        self.mouse_trail = []
    
    def render_particles(self, surface, dt):

        for particle in self.particles:
            particle.render(surface, dt)
        self.particles = [x for x in self.particles if not x.destroy]

        for particle in self.mouse_trail:
            particle.render(surface, dt)
        self.mouse_trail = [x for x in self.mouse_trail if not x.destroy]
    
    def clear_particles(self):
        self.particles = []
    
    def bulk_spawn(self, position, count):
        for _ in range(count):
            self.particles.append(Particle(position))
    
    def spawn_death_particles(self, position, count):
        for _ in range(count):
            self.particles.append(DeathParticle(position))

    def spawn_mouse_trail(self, start):
        self.mouse_trail.append(MouseTrailParticle(start, pygame.mouse.get_pos()))


def get_polyline_points(start, end, width):
    x0, y0 = start
    x1, y1 = end
    if x1 - x0 == 0:
        m0 = 9999
    elif y1-y0 == 0:
        m0 = 0.000000001
    else:
        m0 = y1-y0 / x1-x0

    rad_angle = math.atan(-1/m0)
    p1 = (x0 + math.cos(rad_angle) * width/2, y0 - math.sin(rad_angle) * width/2)
    p2 = (x0 - math.cos(rad_angle) * width/2, y0 + math.sin(rad_angle) * width/2)
    
    p3 = (x1 + math.cos(rad_angle) * width/2, y1 - math.sin(rad_angle) * width/2)
    p4 = (x1 - math.cos(rad_angle) * width/2, y1 + math.sin(rad_angle) * width/2)
    return (p1, p2, p3, p4)


game = Game()
game.run()