import pygame
class AudioManager():
    def __init__(self):
        pygame.mixer.music.load('data/MDK - Press Start.mp3')
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.1)

        self.sound_start = pygame.mixer.Sound('data/start.mp3')
        self.sound_hit2 = pygame.mixer.Sound('data/hit2.wav')
        self.sound_hit2.set_volume(0.2)
        self.sound_loss = pygame.mixer.Sound('data/explosion.wav')
        self.sound_loss.set_volume(0.2)

    def on_loss(self):
        pygame.mixer.Sound.play(self.sound_loss)
    
    def on_new_game(self):
        pygame.mixer.Sound.play(self.sound_start)

    def on_score(self):
        pygame.mixer.Sound.play(self.sound_hit2)
