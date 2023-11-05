import pygame, random
from .Util import get_polyline_points
from .ParticleManager import ParticleManager

SEPIA = (229,208,157)
ORANGE = (221,141,76)
BROWN = (180,93,63)
LIGHT_BROWN = (196, 164, 132)
BLUE_BLACK = (35,40,60)
LIGHT_RED = (208,59,59)

class RenderManager():
    def __init__(self, clock, display_size=(1000,1000)):
        pygame.mouse.set_visible(False)
        self.clock = clock # do not tick the clock. Just get_time()
        self.particle_manager = ParticleManager()
        self.window = pygame.display.set_mode(display_size)
        self.display = pygame.Surface(display_size)
        self.display_size = display_size

        self.screenshake = 0
        self.screenshake_strength = 5
        self.death_message = None

        self.score_font = pygame.font.Font('data/Oswald.ttf', 600)
        self.title_font = pygame.font.Font('data/Oswald.ttf', 150)
        self.info_font = pygame.font.Font('data/Oswald.ttf', 90)

    def add_screenshake(self, duration, strength):
        self.screenshake = duration
        self.screenshake_strength = strength

    def on_score(self):
        self.particle_manager.bulk_spawn(pygame.mouse.get_pos(), 20)
        self.add_screenshake(150, 10)
    
    def on_loss(self):
        self.particle_manager.spawn_death_particles(pygame.mouse.get_pos(), 40)
        self.add_screenshake(350, 15)

    def on_new_game(self):
        self.add_screenshake(150, 15)

    @staticmethod
    def basic_render(sub_render):
        def new_render(self, game_info, *args, **kwargs):
            dt = self.clock.get_time()
            self.window.fill(SEPIA)
            self.display.fill(SEPIA)

            sub_render(self, game_info, *args, **kwargs)
            
            self.particle_manager.render_particles(self.display, dt)
            # level_colour = Game.level_colours[self.level]
            self.particle_manager.spawn_mouse_trail(BLUE_BLACK) # level_colour)
            pygame.draw.circle(self.display, BLUE_BLACK, pygame.mouse.get_pos(), 10)

            if self.screenshake > 0:
                displacement_x = random.randint(-self.screenshake_strength, self.screenshake_strength)
                displacement_y = random.randint(-self.screenshake_strength, self.screenshake_strength)
            else:
                displacement_x = 0
                displacement_y = 0

            self.window.blit(self.display, (displacement_x, displacement_y))
            self.screenshake = max(self.screenshake - dt, 0)
            pygame.display.flip()
        return new_render
    
    @basic_render
    def render_game(self, game_info):
        score = game_info['score']
        score_text = pygame.Font.render(self.score_font, str(score), True, LIGHT_BROWN)
        w, h = score_text.get_size()
        self.display.blit(score_text, (self.display_size[0]/2 - w/2, self.display_size[1]/2 - h/2))

        bounding_box_info = game_info['bounding_box']
        bb_start = bounding_box_info['start']
        bb_end = bounding_box_info['end']
        bb_points = bounding_box_info['points']
        bb_width = bounding_box_info['width']
        bb_hwidth = bb_width/2
        pygame.draw.polygon(self.display, ORANGE, bb_points)
        pygame.draw.circle(self.display, ORANGE, bb_start, bb_hwidth)

        time = game_info['time']
        time_limit = game_info['time limit']
        x0, y0 = bb_start
        x1, y1 = bb_end
        percent_progressed = time / time_limit
        x2 = percent_progressed * (x1-x0) + x0
        y2 = percent_progressed * (y1-y0) + y0
        progress_box_points = get_polyline_points((x2,y2), bb_end, bb_width)
        pygame.draw.polygon(self.display, LIGHT_RED, progress_box_points)
        pygame.draw.circle(self.display, LIGHT_RED, (x2,y2), bb_hwidth)

        pygame.draw.circle(self.display, SEPIA, bb_end, bb_hwidth + 10)
        pygame.draw.circle(self.display, LIGHT_RED, bb_end, bb_hwidth)
        pygame.draw.circle(self.display, BLUE_BLACK, bb_end, bb_hwidth + 10, width=5)

    @basic_render
    def render_menu(self, game_info):
        title_text = pygame.Font.render(self.title_font, 'WITHIN THE LINES', True, LIGHT_BROWN)
        w, h = title_text.get_size()
        self.display.blit(title_text, (self.display_size[0]/2 - w/2, 
                                       self.display_size[1]/2 - h/2))
        info_text = pygame.Font.render(self.info_font, 'HOLD M1 TO PLAY', True, LIGHT_BROWN)
        w, h = info_text.get_size()
        self.display.blit(info_text, (self.display_size[0]/2 - w/2, 
                                       3* self.display_size[1]/4 - h/2))
        pass
    
    @basic_render
    def render_score(self, game_info):
        score = game_info['score']
        death_type = game_info['death type']
        score_text = pygame.Font.render(self.score_font, str(score), True, LIGHT_BROWN)
        w, h = score_text.get_size()
        self.display.blit(score_text, (self.display_size[0]/2 - w/2, 
                                       self.display_size[1]/2 - h/2))
    
        info_text = pygame.Font.render(self.info_font, 'M1 TO CONTINUE', True, LIGHT_BROWN)
        w, h = info_text.get_size()
        self.display.blit(info_text, (self.display_size[0]/2 - w/2, 
                                       6* self.display_size[1]/7 - h/2))
        
        death_messages = {
            0 : ["Don't let go!", "You let go...", 'Hold M1!'],
            2 : ['Faster!', "Too slow...", "Slowpoke!", "Not fast enough..."],
            1 : ['Inside the lines!', 'Where are you going?!', 'Maybe slow down :)', 'Bad aim gitgud']
        }

        if not self.death_message:
            self.death_message = random.choice(death_messages[death_type])
        death_text = pygame.Font.render(self.info_font, self.death_message, True, LIGHT_BROWN)
        w, h = death_text.get_size()
        self.display.blit(death_text, (self.display_size[0]/2 - w/2, 
                                       1* self.display_size[1]/7 - h/2))