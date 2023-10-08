from include import Base
from include.Bullets import PlayerBullet, SpringBullet, BULLET_WIDTH

import pygame
import math

PLAYER_BULLET_SPEED = 12

class PlayerShip(pygame.sprite.Sprite):
    def __init__(self, pos, scale):
       pygame.sprite.Sprite.__init__(self)
       self.image       = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Player.png"), (scale, int(1.5 * scale)))
       self.shield_image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/ShieldOn.png"), (scale, int(1.5 * scale)))
       self.place_holder= pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Bullets/MedBlue.png"), (scale, int(1.5 * scale)))
       self.shift_up = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/PlayerShift.png"), (scale, int(1.5 * scale)))
       self.std_image   = self.image
       self.rect        = self.image.get_rect()
       self.game_state  = Base.STD_GAME_STATE
       self.img_idx     = 0
       self.images      = []
       self.bomb_images = []
       self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Explosion/1.png"), (scale, int(1.5 * scale))))
       self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Explosion/2.png"), (scale, int(1.5 * scale))))
       self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Explosion/3.png"), (scale, int(1.5 * scale))))
       self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Explosion/4.png"), (scale, int(1.5 * scale))))
       self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Explosion/5.png"), (scale, int(1.5 * scale))))
       self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Explosion/6.png"), (scale, int(1.5 * scale))))
       self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Explosion/7.png"), (scale, int(1.5 * scale))))
       self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Explosion/8.png"), (scale, int(1.5 * scale))))
       self.bomb_images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Bomb/1.png"), (scale, int(1.5 * scale))))
       self.bomb_images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Bomb/2.png"), (scale, int(1.5 * scale))))
       self.bomb_images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Bomb/3.png"), (scale, int(1.5 * scale))))
       self.bomb_images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Player/Bomb/4.png"), (scale, int(1.5 * scale))))

    def update(self, player_rect):
        self.rect.centerx = player_rect.centerx
        self.rect.centery = player_rect.centery

        if self.game_state.player.burning > 0:
            self.img_idx = (self.img_idx + 1) % len(self.images)
            self.image = self.images[self.img_idx]
        elif self.game_state.player.shield > 0:
            self.image = self.shield_image
        elif self.game_state.player.onSlowdown:
            self.image = self.shift_up
        elif self.game_state.player.bomb_anim > 0:
            self.img_idx = (self.img_idx + 1) % len(self.bomb_images)
            self.image = self.bomb_images[self.img_idx]
        else:
            self.image = self.std_image

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, scale, cadency, bullet_group, firing = Base.DUAL_FIRE):
        pygame.sprite.Sprite.__init__(self)

        self.std_img        = pygame.image.load(Base.STD_PATH + "res/Player/Hitbox.png")
        self.image          = self.std_img
        self.rect           = self.image.get_rect()
        self.rect.centerx   = pos[0]
        self.rect.centery   = pos[1]
        self.firing         = firing
        self.delta          = 0
        self.cadency        = cadency
        self.isFiring       = False
        self.lives          = 3
        self.shield         = 1
        self.bullet_group   = bullet_group
        self.onSlowdown     = False
        self.game_state     = Base.STD_GAME_STATE
        self.burning        = 0
        self.bomb_anim      = 0
        self.bombs          = 3
        self.total_bombs    = 3
        self.shooting_song = effect = pygame.mixer.Sound(Base.STD_PATH + 'res/Music/single-fire.wav')
        self.shooting_song.set_volume(0.1)

    def upgrade_weapon(self, value):
        if self.firing != Base.SPECIAL_FIRE:
            self.firing = self.firing + value

    def startFiring(self):
        self.isFiring = True

    def stopFiring(self):
        self.isFiring = False

    def startSlowdown(self):
        self.onSlowdown = True

    def stopSlowdown(self):
        self.onSlowdown = False

    def update(self, vel):
        if self.bomb_anim > 0:
            self.bomb_anim -= 1
        else:
            self.bomb_anim = 0


        if self.burning > 0:
            self.burning -= 1.0 / 40
            if self.burning < 0:
                self.burning = 0
                self.shield = 1
                self.rect.center = (Base.WIDTH/2, Base.HEIGHT - 50)
            else:
                return 0

        if self.delta > 0:
            self.delta -= 1.0 / 40
        else:
            self.delta = 0

        if self.isFiring and self.delta == 0:
            self.fire()
            self.delta = self.cadency

        if self.shield > 0:
            self.shield -= 1.0 / 40
        else:
            self.shield = 0

        if self.onSlowdown:
            self.rect.x += vel[0] / 2
            self.rect.y += vel[1] / 2

        else:
            self.rect.x += vel[0]
            self.rect.y += vel[1]

        if self.rect.right > Base.WIDTH:
            self.rect.right = Base.WIDTH

        elif self.rect.left < 0:
            self.rect.left = 0

        if self.rect.bottom > Base.HEIGHT:
            self.rect.bottom = Base.HEIGHT

        elif self.rect.top < 0:
            self.rect.top = 0

    def fire(self):
        self.shooting_song.play()
        if self.firing == Base.SINGLE_FIRE:
            self.fire_dir()

        elif self.firing == Base.DUAL_FIRE:
            self.fire_dir((BULLET_WIDTH, 0))
            self.fire_dir((-BULLET_WIDTH, 0))
            self.fire_dir((-BULLET_WIDTH, 0))

        elif self.firing == Base.TRIPLE_FIRE:
            self.fire_dir((BULLET_WIDTH, 0))
            self.fire_dir((-BULLET_WIDTH, 0))
            self.fire_dir((-BULLET_WIDTH, 0))
            self.fire_dir((BULLET_WIDTH, 0))
            self.fire_dir()

        elif self.firing == Base.SPECIAL_FIRE:
            self.fire_dir((BULLET_WIDTH, 0))
            self.fire_dir((-BULLET_WIDTH, 0))
            self.fire_dir((BULLET_WIDTH, 0))
            self.fire_dir((-BULLET_WIDTH, 0))
            self.fire_dir()
            self.fire_angle(math.pi/4)
            self.fire_angle(-math.pi/4)

    def fire_angle(self, angle = 0, position_var = (0, 0), speed = PLAYER_BULLET_SPEED):
        angle -= math.pi / 2
        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        pos = list(self.rect.midtop)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(PlayerBullet(pos, BULLET_WIDTH, bullet_vel, self.game_state))

    def fire_angle_spring(self, angle = 0, position_var = (0, 0), speed = PLAYER_BULLET_SPEED):
        angle -= math.pi / 2
        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        pos = list(self.rect.midtop)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(SpringBullet(pos, BULLET_WIDTH, bullet_vel, self.game_state))

    def fire_dir(self, position_var = [0, 0], direction = [0, -1], speed = PLAYER_BULLET_SPEED):
        magnitude = direction[0] ** 2 + direction[1] ** 2
        if magnitude > 1:
            direction[0] /= magnitude
            direction[1] /= magnitude

        bullet_vel = (speed * direction[0], speed * direction[1])
        pos = list(self.rect.midtop)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        self.bullet_group.add(PlayerBullet(pos, BULLET_WIDTH, bullet_vel, self.game_state))


    def hit(self, value):
        if self.shield <= 0 and self.burning <= 0:
            if self.lives == 1:
                self.game_state.gameOver    = True
                self.game_state.points      //= 2
                self.lives      = 0
                self.kill()

            else:
                self.firing = Base.DUAL_FIRE
                self.lives -= 1
                self.burning = 0.5
                self.game_state.points      //= 2
                self.bombs = self.total_bombs


    def get_rect(self):
        return self.image.get_rect()
