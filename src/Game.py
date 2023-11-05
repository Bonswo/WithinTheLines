import pygame, sys, random
from pygame.locals import *

from .AudioManager import AudioManager
from .RenderManager import RenderManager
from .BoundingBox import BoundingBox

class Game:
    display_size = (1000, 1000)
    initial_time_limit = 2000
    overshoot_protection_time = 200

    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        pygame.font.init()
        
        self.clock = pygame.time.Clock()
        self.render_manager = RenderManager(self.clock, (1000, 1000))
        self.audio_manager = AudioManager()
        self.dt = 0
        self.current_time_limit = Game.initial_time_limit
        self.timer = Game.initial_time_limit
        self.prev_mpos = pygame.mouse.get_pos()
        self.overshoot_protection = 0

        self.running = True
        self.game_state = 0
        self.high_score = 0
        self.score = 0
        self.death_type = 0
        self.level = 0

        self.bounding_box = None
        self.set_new_bounding_box = False
    
    def run(self):
        while self.running:
            self.main()
    
    def quit(self):
        self.running = False
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

    def on_loss(self):
        self.game_state = 2
        self.render_manager.on_loss()
        self.audio_manager.on_loss()
    
    def on_score(self):
        self.score += 1
        self.set_new_bounding_box = True
        
        self.overshoot_protection = Game.overshoot_protection_time
        if self.score % 10 == 0:
            self.current_time_limit = max(self.current_time_limit - 250, 250)
            self.level += 1 if self.level < 4 else 0
        self.timer = self.current_time_limit

        self.render_manager.on_score()
        self.audio_manager.on_score()
        
    def start_new_game(self):
        self.game_state = 1
        self.score = 0
        self.bounding_box = None
        self.set_new_bounding_box = True
        self.timer = Game.initial_time_limit
        self.current_time_limit = Game.initial_time_limit
        self.death_message = None
        self.level = 0

        self.render_manager.on_new_game()
        self.audio_manager.on_new_game()

    def main(self):
        self.dt = self.clock.tick(144) # milliseconds
        mpos = pygame.mouse.get_pos()

        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self.quit()

        if self.game_state == 0: # menu
            for event in events:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.start_new_game()
            self.render_manager.render_menu(self.get_info())
        
        if self.game_state == 1: # Game
            for event in events:
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    self.on_loss()
                    self.death_type = 0
            
            if self.timer <= 0:
                self.on_loss()
                self.death_type = 2
        
            if self.set_new_bounding_box:
                self.set_new_bounding_box = False
                start_pos = self.bounding_box.end if self.bounding_box else pygame.mouse.get_pos()

                max_x, max_y = self.render_manager.display_size
                end_x = random.randint(100, max_x - 100)
                end_y = random.randint(100, max_y - 100)
                self.bounding_box = BoundingBox(start_pos, (end_x, end_y))

            if not self.bounding_box.point_inside_box(mpos) and self.overshoot_protection == 0: # point outside box sadge
                self.on_loss()
                self.death_type = 1
        
            if self.bounding_box.point_distance_to_end(mpos) <=0:
                self.on_score()

            self.render_manager.render_game(self.get_info())
        
        if self.game_state == 2: # score screen
            for event in events:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.game_state = 0
            self.render_manager.render_score(self.get_info())

        self.prev_mpos = mpos
        self.timer = max(self.timer - self.dt, 0)
        self.overshoot_protection = max(self.overshoot_protection - self.dt, 0)

    def get_info(self):
        return {
            'bounding_box' : self.bounding_box.get_info() if self.bounding_box else None,
            'level' : self.level,
            'time limit' : self.current_time_limit,
            'time' : self.timer,
            'score' : self.score,
            'dt' : self.dt,
            'death type' : self.death_type
        }