import pygame
import Base
import math

BULLET_WIDTH    = Base.WIDTH // 40
BULLET_SPEED    = 3

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, scale, vel, game_state, kind = 0):
        pygame.sprite.Sprite.__init__(self)

        if kind == 0:
            self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Bullets/Purple.png"), (scale, scale))
        elif kind == 1:
            self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Bullets/DarkBlue.png"), (scale, scale))
        elif kind == 2:
            self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Grey.png"), (scale, scale))
        elif kind == 3:
            self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/PinkRed.png"), (scale, scale))
        elif kind == 4:
            self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Blue.png"), (scale, scale))
        else:
            self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Bullets/Purple.png"), (scale, scale))




        self.rect           = self.image.get_rect()
        self.rect.centerx   = pos[0]
        self.rect.centery   = pos[1]
        self.rect.width /= 5
        self.rect.height /= 5

        self.pos = [float(self.rect.centerx), float(self.rect.centery)]
        self.vel            = vel
        self.game_state     = game_state

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        self.rect.centerx = int(self.pos[0])
        self.rect.centery = int(self.pos[1])

        if self.rect.top > 1.4 * Base.HEIGHT:
            self.game_state.points += 10
            self.kill()

        elif self.rect.left > Base.WIDTH or self.rect.right < 0 or self.rect.bottom < 0:
            self.kill()

    def get_rect(self):
        return self.image.get_rect()

class FollowingBullet(Bullet):
    def __init__(self, pos, scale, vel, game_state, kind = 1):
        Bullet.__init__(self, pos, scale, vel, game_state, kind)

    def update(self):
        if self.rect.x - self.game_state.player.rect.x > abs(self.vel[0]):
            self.rect.x -= abs(self.vel[0])
        elif self.rect.x - self.game_state.player.rect.x < abs(self.vel[0]):
            self.rect.x += abs(self.vel[0])
        self.rect.y += self.vel[1]

        if self.rect.top > 2 * Base.HEIGHT:
            self.game_state.points += 10
            self.kill()

        elif self.rect.left > Base.WIDTH or self.rect.right < 0 or self.rect.bottom < 0:
            self.kill()

class RocketBullet(Bullet):
    def __init__(self, pos, scale, vel, game_state, bullet_group, kind = 0):
        Bullet.__init__(self, pos, scale, vel, game_state, kind)
        self.image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/ExplosiveBullet.png"), (scale, 3*scale))
        self.delta = 500
        self.bullet_group = bullet_group
        self.bursted = False

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        self.delta -= 35

        if self.delta < 0 and not self.bursted:
            self.explode(10)
            self.bursted = True
            self.delta = 400

        elif self.delta < 0:
            self.explode(12)
            self.kill()

        if self.rect.top > 2 * Base.HEIGHT:
            self.game_state.points += 10
            self.kill()

        elif self.rect.left > Base.WIDTH or self.rect.right < 0 or self.rect.bottom < 0:
            self.kill()

    def explode(self, n):
        angle = 0

        for i in range(n):
            angle += math.pi / (n // 2)
            vel_x = BULLET_SPEED * math.cos(angle)
            vel_y = BULLET_SPEED * math.sin(angle)
            self.bullet_group.add(Bullet(self.rect.center, BULLET_WIDTH, (vel_x, vel_y), self.game_state))

class HellBullet(Bullet):
    def __init__(self, pos, scale, vel, game_state, kind = 0):
        Bullet.__init__(self, pos, scale, vel, game_state, kind)
        self.image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Bullets/MedBlue.png"), (scale, scale))

class PlayerBullet(Bullet):
    def __init__(self, pos, scale, vel, game_state, kind = 0):
        Bullet.__init__(self, pos, scale, vel, game_state, kind)
        self.image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Bullets/LightBlue.png"), (scale, scale))

class SpringBullet(Bullet):
    def __init__(self, pos, scale, vel, game_state, kind = 0):
        Bullet.__init__(self, pos, scale, vel, game_state, kind)
        self.image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Peridot.png"), (scale, scale))
        self.time_life  = 0
        self.duration   = 9000

    def update(self):
        self.time_life += 30

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        self.rect.centerx = int(self.pos[0])
        self.rect.centery = int(self.pos[1])

        if self.time_life > self.duration:
            self.game_state.points += 100
            self.kill()

        if self.rect.top > Base.HEIGHT:
            self.rect.top = Base.HEIGHT
            self.vel[1] *= -1
        elif self.rect.bottom < 0:
            self.rect.bottom = 0
            self.vel[1] *= -1
        if self.rect.right < 0:
            self.rect.right = 0
            self.vel[0] *= -1
        elif self.rect.left > Base.WIDTH:
            self.rect.left = Base.WIDTH
            self.vel[0] *= -1

class ShortSpringBullet(SpringBullet):
    def __init__(self, pos, scale, vel, game_state, kind = 0):
        Bullet.__init__(self, pos, scale, vel, game_state, kind)
        self.image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Peridot.png"), (scale, scale))
        self.time_life  = 0
        self.duration   = 4000
