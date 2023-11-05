import random, pygame

ORANGE = (221,141,76)
BROWN = (180,93,63)
BLUE_BLACK = (35,40,60)
LIGHT_RED = (208,59,59)

# this is messy and needs to be better structured

class ScoreParticle():
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
        pygame.draw.circle(surface, BROWN, self.position, self.radius)
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
    def __init__(self, start, end, colour):
        self.duration = MouseTrailParticle.initial_duration
        self.start = start
        self.end = end
        self.destroy = False
        self.alpha = 255
        self.width = 20
        self.colour = colour

    def render(self, surface, dt):
        pygame.draw.line(surface, self.colour, self.start, self.end, round(self.width))
        self.duration -= dt
        self.width -=  dt * 20/MouseTrailParticle.initial_duration
        if self.duration <= 0 or self.alpha <= 0:
            self.destroy = True  