import pygame
from .Particles import ScoreParticle, DeathParticle, MouseTrailParticle

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
            self.particles.append(ScoreParticle(position))
    
    def spawn_death_particles(self, position, count):
        for _ in range(count):
            self.particles.append(DeathParticle(position))

    def spawn_mouse_trail(self, colour):
        start = pygame.mouse.get_pos()
        if len(self.mouse_trail) > 0:
            start = self.mouse_trail[-1].end
        self.mouse_trail.append(MouseTrailParticle(start, pygame.mouse.get_pos(), colour))