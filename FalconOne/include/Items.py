import pygame
from include import Base

STD_ITEM_SIZE = 20

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, scale, vel):
        pygame.sprite.Sprite.__init__(self)
        self.pos    = list(pos)
        self.vel    = list(vel)
        self.scale  = scale

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        if self.rect.top > Base.HEIGHT:
            self.kill()

        elif self.rect.left > Base.WIDTH or self.rect.right < 0 or self.rect.bottom < 0:
            self.kill()

    def get_rect(self):
        return self.image.get_rect()

class Life(Item):
    def __init__(self, pos, scale, value, vel = [0, 2]):
        Item.__init__(self, pos, scale, vel)

        self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Items/Life.png"), (scale, scale))
        self.value          = value
        self.rect           = self.image.get_rect()
        self.rect.centerx   = pos[0]
        self.rect.centery   = pos[1]

    def apply(self, player):
        player.lives += self.value

class Bomb(Item):
    def __init__(self, pos, scale, value, vel = [0, 2]):
        Item.__init__(self, pos, scale, vel)

        self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Items/Bomb.png"), (scale, scale))
        self.value          = value
        self.rect           = self.image.get_rect()
        self.rect.centerx   = pos[0]
        self.rect.centery   = pos[1]

    def apply(self, player):
        player.bombs += self.value

class Point(Item):
    def __init__(self, pos, scale, value, vel = [0, 2]):
        Item.__init__(self, pos, scale, vel)

        self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Items/Point.png"), (scale, scale))
        self.value          = value
        self.rect           = self.image.get_rect()
        self.rect.centerx   = pos[0]
        self.rect.centery   = pos[1]
        self.game_state     = Base.STD_GAME_STATE

    def apply(self, player):
        self.game_state.points += self.value

class Upgrade(Item):
    def __init__(self, pos, scale, vel = [0, 2]):
        Item.__init__(self, pos, scale, vel)

        self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Items/Upgrade.png"), (scale, scale))
        self.rect           = self.image.get_rect()
        self.rect.centerx   = pos[0]
        self.rect.centery   = pos[1]

    def apply(self, player):
        player.upgrade_weapon(1)
