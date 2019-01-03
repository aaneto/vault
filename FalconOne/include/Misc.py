import pygame
import Base

class Misc(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    def kill(self, opt = None):
        pygame.sprite.Sprite.kill(self)

class Asteroid(Misc):
    def __init__(self, pos, size, vel):
        Misc.__init__(self)
        self.image          = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/asteroide.jpg"), (scale, scale))
        self.rect           = self.image.get_rect()
        self.size           = list(size)
        self.vel            = list(vel)
        self.rect.centerx   = pos[0]
        self.rect.centery   = pos[1]

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        if self.rect.left > Base.WIDTH or self.rect.right < 0 or self.rect.top > Base.HEIGHT or self.rect.bottom < 0:
            self.kill()

    def get_rect(self):
        return self.image.get_rect()

class Explosion(Misc):
    def __init__(self, pos, scale):
        Misc.__init__(self)
        self.delta = 0
        self.time_acc = 0

        self.explosion_imgs = []
        self.explosion_imgs.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Animations/Explosion/1.png"), (scale, int(1.5 * scale))))
        self.explosion_imgs.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Animations/Explosion/2.png"), (scale, int(1.5 * scale))))
        self.explosion_imgs.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Animations/Explosion/3.png"), (scale, int(1.5 * scale))))
        self.explosion_imgs.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Animations/Explosion/4.png"), (scale, int(1.5 * scale))))
        self.explosion_imgs.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Animations/Explosion/5.png"), (scale, int(1.5 * scale))))
        self.explosion_imgs.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Animations/Explosion/6.png"), (scale, int(1.5 * scale))))
        self.img_idx = 0
        self.image = self.explosion_imgs[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        self.delta += 30
        self.time_acc += 30

        if self.time_acc > 700:
            self.kill()

        if self.delta > 90:
            self.img_idx = (self.img_idx + 1) % len(self.explosion_imgs)
            self.image = self.explosion_imgs[self.img_idx]
            self.delta = 0

    def kill(self, opt=None):
        if opt != -1:
            Misc.kill(self)
