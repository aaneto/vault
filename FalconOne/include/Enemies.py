import pygame
import Base
import math
import random
from Bullets import Bullet, BULLET_WIDTH, BULLET_SPEED, RocketBullet, SpringBullet, ShortSpringBullet, FollowingBullet
from Items import Upgrade, Life, Bomb, Point, STD_ITEM_SIZE
from Misc import Explosion

ENEMY_STD_SCALE     = Base.WIDTH / 12

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, scale, bullet_group, image, vel = [0, 0], kind = 0):
        pygame.sprite.Sprite.__init__(self)
        self.kind = kind
        pos = list(pos)

        if bullet_group != None:
            self.bullet_group   = bullet_group

        self.image          = image
        self.rect           = self.image.get_rect()
        self.rect.centerx   = pos[0]
        self.rect.centery   = pos[1]
        self.vel            = list(vel)
        self.game_state     = Base.STD_GAME_STATE
        self.reward         = 0
        self.bullet_origin  = 0
        self.firing_rate    = 1000
        self.delta          = 0
        self.enemy_group    = self.game_state.enemy_group

    def kill(self, opt = None):
        self.game_state.misc_group.add(Explosion(self.rect.center, ENEMY_STD_SCALE))
        pygame.sprite.Sprite.kill(self)

    def hit(self, value):
        if self.lives <= value:
            self.game_state.points += self.reward
            self.kill()
        else:
            self.lives -= value

    def get_rect(self):
        return self.image.get_rect()

    def check_boundaries(self):
        if self.rect.right > Base.WIDTH:
            self.rect.right = Base.WIDTH

        elif self.rect.left < 0:
            self.rect.left = 0

        else:
            return False
        return True

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]


        if self.check_boundaries():
            self.vel[0] *= -1

    def fire_angle(self, angle = 0, position_var = (0, 0), speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        angle += math.pi / 2
        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        if self.bullet_origin == 0:
            pos = list(self.rect.midbottom)
        else:
            pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(Bullet(pos, BULLET_WIDTH, bullet_vel, self.game_state, self.kind))

    def fire_dir(self, position_var = [0, 0], direction = [0, 1], speed = BULLET_SPEED, size = BULLET_WIDTH):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        direction = list(direction)
        position_var = list(position_var)
        magnitude = float(math.sqrt(direction[0] ** 2 + direction[1] ** 2))


        if magnitude > 1:
            direction[0] = speed * direction[0] / magnitude
            direction[1] = speed * direction[1] / magnitude
        else:
            direction[0] *= speed
            direction[1] *= speed

        if magnitude == 0:
            magnitude = 1

        if self.bullet_origin == 0:
            pos = list(self.rect.midbottom)
        else:
            pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        self.bullet_group.add(Bullet(pos, size, direction, self.game_state, self.kind))

    def fire_at_player(self, displacement = [0, 0], speed = BULLET_SPEED):
        if self.bullet_origin == 0:
            pos = list(self.rect.midbottom)
        else:
            pos = list(self.rect.center)

        to_player = (self.game_state.player.rect.center[0] - pos[0], self.game_state.player.rect.center[1] - pos[1])
        self.fire_dir(displacement, to_player, speed)

    def fire_angle_spring(self, angle = math.pi, position_var = (0,0), speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        angle += math.pi / 2
        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        if self.bullet_origin == 0:
            pos = list(self.rect.midbottom)
        else:
            pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(SpringBullet(pos, BULLET_WIDTH, bullet_vel, self.game_state))

class Pursuer(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image   = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/ExplosiveBullet.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward         = 100
        self.lives          = 1
        self.bullet_origin  = 1

    def update(self):
        if self.game_state.player.rect.center[0] > self.rect.center[0]:
            self.rect.x += self.vel[0]
        elif self.game_state.player.rect.center[0] < self.rect.center[0]:
            self.rect.x -= self.vel[0]
        self.rect.y += self.vel[1]

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def kill(self, opt = None):
        if self.bullet_origin == 0:
            pos = list(self.rect.midbottom)
        else:
            pos = list(self.rect.center)

        to_player = (self.game_state.player.rect.center[0] - pos[0], self.game_state.player.rect.center[1] - pos[1])
        self.fire_dir((0, 0), to_player, 2 * BULLET_SPEED)
        Enemy.kill(self)

class SingleFireEnemy(Enemy):
    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > self.firing_rate:
            self.delta = 0
            self.fire()

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def fire(self):
        self.fire_dir()

class MultiFireEnemy(Enemy):

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.firing_stage == 0:
            if self.delta > self.delay:
                self.firing_stage = self.fire_qt
                self.delta = 0
        elif self.firing_stage > 0:
            if self.delta > self.fire_interval:
                self.fire()
                self.firing_stage -= 1
                self.delta = 0

        if self.delta > self.firing_rate:
            self.delta = 0
            self.fire()

        if self.rect.top > Base.HEIGHT:
            self.kill()

class DualModeEnemy(Enemy):
    def first_mode(self, to_player):
        self.fire_dir((0, 0), to_player)
        self.fire_dir((BULLET_WIDTH, 0), to_player)

    def second_mode(self):
        self.fire_angle()
        for angle in range(-3, 4):
            self.fire_angle(angle * math.pi/6)
        for angle in range(-2, 3):
            self.fire_angle_spring(math.pi + angle * math.pi/6)


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > self.firing_rate:
            if self.firing_mode == 0:
                to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
                self.bullet_origin = 0
                self.delta = 0
                self.first_mode(to_player)
                self.firing_mode = 1
            elif self.firing_mode == 1:
                self.bullet_origin = 1
                self.second_mode()
                self.firing_mode = 0
                self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

class SmartEnemy(SingleFireEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 1):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/Enemy.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.lives          = 1
        self.reward         = 100

    def fire(self):
        self.fire_at_player()

class BigEnemy(SingleFireEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 1):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/BigEnemy.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.lives          = 3
        self.reward         = 300
        self.firing_rate    = 700

    def fire(self):
        self.fire_dir((-2*BULLET_WIDTH, 0))
        self.fire_dir((2*BULLET_WIDTH, 0))

class VeryBigEnemy(SingleFireEnemy):
    def __init__(self, pos, scale, bullet_group, vel):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/VeryBigEnemy.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale,bullet_group, image, vel, kind)

        self.lives          = 5
        self.reward         = 600
        self.firing_rate    = 600

    def fire(self):
        self.fire_dir()
        self.fire_dir((2*BULLET_WIDTH, 0))
        self.fire_dir((-2*BULLET_WIDTH, 0))

class SingleSpawnEnemy(Enemy):
    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > self.spawn_rate:
            self.spawn()
            self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

class SpawnerBomber(SingleSpawnEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 1):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/Bomber.png"), (int(2 * scale), int(2 *scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward         = 400
        self.lives          = 3
        self.delta          = 3000
        self.spawn_rate     = 3200

    def spawn(self):
        self.enemy_group.add(Pursuer(self.rect.midleft, ENEMY_STD_SCALE/2, self.bullet_group, [2, 2 + self.vel[1]]))
        self.enemy_group.add(Pursuer(self.rect.midright, ENEMY_STD_SCALE/2, self.bullet_group, [2, 2 + self.vel[1]]))

class Rocket(Enemy):
    def __init__(self, pos, scale, bullet_group, vel, kind = 1):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/SmallRocket.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.kind = kind

        self.lives  = 3
        self.reward = 1000

    def kill(self, opt = None):
        self.explode()
        Enemy.kill(self)

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def explode(self):
        angle = 0

        for i in range(10):
            angle += math.pi / 5
            self.fire_angle(angle)


        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])

        self.fire_dir((0, 0), to_player)
        self.fire_dir((0, -BULLET_WIDTH), to_player)
        self.fire_dir([BULLET_WIDTH, -BULLET_WIDTH], to_player)
        self.fire_dir([BULLET_WIDTH, -2*BULLET_WIDTH], to_player)

class SimpleCarrier(Enemy):
    def __init__(self, pos, scale, item_group, item, vel = [0, 0]):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/Triangle.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, None, image, vel)

        self.lives      = 5
        self.reward     = 15
        self.item_group = item_group
        self.item       = item

    def kill(self, opt = -1):
        self.game_state.points += self.reward
        if self.item == "U":
            self.item_group.add(Upgrade((self.rect.centerx, self.rect.centery), STD_ITEM_SIZE))
        elif self.item == "P":
            self.item_group.add(Point((self.rect.centerx, self.rect.centery), STD_ITEM_SIZE, 500))
        elif self.item == "L":
            self.item_group.add(Life((self.rect.centerx, self.rect.centery), STD_ITEM_SIZE, 1))
        elif self.item == "B":
            self.item_group.add(Bomb((self.rect.centerx, self.rect.centery), STD_ITEM_SIZE, 1))
        Enemy.kill(self, opt)

class MultiSpawnEnemy(Enemy):
    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.firing_stage == 0:
            if self.delta > self.delay:
                self.firing_stage = self.spawn_qt
                self.delta = 0
        elif self.firing_stage > 0:
            if self.delta > self.spawn_interval:
                self.spawn()
                self.firing_stage -= 1
                self.delta = 0


        if self.rect.top > Base.HEIGHT:
            self.kill()

class SpawnerShip(MultiSpawnEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/Ship.png"), (int(0.8 * scale), int(1.6 * scale)))
        MultiSpawnEnemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.enemy_group = self.game_state.enemy_group
        self.reward         = 400
        self.lives          = 12
        self.spawn_interval = 400
        self.delay          = 1800
        self.spawn_qt       = 6
        self.firing_stage   = 0

    def spawn(self):
        self.enemy_group.add(Pursuer(self.rect.center, ENEMY_STD_SCALE/2, self.bullet_group, [2, 2 + self.vel[1]]))

class ShipCannon(SingleFireEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Amethyst.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.firing_rate = 1500

    def fire(self):
        self.bullet_group.add(RocketBullet(self.rect.midbottom, BULLET_WIDTH, (0, BULLET_SPEED + self.vel[1]), self.game_state, self.bullet_group))

class ThinCannon(SingleFireEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Peridot.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward         = 400
        self.lives          = 3
        self.firing_rate    = 1500
        self.bullet_origin  = 1

    def fire(self):
        self.fire_at_player((0, 0), 3 * BULLET_SPEED)

class SmallCannon(MultiFireEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.firing_stage = 0
        self.fire_qt = 3
        self.fire_interval = 300
        self.delay = 800

    def fire(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] > 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            angle = math.pi

        self.fire_dir((disp_x,disp_y), to_player)
        self.fire_dir((-disp_x,-disp_y), to_player)
        self.fire_dir((0,0), to_player)

class EnemyGroup(Enemy):
    def kill(self, opt = None):
        for child in self.children:
            child.kill(opt)
        Enemy.kill(self, opt)

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        for child in self.children:
            child.rect.center = self.rect.center

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            self.kill()

class BigShip(EnemyGroup):
    def __init__(self, pos, scale, children, vel = [0, 0], kind = 3):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/BigShip.png"), (scale, int(3 * scale)))
        Enemy.__init__(self, pos, scale, None, image, vel, kind)

        self.lives      = 10
        self.reward     = 300
        self.children   = children

class Bomber(DualModeEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/Bomber.png"), (int(2* scale), int(2 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 10
        self.reward         = 100
        self.firing_mode    = 0
        self.firing_rate    = 1000

class SubmarineCrystal(Enemy):
    def __init__(self, pos, scale, child, vel = [0, 0], kind = 0):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Malachite.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, None, image, vel, kind)
        self.total_lives = 400
        self.lives      = self.total_lives
        self.reward     = 300
        self.laser_angle = 0
        self.game_state.on_boss = True
        self.game_state.actual_boss = self
        self.is_on_middle = False
        self.child = child

    def update(self):
        self.laser_angle += math.pi/40
        if self.lives / float(self.total_lives) < 0.666:
            self.child.mode = 1
        if self.lives / float(self.total_lives) < 0.333:
            self.child.mode = 2
        if not self.is_on_middle:
            self.rect.centery += 2

            if self.rect.centery >= Base.HEIGHT/2:
                self.child.is_on_middle = True
                self.is_on_middle = True
        self.child.rect.center = self.rect.center

    def hit(self, value):
        if self.is_on_middle:
            if self.lives <= value:
                self.game_state.points += self.reward
                self.kill()
            else:
                self.lives -= value

    def kill(self, opt = None):
        self.game_state.on_boss = False
        self.game_state.actual_boss = None
        self.game_state.boss_killed = True
        self.child.kill()
        Enemy.kill(self)

class SubmarineBoss(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 1):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/Alessia.png"), (3 * scale, int(9 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.delta = 0
        self.firing_angle = 0
        self.is_on_middle = False
        self.is_pursuing = False
        self.delta2 = 0
        self.firing_angle = 0
        self.mode = 0
        self.x_angle = 0

    def update(self):
        if self.is_on_middle:
            self.delta += 30
            self.delta2 += 30

            if self.mode == 0:
                if self.delta2 > 200:
                    self.fire_angle(self.firing_angle, (0, 0), BULLET_SPEED)
                    self.firing_angle += math.pi/8
                    self.delta2 = 0

                if self.delta > 800:
                    to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
                    self.fire_dir((0,0), to_player, BULLET_SPEED)

                if 1200 > self.delta > 860:
                    displ_x = self.rect.width/2.7
                    displ_y = self.rect.height/8.7
                    self.spread_fire(6, (displ_x, displ_y/1.5))
                    self.spread_fire(6, (displ_x, -displ_y))
                    self.spread_fire(6, (-displ_x, -displ_y))
                    self.spread_fire(6, (-displ_x, displ_y/1.5))
                    self.delta = 1200
                if self.delta > 1400:
                    self.spread_back(4, (0, -self.rect.height/2), 1.5 * BULLET_SPEED)
                    self.spread_back(4, (0, -self.rect.height/2))
                    self.spread_back(4, (0, -self.rect.height/2), 0.5 * BULLET_SPEED)
                    self.delta = 0
            elif self.mode == 1:

                if self.delta > 250:
                    displ_x = self.rect.width/2.7
                    displ_y = self.rect.height/8.7
                    self.fire_angle_spring(math.pi/2 + self.firing_angle, (displ_x, displ_y/1.5), 1.7 * BULLET_SPEED)
                    self.fire_angle_spring(-math.pi/2 + self.firing_angle, (displ_x, -displ_y), 1.7 * BULLET_SPEED)
                    self.fire_angle_spring(math.pi/2 + self.firing_angle, (-displ_x, -displ_y), 1.7 * BULLET_SPEED)
                    self.fire_angle_spring(-math.pi/2 + self.firing_angle, (-displ_x, displ_y/1.5), 1.7 * BULLET_SPEED)

                    self.firing_angle += math.pi/30
                    self.delta = 0

                if self.delta2 > 1000:
                    self.spread_fire(12, (0, 0), 1.5 * BULLET_SPEED)
                    self.delta2 = 0
            else:
                if self.delta > 2000:
                    displ_x = self.rect.width/2.7
                    displ_y = self.rect.height/8.7
                    self.spread_fire_spring(6, (displ_x, displ_y/1.5))
                    self.spread_fire_spring(6, (displ_x, -displ_y))
                    self.spread_fire_spring(6, (-displ_x, -displ_y))
                    self.spread_fire_spring(6, (-displ_x, displ_y/1.5))
                    self.delta = 0
                if self.delta2 > 200:
                    self.laser(self.firing_angle)
                    self.firing_angle += math.pi/50
                    self.fire_x(self.x_angle)
                    self.x_angle += math.pi/50
                    self.delta2 = 0


    def laser(self, angle):
        self.fire_angle(angle)
        self.fire_angle(angle +math.pi/2)
        self.fire_angle(angle + math.pi)
        self.fire_angle(angle + 3 * math.pi / 2)

    def fire_sides(self):
        # left
        self.fire_angle(4 * math.pi/6)
        self.fire_angle(math.pi/6)
        self.fire_angle(math.pi/2)

        # rigth
        self.fire_angle(-4 * math.pi/6)
        self.fire_angle(-math.pi/6)
        self.fire_angle(-math.pi/2)

        # bottom
        self.fire_angle(0)
        self.fire_angle(-math.pi/6)
        self.fire_angle(math.pi/6)

        # top
        self.fire_angle(-math.pi)

    def fire_x(self, angle):
        self.fire_angle(math.pi/2 + angle)
        self.fire_angle(-math.pi/2 + angle)
        self.fire_angle(math.pi + angle)
        self.fire_angle(-math.pi + angle)

    def spread_back(self, N, position_var = (0, 0), speed = BULLET_SPEED):
        angle = math.pi
        step = math.pi / (2 * N)
        for i in range(N + 1):
            if angle + step > 10 * math.pi/8 or angle + step < 6 * math.pi/8:
                step *= -1
                angle = math.pi

            angle += step
            self.fire_angle_spring(angle, position_var, speed)

    def spread_fire(self, N, position_var = (0, 0), speed = BULLET_SPEED):
        for i in range(1, N + 1):
            angle = i * 2 * math.pi / N
            self.fire_angle(angle, position_var, speed)

    def fire_angle_spring(self, angle = math.pi, position_var = (0,0), speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        angle += math.pi / 2

        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(SpringBullet(pos, BULLET_WIDTH, bullet_vel, self.game_state))

    def fire_angle(self, angle = math.pi, position_var = (0, 0), speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        angle += math.pi / 2
        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(Bullet(pos, BULLET_WIDTH, bullet_vel, self.game_state, self.kind))

    def spread_fire_spring(self, N, position_var = (0,0), speed= BULLET_SPEED):
        for i in range(1, N + 1):
            angle = i * 2 * math.pi / N
            self.fire_angle_spring(angle, position_var, speed)

    def fire_dir(self, position_var = [0, 0], direction = [0, 1], speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        direction = list(direction)
        position_var = list(position_var)
        magnitude = float(math.sqrt(direction[0] ** 2 + direction[1] ** 2)) / 2


        if magnitude > 0:

            direction[0] = speed * direction[0] / magnitude
            direction[1] = speed * direction[1] / magnitude
        else:
            direction[0] *= speed
            direction[1] *= speed

        pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        self.bullet_group.add(Bullet(pos, BULLET_WIDTH, direction, self.game_state, self.kind))

class RocketEnemy(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/ExplosiveBullet.png"), (scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 4
        self.delta  = 0


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 700:
            self.explode(10)
            self.delta = 0


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

class Tank(Enemy):
    def __init__(self, pos, scale, children, vel = [0, 0], kind = 3):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/Veleno.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, None, image, vel, kind)

        self.lives      = 3
        self.reward     = 500
        self.children   = children

    def hit(self, value):
        if self.lives <= 1:
            self.game_state.points += self.reward
            for child in self.children:
                child.kill()
            self.kill()
        else:
            self.lives -= 1

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        for child in self.children:
            child.rect.center = self.rect.center

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            for child in self.children:
                child.kill()

            self.kill()

class SmallTankCannon(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.delta  = 0
        self.delta_burst = 0
        self.bursting  = False

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        if self.bursting:
            self.delta_burst += 35
        else:
            self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1


        if self.delta_burst == 35:
            self.triple_shoot()
        elif self.delta_burst == 350:
            self.triple_shoot()
        elif self.delta_burst == 700:
            self.triple_shoot()
            self.delta_burst = 0
            self.bursting = False


        if self.delta > 800:
            self.delta = 0
            self.bursting = True
            self.delta_burst = 0


        if self.rect.top > Base.HEIGHT:
            self.kill

    def triple_shoot(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if to_player[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2
        self.fire_angle(angle)
        self.fire_angle(angle + math.pi/10)
        self.fire_angle(angle + 2 * math.pi/10)
        self.fire_angle(angle + 3 * math.pi/10)
        self.fire_angle(angle - math.pi/10)
        self.fire_angle(angle - 2 * math.pi/10)
        self.fire_angle(angle - 3 * math.pi/10)

class ThinTankCannon(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Peridot.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward         = 400
        self.lives          = 3
        self.delta          = 0

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 1500:
            self.delta = 0
            self.spread_at_player()

        if self.rect.top > Base.HEIGHT:
            self.kill()


    def spread_at_player(self, position_var = (0, 0), speed = 2 * BULLET_SPEED):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if to_player[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2

        self.fire_angle(angle, position_var, speed)
        self.fire_angle(angle + math.pi/3, position_var, speed)
        self.fire_angle(angle - math.pi/3, position_var, speed)

class DefaultTankCannon(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Amethyst.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.delta  = 0


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 1500:
            self.delta = 0
            self.game_state.enemy_group.add(RocketEnemy(self.rect.midbottom, ENEMY_STD_SCALE/2, self.bullet_group, (0, BULLET_SPEED + self.vel[1])))

        if self.rect.top > Base.HEIGHT:
            self.kill()

class Fabric(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/Fabric.png"), (2 * scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.enemy_group = self.game_state.enemy_group
        self.misc_group = self.game_state.misc_group
        self.real_pos = map(float, self.rect)
        self.reward = 400
        self.lives  = 10
        self.delta  = 3500

    def spawn_tank(self, vel):
        children = []

        pos = list(self.rect.center)
        if pos[0] < ENEMY_STD_SCALE:
            pos[0] += ENEMY_STD_SCALE

        if self.kind == 0:
            c1 = DefaultTankCannon(pos, ENEMY_STD_SCALE // 3, self.bullet_group, vel)
        elif self.kind == 1:
            c1 = ThinTankCannon(pos, ENEMY_STD_SCALE // 3, self.bullet_group, vel)
        elif self.kind == 2:
            c1 = SmallTankCannon(pos, ENEMY_STD_SCALE // 3, self.bullet_group, vel)

        children.append(c1)

        self.enemy_group.add(Tank(pos, ENEMY_STD_SCALE, children, vel))
        self.misc_group.add(c1)

    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]
        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]

        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 4000:
            self.delta = 0
            self.spawn_tank((0, 3))

class Airport(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/Airport.png"), (2 * scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.enemy_group = self.game_state.enemy_group
        self.reward = 400
        self.lives  = 10
        self.delta  = 3000
        self.real_pos = map(float, self.rect)


    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]

        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 4000:
            self.delta = 0
            pos_x = self.rect.right - ENEMY_STD_SCALE//2
            pos_y = self.rect.centery + 10

            self.enemy_group.add(HunterEnemy((pos_x, pos_y), ENEMY_STD_SCALE, self.bullet_group, (0, self.vel[1] + 2)))

class MissileLauncher(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/MissileLauncher.png"), (2 * scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.enemy_group = self.game_state.enemy_group
        self.reward = 400
        self.lives  = 5
        self.delta  = 1500
        self.real_pos = map(float, self.rect)

    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]
        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 2000:
            self.delta = 0
            self.enemy_group.add(ImprovedRocket(self.rect.midbottom, int(ENEMY_STD_SCALE/1.5), self.bullet_group, (0, 2 + self.vel[1])))

class FollowerMissileLauncher(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/MissileLauncher.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.enemy_group = self.game_state.enemy_group
        self.reward = 400
        self.lives  = 10
        self.delta  = 1500

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 2000:
            self.delta = 0
            self.enemy_group.add(FollowingRocket(self.rect.bottomright, ENEMY_STD_SCALE, self.bullet_group, (0, 2 + self.vel[1])))
            self.enemy_group.add(FollowingRocket(self.rect.bottomleft, ENEMY_STD_SCALE, self.bullet_group, (0, 2 + self.vel[1])))

class HunterEnemy(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 1):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/FSN.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.kind = kind
        self.lives          = 5
        self.delta          = 0
        self.reward         = 100

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 1000:
            self.delta = 0
            self.fire_dir()
            self.fire_dir((BULLET_WIDTH, 0))
            self.fire_dir((-BULLET_WIDTH, 0))

        if self.rect.top > Base.HEIGHT:
            self.kill()

class ImprovedRocket(Rocket):
    def __init__(self, pos, scale, bullet_group, vel, kind = 1):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/Serpente.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.kind = kind

        self.lives  = 6
        self.reward = 1000
        self.delta  = 0
    def explode(self):
        angle = 0

        for i in range(24):
            angle += math.pi / 12.0
            vel_x = BULLET_SPEED * math.cos(angle)
            vel_y = BULLET_SPEED * math.sin(angle)
            self.bullet_group.add(Bullet(self.rect.center, BULLET_WIDTH, (vel_x, vel_y), self.game_state))

class Bomber2(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/Vespa.png"), (int(2* scale), int(2 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.delta2         = 0
        self.lives          = 10
        self.reward         = 100
        self.firing_mode    = 0
        self.firing_angle   = 0


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35
        self.delta2  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta2 > 200:
            self.close_in_player()
            self.delta2 = 0

        if self.delta > 1000:
            if self.firing_mode == 0:
                to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
                self.delta = 0
                self.fire_dir((0, 0), to_player)
                self.fire_dir((BULLET_WIDTH, 0), to_player)

                self.fire_dir((-BULLET_WIDTH, 0), (0, -1))
                self.fire_dir((BULLET_WIDTH, 0), (0, -1))
                self.firing_mode = 1
            elif self.firing_mode == 1:
                self.fire_angle()
                for angle in range(-4, 5):
                    self.fire_angle(angle * math.pi/6)
                self.firing_mode = 0
                self.delta = 0



        if self.rect.top > Base.HEIGHT:
            self.kill()

    def close_in_player(self):
        self.fire_angle(self.firing_angle -math.pi/3)
        self.fire_angle(- self.firing_angle + math.pi/3)
        self.firing_angle += math.pi/ 80

class FollowingRocket(Rocket):
    def __init__(self, pos, scale, bullet_group, vel, kind = 1):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level1/SmallRocket.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.kind = kind

        self.lives  = 6
        self.reward = 1000
        self.delta  = 0

    def update(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.midbottom[0], self.game_state.player.rect.center[1] - self.rect.midbottom[1])
        mag = math.sqrt(to_player[0] ** 2 + to_player[1] ** 2)
        if mag == 0:
            vel_x = 0
        else:
            vel_x =  BULLET_SPEED * to_player[0] / mag
        vel_y = self.vel[1]

        self.rect.x += vel_x
        self.rect.y += vel_y
        self.delta  += 50

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            self.explode()
            self.kill()

    def explode(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if self.game_state.player.rect.centery < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2
        self.fire_angle(angle)
        self.fire_angle(angle + math.pi/40)
        self.fire_angle(angle + 2 * math.pi/40)
        self.fire_angle(angle + 3 * math.pi/40)
        self.fire_angle(angle - math.pi/40)
        self.fire_angle(angle - 2 * math.pi/40)
        self.fire_angle(angle - 3 * math.pi/40)

class Bunker(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/Bunker.png"), (int(1.2 * scale), int(1.2 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.real_pos = map(float, self.rect)
        self.reward = 400
        self.lives  = 10
        self.delta  = 0
        self.firing_angle = 0

    def fire_angle(self, angle = 0, position_var = (0, 0), speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        angle += math.pi / 2
        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(Bullet(pos, BULLET_WIDTH, bullet_vel, self.game_state, self.kind))

    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]

        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 160:
            self.firing_angle += math.pi/20
            self.delta = 0
            self.fire_angle(self.firing_angle)

class ScrewBoss(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 1):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level2/Georgia.png"), (int(Base.WIDTH/1.5), int(Base.WIDTH/1.5)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.is_on_middle = False
        self.enemy_group = self
        self.mode = 1
        self.enemy_group = self.game_state.enemy_group
        self.misc_group = self.game_state.misc_group
        self.delta1 = 0
        self.delta2 = 0
        self.hunters_delta = 2000
        self.tanks_delta = 1000
        self.spawn_mode = 0

    def spawn_tank(self, pos, vel, kind=1):
        children = []
        pos = list(pos)

        if pos[0] < ENEMY_STD_SCALE:
            pos[0] += ENEMY_STD_SCALE

        if kind == 0:
            c1 = DefaultTankCannon(pos, ENEMY_STD_SCALE // 3, self.bullet_group, vel)
        elif kind == 1:
            c1 = ThinTankCannon(pos, ENEMY_STD_SCALE // 3, self.bullet_group, vel)
        elif kind == 2:
            c1 = SmallTankCannon(pos, ENEMY_STD_SCALE // 3, self.bullet_group, vel)

        children.append(c1)
        self.enemy_group.add(Tank(pos, ENEMY_STD_SCALE, children, vel))
        self.misc_group.add(c1)

    def update(self):
        if self.is_on_middle:
            self.delta1 += 30
            self.delta2 += 30
            self.hunters_delta += 30
            self.tanks_delta += 30
            if self.mode == 1:
                if self.hunters_delta > 4500:
                    r_airport = (self.rect.centerx + self.rect.width/7.5, self.rect.centery - self.rect.height/6)
                    self.enemy_group.add(HunterEnemy(r_airport, ENEMY_STD_SCALE, self.bullet_group, (0, self.vel[1] + 2)))
                    self.hunters_delta = 0
                if self.delta1 > 60:

                    for i in range(0, 50, 10):
                        self.fire_dir((i//2, -i + self.rect.height/2.4), (0.8,0.6), BULLET_SPEED)
                        self.fire_dir((-i//2, -i + self.rect.height/2.4), (-0.8,0.6), BULLET_SPEED)

                    self.delta1 = 0
            elif self.mode == 2:
                if self.hunters_delta > 4500:
                    r_airport = (self.rect.centerx + self.rect.width/7.5, self.rect.centery - self.rect.height/6)
                    l_airport = (self.rect.centerx - self.rect.width/7.5, self.rect.centery - self.rect.height/6)
                    self.enemy_group.add(HunterEnemy(l_airport, ENEMY_STD_SCALE, self.bullet_group, (0, self.vel[1] + 2)))
                    self.enemy_group.add(HunterEnemy(r_airport, ENEMY_STD_SCALE, self.bullet_group, (0, self.vel[1] + 2)))
                    self.hunters_delta = 0
                if self.delta2 > 90:
                    self.fire_dir((0, self.rect.height/2.4), (0.8,0.6), BULLET_SPEED)
                    self.fire_dir((0, self.rect.height/2.4), (-0.8,0.6), BULLET_SPEED)
                    self.delta2 = 0
                if self.delta1 > 1000:
                    self.fire_dir((0, self.rect.height/2.4), (0,1), BULLET_SPEED)
                    self.fire_dir((0, self.rect.height/2.4), (0.8,0.6), BULLET_SPEED)
                    self.fire_dir((0, self.rect.height/2.4), (-0.8,0.6), BULLET_SPEED)
                    self.delta1 = 0
                if self.tanks_delta > 7000:
                    r_field = (self.rect.centerx + self.rect.width/7.5, self.rect.centery + self.rect.height/3)
                    l_field = (self.rect.centerx - self.rect.width/7.5, self.rect.centery + self.rect.height/3)
                    if self.spawn_mode == 0:
                        self.spawn_tank(r_field, (self.vel[1] + 2, 0), 1)
                        self.spawn_tank(l_field, (-(self.vel[1] + 2), 0), 2)
                        self.spawn_mode = 1
                    else:
                        self.spawn_tank(r_field, (self.vel[1] + 2, 0), 2)
                        self.spawn_tank(l_field, (-(self.vel[1] + 2), 0), 1)
                        self.spawn_mode = 0
                    self.tanks_delta = 0
            else:
                if self.hunters_delta > 3500:
                    r_airport = (self.rect.centerx + self.rect.width/7.5, self.rect.centery - self.rect.height/6)
                    l_airport = (self.rect.centerx - self.rect.width/7.5, self.rect.centery - self.rect.height/6)
                    self.enemy_group.add(HunterEnemy(l_airport, ENEMY_STD_SCALE, self.bullet_group, (0, self.vel[1] + 2)))
                    self.enemy_group.add(HunterEnemy(r_airport, ENEMY_STD_SCALE, self.bullet_group, (0, self.vel[1] + 2)))
                    self.hunters_delta = 0
                if self.delta1 > 2300:
                    self.explode((0, self.rect.height/2.4))
                    self.delta1 = 0
                if self.tanks_delta > 5000:
                    r_field = (self.rect.centerx + self.rect.width/7.5, self.rect.centery + self.rect.height/3)
                    l_field = (self.rect.centerx - self.rect.width/7.5, self.rect.centery + self.rect.height/3)
                    if self.spawn_mode == 0:
                        self.spawn_tank(r_field, (self.vel[1] + 2, 0), 1)
                        self.spawn_tank(l_field, (-(self.vel[1] + 2), 0), 2)
                        self.spawn_mode = 1
                    else:
                        self.spawn_tank(r_field, (self.vel[1] + 2, 0), 2)
                        self.spawn_tank(l_field, (-(self.vel[1] + 2), 0), 1)
                        self.spawn_mode = 0
                    self.tanks_delta = 0

    def triple_shoot(self, displacement):
        pos = (self.rect.center[0] + displacement[0], self.rect.center[1] + displacement[1])
        to_player = (self.game_state.player.rect.center[0] - pos[0], self.game_state.player.rect.center[1] - pos[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if pos[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2
        self.fire_angle(angle)
        self.fire_angle(angle + math.pi/10, displacement)
        self.fire_angle(angle + 2 * math.pi/10, displacement)
        self.fire_angle(angle + 3 * math.pi/10, displacement)
        self.fire_angle(angle - math.pi/10, displacement)
        self.fire_angle(angle - 2 * math.pi/10, displacement)
        self.fire_angle(angle - 3 * math.pi/10, displacement)

    def explode(self, displacement):
        angle = 0

        for i in range(24):
            angle += math.pi / 12.0
            vel_x = BULLET_SPEED * math.cos(angle)
            vel_y = BULLET_SPEED * math.sin(angle)
            pos = (self.rect.centerx + displacement[0], self.rect.centery + displacement[1])
            self.bullet_group.add(Bullet(pos, BULLET_WIDTH, (vel_x, vel_y), self.game_state))

    def fire_dir(self, position_var = [0, 0], direction = [0, 1], speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        direction = list(direction)
        position_var = list(position_var)
        magnitude = float(math.sqrt(direction[0] ** 2 + direction[1] ** 2))


        if magnitude > 1:
            direction[0] = speed * direction[0] / magnitude
            direction[1] = speed * direction[1] / magnitude
        else:
            direction[0] *= speed
            direction[1] *= speed

        if magnitude == 0:
            magnitude = 1

        pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        self.bullet_group.add(Bullet(pos, BULLET_WIDTH, direction, self.game_state, self.kind))

class ScrewCrystal(Enemy):
    def __init__(self, pos, scale, child, crystals, vel = [0, 0], kind = 0):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/MetalCross.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, None, image, vel, kind)
        self.total_lives = 500
        self.lives      = self.total_lives
        self.reward     = 300
        self.game_state.on_boss = True
        self.game_state.actual_boss = self
        self.is_on_middle = False
        self.child = child
        self.crystals = crystals
        self.crystals[0].rect.centerx += self.child.rect.width/4.8
        self.crystals[0].rect.centery -= self.child.rect.height/5
        self.crystals[1].rect.centerx -= self.child.rect.width/4.8
        self.crystals[1].rect.centery -= self.child.rect.height/5
        self.v_vel = 2

    def update(self):
        if self.rect.centery > Base.HEIGHT/3:
            self.rect.centery = Base.HEIGHT/3
            self.child.is_on_middle = True
            self.is_on_middle = True
            self.crystals[0].is_on_middle = True
            self.crystals[1].is_on_middle = True

        if not self.is_on_middle:
            self.rect.centery += 2
            for crystal in self.crystals:
                crystal.rect.centery += 2
        else:
            self.rect.centerx += self.v_vel
	    for crystal in self.crystals:
                crystal.rect.centerx += self.v_vel
            if self.rect.centerx > Base.WIDTH:
                self.v_vel *= -1
                self.rect.centerx = Base.WIDTH
            elif self.rect.centerx < 0:
                self.v_vel *= -1
                self.rect.centerx = 0

        self.child.rect.center = self.rect.center

    def hit(self, value):
        if self.is_on_middle:
            if self.lives <= value:
                self.game_state.points += self.reward
                self.kill()
            else:
                self.lives -= value
        if 0 < self.lives < self.total_lives/3.0:
            self.child.mode = 3
            self.crystals[0].mode = 3
            self.crystals[1].mode = 3

        elif self.total_lives/3.0 < self.lives < 2 * self.total_lives/3.0:
            self.child.mode = 2
            self.crystals[0].mode = 2
            self.crystals[1].mode = 2

    def kill(self, opt = None):
        self.game_state.on_boss = False
        self.game_state.actual_boss = None
        self.game_state.boss_killed = True
        self.child.kill()
        for crystal in self.crystals:
            crystal.kill()
        Enemy.kill(self)

class ScrewMinorCrystal(Enemy):

    def __init__(self, pos, scale, bullet_group, vel = [0, 0], fire_mode = 0):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/MetalCross.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, 1)
        self.reward     = 300
        self.is_on_middle = False
        self.delta = 0
        self.mode = 3
        self.fire_mode = fire_mode
        self.firing_angle = 0

    def update(self):
        if self.is_on_middle:
            if self.mode == 1:
                self.delta += 30

                if self.fire_mode == 0 and self.delta > 900:
                    self.spread_back()
                    self.delta = 0
                    self.fire_mode = 1
                elif self.fire_mode == 1 and self.delta > 1200:
                    self.triple_shoot()
                    self.delta = 0
                    self.fire_mode = 0
            elif self.mode == 2:
                self.delta += 30
                if self.fire_mode == 0 and self.delta > 400:
                    self.fire_at_player()
                    self.delta = 0
                    self.fire_mode = 1
                elif self.fire_mode == 1 and self.delta > 800:
                    self.fire_at_player()
                    self.delta = 0
                    self.fire_mode = 0
            else:
                self.delta += 30
                self.firing_angle += math.pi/30
                if self.delta > 180:
                    self.fire_angle(self.firing_angle)
                    self.delta = 0


    def spread_at_player(self, position_var = (0, 0), speed = BULLET_SPEED):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if to_player[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2

        self.fire_angle(angle, position_var, speed)
        self.fire_angle(angle + math.pi/3, position_var, speed)
        self.fire_angle(angle - math.pi/3, position_var, speed)

    def triple_shoot(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if to_player[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2
        self.fire_angle(angle)
        self.fire_angle(angle + math.pi/10)
        self.fire_angle(angle + 2 * math.pi/10)
        self.fire_angle(angle + 3 * math.pi/10)
        self.fire_angle(angle - math.pi/10)
        self.fire_angle(angle - 2 * math.pi/10)
        self.fire_angle(angle - 3 * math.pi/10)

    def spread_back(self, position_var = (0, 0), speed = 2*BULLET_SPEED):
        self.fire_angle_spring(-math.pi, position_var, speed)
        self.fire_angle_spring(-math.pi + math.pi/3, position_var, speed)
        self.fire_angle_spring(-math.pi - math.pi/3, position_var, speed)

    def fire_angle_spring(self, angle = math.pi, position_var = (0,0), speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        angle += math.pi / 2
        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(SpringBullet(pos, BULLET_WIDTH, bullet_vel, self.game_state))
    def kill(self, opt = None):
	if opt != -1:
	    Enemy.kill(self)

class TimedRocket(Enemy):
    def __init__(self, pos, scale, bullet_group, vel, kind, time):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/V2.png"), (0,0))
        Enemy.__init__(self, pos, 0, bullet_group, image, vel, kind)
        self.scale = scale
        self.kind = kind

        self.lives  = 3
        self.reward = 1000
        self.delta  = 0
        self.time = time

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 50

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            self.explode()

        if self.delta > self.time:
            self.explode()

    def hit(self, value):
        pass

    def explode(self):
        angle = 0

        for i in range(10):
            angle += math.pi / 5
            self.fire_angle(angle)
        self.kill()

class V2(Rocket):
    def __init__(self, pos, scale, bullet_group, vel, kind = 1):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/V2.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.scale = scale
        self.lives  = 3
        self.reward = 1000

    def explode(self):
        self.enemy_group.add(TimedRocket(self.rect.center, self.scale, self.bullet_group, self.vel, self.kind, 0))
        self.enemy_group.add(TimedRocket(self.rect.center, self.scale, self.bullet_group, self.vel, self.kind, 800))
        self.enemy_group.add(TimedRocket(self.rect.center, self.scale, self.bullet_group, self.vel, self.kind, 1600))

class Eichelhaher(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Eichelhaher.png"), (int(2* scale), int(2 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 2000
        self.lives          = 10
        self.reward         = 100
        self.firing_mode    = 0
        self.enemy_group    = self.game_state.enemy_group

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 4000:
            self.enemy_group.add(ImprovedRocket(self.rect.topleft, ENEMY_STD_SCALE//2, self.bullet_group, [0, self.vel[1] - 1]))
            self.enemy_group.add(ImprovedRocket(self.rect.topright, ENEMY_STD_SCALE//2, self.bullet_group, [0, self.vel[1] - 1]))
            self.delta = 0



        if self.rect.top > Base.HEIGHT:
            self.kill()

class Schneefink(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 2):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Schneefink.png"), (int(2* scale), int(2 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.delta2         = 0
        self.lives          = 10
        self.reward         = 100
        self.firing_mode    = 0
        self.firing_angle   = 0


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35
        self.delta2  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta2 > 400:
            self.fire_angle(math.pi/4, (-self.rect.width/4, 0))
            self.fire_angle(-math.pi/4, (self.rect.width/4, 0))
            self.delta2 = 0

        if self.delta > 600:
            self.fire_dir_spring((0, -self.rect.height/2), (0, -1))
            self.fire_dir_spring((0, -self.rect.height/2), (0.6, -0.8))
            self.fire_dir_spring((0, -self.rect.height/2), (-0.6, -0.8))
            self.delta = 0



        if self.rect.top > Base.HEIGHT:
            self.kill()

    def fire_dir_spring(self, position_var = [0, 0], direction = [0, 1], speed = BULLET_SPEED//2):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        direction = list(direction)
        position_var = list(position_var)
        magnitude = float(math.sqrt(direction[0] ** 2 + direction[1] ** 2)) / 2

        if magnitude > 0:

            direction[0] = speed * direction[0] / magnitude
            direction[1] = speed * direction[1] / magnitude
        else:
            direction[0] *= speed
            direction[1] *= speed

        pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        self.bullet_group.add(SpringBullet(pos, BULLET_WIDTH, direction, self.game_state, self.kind))

class Graureiher(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 2):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Graureiher.png"), (int(2* scale), int(2 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.delta2         = 0
        self.lives          = 10
        self.reward         = 100
        self.firing_mode    = 0
        self.firing_angle   = 0


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35
        self.delta2  += 35
        self.firing_angle += math.pi/30

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta2 > 120:
            self.fire_angle(math.pi/4, (-self.rect.width/3, 0))
            self.fire_angle(-math.pi/4, (self.rect.width/3, 0))
            self.delta2 = 0

        if self.delta > 90:
            self.fire_angle(self.firing_angle, (-self.rect.width/3, -self.rect.height/2))
            self.fire_angle(math.pi-self.firing_angle, (self.rect.width/3, -self.rect.height/2))
            self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

class Birkhuhn(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 2):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Birkhuhn.png"), (int(2* scale), int(2 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.delta2         = 0
        self.lives          = 10
        self.reward         = 100
        self.firing_mode    = 0
        self.firing_angle   = 0


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35
        self.delta2  += 35
        self.firing_angle += math.pi/30

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.firing_mode == 0 and self.delta2 > 900:
            self.octa_fire()

            self.delta2 = 0
            self.firing_mode = 1
        elif self.firing_mode == 1 and self.delta2 > 200:
            self.octa_fire()
            self.delta2 = 0
            self.firing_mode = 0

        if self.delta > 900:
            self.spread_at_player()
            self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def octa_fire(self):
        self.fire_dir((BULLET_WIDTH,self.rect.width/5), (-1,5))
        self.fire_dir((2*BULLET_WIDTH,self.rect.width/5), (-1,5))
        self.fire_dir((3*BULLET_WIDTH,self.rect.width/5), (-1,5))

        self.fire_dir((-BULLET_WIDTH,self.rect.width/5), (1,5))
        self.fire_dir((-2*BULLET_WIDTH,self.rect.width/5), (1,5))
        self.fire_dir((-3*BULLET_WIDTH,self.rect.width/5), (1,5))

        self.fire_dir((-BULLET_WIDTH,-self.rect.width/2), (-1,-5))
        self.fire_dir((-2*BULLET_WIDTH,-self.rect.width/2), (-1,-5))
        self.fire_dir((-3*BULLET_WIDTH,-self.rect.width/2), (-1,-5))

        self.fire_dir((BULLET_WIDTH,-self.rect.width/2), (1,-5))
        self.fire_dir((2*BULLET_WIDTH,-self.rect.width/2), (1,-5))
        self.fire_dir((3*BULLET_WIDTH,-self.rect.width/2), (1,-5))


    def spread_at_player(self, position_var = (0, 0), speed = BULLET_SPEED):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if self.game_state.player.rect.centery < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2

        self.fire_angle(angle, position_var, speed)
        self.fire_angle(angle + math.pi/3, position_var, speed)
        self.fire_angle(angle - math.pi/3, position_var, speed)

    def fire_angle(self, angle = 0, position_var = (0, 0), speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        angle += math.pi / 2
        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(Bullet(pos, BULLET_WIDTH, bullet_vel, self.game_state, self.kind))

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class Edelweiss(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Edelweiss.png"), (int(1.5 * scale), int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 2000
        self.delta2         = 0
        self.total_lives    = 110
        self.lives          = self.total_lives
        self.reward         = 100
        self.firing_mode    = 0
        self.firing_angle   = 0
        self.respawnable    = True
        self.scale          = scale
        self.bursting       = False
        self.timeacc        = 0
        self.delta3         = 0

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        if self.rect.y > Base.HEIGHT/2 or self.rect.y < -80:
            self.vel[1] *= -1



        self.delta  += 35
        self.delta2 += 35
        self.delta3 += 35
        self.firing_angle += math.pi/30

        if self.lives / float(self.total_lives) < 0.5 and self.respawnable:
            left = (self.rect.centerx + ENEMY_STD_SCALE, self.rect.centery)
            right = (self.rect.centerx - ENEMY_STD_SCALE, self.rect.centery)
            center = (self.rect.centerx, self.rect.centery + ENEMY_STD_SCALE)
            e1 = Edelweiss(left, self.scale, self.bullet_group, self.vel, self.kind)
            e2 = Edelweiss(right, self.scale, self.bullet_group, self.vel, self.kind)
            e3 = Edelweiss(center, self.scale, self.bullet_group, self.vel, self.kind)


            e1.respawnable = False
            e2.respawnable = False
            e3.respawnable = False
            self.game_state.enemy_group.add(e1)
            self.game_state.enemy_group.add(e2)
            self.game_state.enemy_group.add(e3)
            self.kill()

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta2 > 900:
            self.explode()
            self.delta2 = 0
            self.firing_mode = 1

        if self.delta > 3000:
            self.bursting = True
            self.delta = 0

        if self.bursting and self.delta3 > 90:
            self.fire_angle(math.pi/10)
            self.fire_angle(-math.pi/10)
            self.fire_angle(2 * math.pi/10)
            self.fire_angle(-2 * math.pi/10)
            self.delta3 = 0
            self.timeacc += 1

        if self.timeacc > 20:
            self.timeacc = 0
            self.bursting = False
            self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def explode(self):
        angle = 0

        for i in range(24):
            angle += math.pi / 12.0
            vel_x = BULLET_SPEED * math.cos(angle)
            vel_y = BULLET_SPEED * math.sin(angle)
            self.bullet_group.add(Bullet(self.rect.center, BULLET_WIDTH, (vel_x, vel_y), self.game_state))

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class Maiglockchen(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [2, 2], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Maiglockchen.png"), (int(1.5 * scale), int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 2000
        self.delta2         = 0
        self.total_lives    = 120
        self.lives          = self.total_lives
        self.reward         = 100
        self.firing_mode    = 0
        self.firing_angle   = 0
        self.respawnable    = True
        self.scale          = scale
        self.bursting       = False
        self.timeacc        = 0
        self.delta3         = 0
        self.misc_group     = self.game_state.misc_group
        self.mode           = 0
        self.spawned        = False
        self.stachels       = []

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        if self.rect.centery > Base.HEIGHT//2:
            self.vel[1] = 0


        self.delta  += 35
        self.delta2 += 35
        self.delta3 += 35
        self.firing_angle += math.pi/30

        if self.lives / float(self.total_lives) < 0.5 and not self.spawned:
            self.vel[1] = 0
            self.vel[0] = float(self.vel[0]) / abs(self.vel[0])
            self.mode = 1

            first_left = list(self.rect.center)
            first_left[0] += ENEMY_STD_SCALE

            second_left = list(self.rect.center)
            second_left[0] += 2 * ENEMY_STD_SCALE

            first_right = list(self.rect.center)
            first_right[0] -= ENEMY_STD_SCALE

            second_right = list(self.rect.center)
            second_right[0] -= 2 * ENEMY_STD_SCALE

            s1 = Stachel(first_right, self.scale, self.bullet_group, self.vel, self.kind)
            s2 = Stachel(second_right, self.scale, self.bullet_group, self.vel, self.kind)
            s3 = Stachel(first_left, self.scale, self.bullet_group, self.vel, self.kind)
            s4 = Stachel(second_left, self.scale, self.bullet_group, self.vel, self.kind)
            s1.binding_group = [self, s2, s3, s4]
            s2.binding_group = [self, s1, s3, s4]
            s3.binding_group = [self, s1, s2, s4]
            s4.binding_group = [self, s1, s2, s3]

            self.stachels.extend([s1,s2,s3,s4])

            self.misc_group.add(s1)
            self.misc_group.add(s2)
            self.misc_group.add(s3)
            self.misc_group.add(s4)
            self.spawned = True

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.mode == 0:
            if self.delta2 > 900:
                self.octa_fire()
                self.delta2 = 0
                self.firing_mode = 1

            if self.delta > 3000:
                self.bursting = True
                self.delta = 0

            if self.bursting and self.delta3 > 90:
                self.fire_dir()
                self.delta3 = 0
                self.timeacc += 1

            if self.timeacc > 20:
                self.timeacc = 0
                self.bursting = False
                self.delta = 0
        elif self.mode == 1:

            if self.delta > 3500:
                self.bursting = True
                self.delta = 0

            if self.bursting and self.delta3 > 90:
                self.fire_dir()
                self.fire_dir((BULLET_WIDTH,0))
                self.fire_dir((2*BULLET_WIDTH,0))
                self.fire_dir((-BULLET_WIDTH,0))
                self.fire_dir((-2*BULLET_WIDTH,0))

                self.delta3 = 0
                self.timeacc += 1

            if self.timeacc > 20:
                self.timeacc = 0
                self.bursting = False
                self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()


    def kill(self, opt = 1):
        if opt > 0:
            for stach in self.stachels:
                stach.kill()
            Enemy.kill(self)

    def explode(self):
        angle = 0

        for i in range(24):
            angle += math.pi / 12.0
            vel_x = BULLET_SPEED * math.cos(angle)
            vel_y = BULLET_SPEED * math.sin(angle)
            self.bullet_group.add(Bullet(self.rect.center, BULLET_WIDTH, (vel_x, vel_y), self.game_state))

    def octa_fire(self):
        self.fire_dir((BULLET_WIDTH,self.rect.width/6), (1,5))
        self.fire_dir((2*BULLET_WIDTH,-10 + self.rect.width/6), (1,5))
        self.fire_dir((3*BULLET_WIDTH,-20 + self.rect.width/6), (1,5))

        self.fire_dir((-BULLET_WIDTH,self.rect.width/6), (-1,5))
        self.fire_dir((-2*BULLET_WIDTH,-10 + self.rect.width/6), (-1,5))
        self.fire_dir((-3*BULLET_WIDTH,-20 + self.rect.width/6), (-1,5))

class Stachel(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 2):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Stachel.png"), (scale//2, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 15
        self.reward         = 100
        self.binding_group  = None


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1
            for ele in self.binding_group:
                ele.vel[0] *= -1


        if self.delta > 1000:
            self.fire_dir()
            self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class LaserStachel(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 2):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Stachel.png"), (scale//2, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 15
        self.reward         = 100
        self.bursting       = False
        self.delta3         = 0
        self.timeacc        = 0


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35
        self.delta3 += 35

        if self.check_boundaries():
            self.vel[0] *= -1
            for ele in self.binding_group:
                ele.vel[0] *= -1


        if self.delta > 3000:
            self.bursting = True
            self.delta = 0

        if self.bursting and self.delta3 > 90:
            self.fire_dir()
            self.delta3 = 0
            self.timeacc += 1

        if self.timeacc > 20:
            self.timeacc = 0
            self.bursting = False
            self.delta = 0

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class Lowernzahn(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Lowernzahn.png"), (scale, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 100
        self.total_lives    = self.lives
        self.reward         = 100
        self.binding_group  = None
        self.fire_mode      = 0
        self.explosion_acc  = 0
        self.firing_acc     = 0
        self.mode           = 0
        self.spawned        = False
        self.stachels       = []
        self.scale          = scale
        self.misc_group     = self.game_state.misc_group
        self.x_angle        = 0

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.lives / float(self.total_lives) < 0.5 and not self.spawned:
            self.mode = 1

            left = list(self.rect.center)
            left[0] += ENEMY_STD_SCALE

            right = list(self.rect.center)
            right[0] -= ENEMY_STD_SCALE


            s1 = LaserStachel(left, self.scale, self.bullet_group, self.vel, self.kind)
            s2 = LaserStachel(right, self.scale, self.bullet_group, self.vel, self.kind)
            s1.binding_group = [self, s2]
            s2.binding_group = [self, s1]

            self.stachels.extend([s1,s2])

            self.misc_group.add(s1)
            self.misc_group.add(s2)
            self.spawned = True



        if self.rect.y > Base.HEIGHT/2 or self.rect.y < -80:
            self.vel[1] *= -1
            if self.stachels != None:
                for ele in self.stachels:
                    ele.vel[1] *= -1

        if self.check_boundaries():
            self.vel[0] *= -1
            if self.stachels != None:
                for ele in self.stachels:
                    ele.vel[0] *= -1

        if self.mode == 0:
            if self.explosion_acc > 1:
                self.explosion_acc = 0
                self.fire_mode = 1

            if self.firing_acc > 2:
                self.firing_acc = 0
                self.fire_mode = 0


            if self.fire_mode == 0 and self.delta > 1000:
                self.explode()
                self.explosion_acc += 1
                self.delta = 0

            if self.fire_mode == 1 and self.delta > 120:
                self.fire_at_player((0, 0), 3 * BULLET_SPEED)
                self.firing_acc += 1
                self.delta = 0
        elif self.mode == 1:
            if self.delta > 90:
                self.fire_x(self.x_angle)
                self.x_angle += math.pi/50
                self.delta = 0


        if self.rect.top > Base.HEIGHT:
            self.kill()

    def explode(self):
        angle = 0
        n = 20

        for i in range(n):
            angle += math.pi / (n // 2)
            vel_x = BULLET_SPEED * math.cos(angle)
            vel_y = BULLET_SPEED * math.sin(angle)
            self.bullet_group.add(Bullet(self.rect.center, BULLET_WIDTH, (vel_x, vel_y), self.game_state))

    def fire_x(self, angle):
        self.fire_angle(angle)
        self.fire_angle(-math.pi + angle)
        self.fire_angle(-math.pi/2 + angle)
        self.fire_angle(-angle)

    def kill(self, opt = 1):
        if opt > 0:
            for stachel in self.stachels:
                stachel.kill()
            Enemy.kill(self)

class Sonnenblume(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Sonnenblume.png"), (4 * scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.lives          = 150
        self.total_lives    = self.lives
        self.reward         = 100
        self.stachels       = []
        self.scale          = scale
        self.misc_group     = self.game_state.misc_group
        self.dmg_acc        = 0
        self.speed_limit    = self.lives // 5
        self.add_stachels()

    def add_stachels(self):
        self.mode = 1

        left = list(self.rect.center)
        left[0] += ENEMY_STD_SCALE

        right = list(self.rect.center)
        right[0] -= ENEMY_STD_SCALE


        s1 = StachelZwei(left, self.scale, self.bullet_group, self.vel, self.kind)
        s2 = StachelZwei(right, self.scale, self.bullet_group, self.vel, self.kind)
        s3 = StachelZwei((right[0] + 10, right[1] - ENEMY_STD_SCALE), self.scale, self.bullet_group, self.vel, self.kind)
        s4 = StachelZwei((left[0] - 10, left[1] - ENEMY_STD_SCALE), self.scale, self.bullet_group, self.vel, self.kind)
        s5 = StachelZwei((right[0] + 20, right[1] + ENEMY_STD_SCALE), self.scale, self.bullet_group, self.vel, self.kind)
        s6 = StachelZwei((left[0] - 20, left[1] + ENEMY_STD_SCALE), self.scale, self.bullet_group, self.vel, self.kind)
        s7 = StachelZwei((right[0] - ENEMY_STD_SCALE//2, right[1] - ENEMY_STD_SCALE - 10), self.scale, self.bullet_group, self.vel, self.kind)
        s8 = StachelZwei((left[0] + ENEMY_STD_SCALE//2, left[1] - ENEMY_STD_SCALE - 10), self.scale, self.bullet_group, self.vel, self.kind)

        s1.binding_group = [self, s2, s3, s4, s5, s6, s7, s8]
        s2.binding_group = [self, s1, s3, s4, s5, s6, s7, s8]
        s3.binding_group = [self, s1, s2, s4, s5, s6, s7, s8]
        s4.binding_group = [self, s1, s2, s3, s5, s6, s7, s8]
        s5.binding_group = [self, s1, s2, s3, s4, s6, s7, s8]
        s6.binding_group = [self, s1, s2, s3, s4, s5, s7, s8]
        s7.binding_group = [self, s1, s2, s3, s4, s5, s6, s8]
        s8.binding_group = [self, s1, s2, s3, s4, s5, s6, s7]


        self.stachels.extend([s1,s2, s3, s4, s5, s6, s7, s8])

        self.misc_group.add(s1)
        self.misc_group.add(s2)
        self.misc_group.add(s3)
        self.misc_group.add(s4)
        self.misc_group.add(s5)
        self.misc_group.add(s6)
        self.misc_group.add(s7)
        self.misc_group.add(s8)

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        if self.dmg_acc > self.speed_limit:
            self.dmg_acc = 0
            for stachel in self.stachels:
                stachel.firing_rate -= 400

        if self.rect.y > Base.HEIGHT/2 or self.rect.y < -80:
            self.vel[1] *= -1
            if self.stachels != None:
                for ele in self.stachels:
                    ele.vel[1] *= -1

        if self.check_boundaries():
            self.vel[0] *= -1
            for ele in self.stachels:
                ele.vel[0] *= -1

    def hit(self, value):
        self.dmg_acc += 1
        Enemy.hit(self, value)

    def kill(self, opt = 1):
        if opt > 0:
            for stach in self.stachels:
                stach.kill()
            Enemy.kill(self)

class StachelDrei(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Stachel.png"), (scale//2, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 15
        self.reward         = 100
        self.binding_group  = None
        self.firing_mode    = 0
        self.firing_rate    = 2100

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1
            for ele in self.binding_group:
                ele.vel[0] *= -1

        if self.delta > 900:
            self.spread_at_player()
            self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def spread_at_player(self, position_var = (0, 0), speed = 2 * BULLET_SPEED):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if to_player[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2

        self.fire_angle(angle, position_var, speed)
        self.fire_angle(angle + math.pi/3, position_var, speed)
        self.fire_angle(angle - math.pi/3, position_var, speed)

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class StachelZwei(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Stachel.png"), (scale//2, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 15
        self.reward         = 100
        self.binding_group  = None
        self.firing_mode    = 0
        self.firing_rate    = 2100


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1
            for ele in self.binding_group:
                ele.vel[0] *= -1

        if self.firing_mode == 0 and self.delta > 500:
            self.triple_shoot()
            self.delta = 0
            self.firing_mode = 1

        if self.firing_mode == 1 and self.delta > 500:
            self.spread_at_player()
            self.delta = 0
            self.firing_mode = 2

        if self.firing_mode == 2 and self.delta > self.firing_rate:
            self.firing_mode = 0
            self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def spread_at_player(self, position_var = (0, 0), speed = 2 * BULLET_SPEED):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if to_player[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2

        self.fire_angle(angle, position_var, speed)
        self.fire_angle(angle + math.pi/3, position_var, speed)
        self.fire_angle(angle - math.pi/3, position_var, speed)

    def triple_shoot(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if self.game_state.player.rect.centery < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2
        self.fire_angle(angle)
        self.fire_angle(angle + math.pi/10)
        self.fire_angle(angle + 2 * math.pi/10)
        self.fire_angle(angle + 3 * math.pi/10)
        self.fire_angle(angle - math.pi/10)
        self.fire_angle(angle - 2 * math.pi/10)
        self.fire_angle(angle - 3 * math.pi/10)

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class Blatt(Rocket):
    def __init__(self, pos, scale, bullet_group, vel, kind = 4):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Blatt.png"), (scale//2, int(1.5 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.kind = kind

        self.lives  = 3
        self.reward = 1000
        self.delta  = 0

    def explode(self):
        for angle in [0, math.pi/2, math.pi, 3 * math.pi/2]:
            self.fire_angle(angle)
            self.fire_angle(angle + math.pi/40)
            self.fire_angle(angle + 2 * math.pi/40)
            self.fire_angle(angle + 3 * math.pi/40)
            self.fire_angle(angle - math.pi/40)
            self.fire_angle(angle - 2 * math.pi/40)
            self.fire_angle(angle - 3 * math.pi/40)

class TranendeHerz(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/TranendeHerz.png"), (int(3* scale), int(3 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 200
        self.total_lives    = 200
        self.reward         = 100
        self.enemy_group    = self.game_state.enemy_group
        self.scale          = scale
        self.stachels       = []
        self.mode           = 0
        self.spawned        = False
        self.misc_group     = self.game_state.misc_group


    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.rect.y > Base.HEIGHT/2 or self.rect.y < -80:
            self.vel[1] *= -1
            for ele in self.stachels:
                ele.vel[1] *= -1

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.lives / float(self.total_lives) < 0.5 and not self.spawned:
            self.mode = 1

            left = list(self.rect.center)
            left[0] += ENEMY_STD_SCALE

            right = list(self.rect.center)
            right[0] -= ENEMY_STD_SCALE


            s1 = StachelDrei(left, self.scale, self.bullet_group, self.vel, self.kind)
            s2 = StachelDrei(right, self.scale, self.bullet_group, self.vel, self.kind)
            s1.binding_group = [self, s2]
            s2.binding_group = [self, s1]

            self.stachels.extend([s1,s2])

            self.misc_group.add(s1)
            self.misc_group.add(s2)
            self.spawned = True

        if self.mode == 0:
            if self.delta > 2500:
                if self.vel[1] > 0:
                    rocket_vel = self.vel[1] + 2
                else:
                    rocket_vel = 2
                self.enemy_group.add(Blatt(self.rect.bottomleft, self.scale, self.bullet_group, (self.vel[0], rocket_vel), self.kind))
                self.enemy_group.add(Blatt(self.rect.bottomright, self.scale, self.bullet_group, (self.vel[0], rocket_vel), self.kind))
                self.delta = 0
        else:
            if self.delta > 2500:
                if self.vel[1] > 0:
                    rocket_vel = self.vel[1] + 2
                else:
                    rocket_vel = 2
                self.enemy_group.add(Blatt(self.rect.bottomleft, self.scale, self.bullet_group, (self.vel[0], rocket_vel), self.kind))
                self.enemy_group.add(Blatt(self.rect.bottomright, self.scale, self.bullet_group, (self.vel[0], rocket_vel), self.kind))
                self.enemy_group.add(Blatt(self.rect.midbottom, self.scale, self.bullet_group, (self.vel[0], rocket_vel), self.kind))
                self.delta = 0

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def kill(self, opt = 1):
        if opt > 0:
            for stach in self.stachels:
                stach.kill()
            Enemy.kill(self)

class BunkerCrystal(SingleFireEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 1):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/MetalCross.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.lives          = 50
        self.reward         = 100
        self.bullet_origin  = 1
        self.relatives      = []
        self.firing_angle   = 0
        self.firing_rate    = 160

    def add_relatives(self, relatives):
        self.relatives = relatives

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1
            for relative in self.relatives:
                relative.vel[0] *= -1

        if self.delta > self.firing_rate:
            self.delta = 0
            self.fire()

        if self.rect.top > Base.HEIGHT:
            self.kill()


    def fire(self):
        self.firing_angle += math.pi/20
        self.fire_angle(self.firing_angle)

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class SentinelCrystal(SingleFireEnemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 1):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/MetalCross.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.lives          = 50
        self.reward         = 100
        self.bullet_origin  = 1
        self.relatives      = []

    def add_relatives(self, relatives):
        self.relatives = relatives

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1
            for relative in self.relatives:
                relative.vel[0] *= -1

        if self.delta > self.firing_rate:
            self.delta = 0
            self.fire()

        if self.rect.top > Base.HEIGHT:
            self.kill()


    def fire(self):
        self.fire_angle(0, (self.rect.width/16, -self.rect.height/16))
        self.fire_angle(math.pi/2, (self.rect.width/16, -self.rect.height/16))
        self.fire_angle(math.pi, (self.rect.width/16, -self.rect.height/16))
        self.fire_angle(3 * math.pi/2, (self.rect.width/16, -self.rect.height/16))

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class BrynhildrCrystal(Enemy):
    def __init__(self, pos, scale, bullet_group, child, vel = [0, 0], kind = 0):
        image      = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/MetalCross.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.total_lives = 600
        self.lives      = self.total_lives
        self.reward     = 300
        self.laser_angle = 0
        self.game_state.on_boss = True
        self.game_state.actual_boss = self
        self.child = child
        self.crystals = []
        self.make_crystals()
        self.passed = False

    def make_crystals(self):
        pos = self.rect.center
        c1 = SentinelCrystal((pos[0] + 2 * ENEMY_STD_SCALE, pos[1] + ENEMY_STD_SCALE), ENEMY_STD_SCALE//2, self.bullet_group, self.vel, self.kind)
        c2 = SentinelCrystal((pos[0] + 2 * ENEMY_STD_SCALE, pos[1] - ENEMY_STD_SCALE), ENEMY_STD_SCALE//2, self.bullet_group, self.vel, self.kind)
        c3 = SentinelCrystal((pos[0] - 2 * ENEMY_STD_SCALE, pos[1] - ENEMY_STD_SCALE), ENEMY_STD_SCALE//2, self.bullet_group, self.vel, self.kind)
        c4 = SentinelCrystal((pos[0] - 2 * ENEMY_STD_SCALE, pos[1] + ENEMY_STD_SCALE), ENEMY_STD_SCALE//2, self.bullet_group, self.vel, self.kind)

        c5 = BunkerCrystal((pos[0] + ENEMY_STD_SCALE, pos[1] + 2 * ENEMY_STD_SCALE), ENEMY_STD_SCALE//2, self.bullet_group, self.vel, self.kind)
        c6 = BunkerCrystal((pos[0] - ENEMY_STD_SCALE, pos[1] + 2 * ENEMY_STD_SCALE), ENEMY_STD_SCALE//2, self.bullet_group, self.vel, self.kind)
        c7 = BunkerCrystal((pos[0] + ENEMY_STD_SCALE, pos[1] - 2 * ENEMY_STD_SCALE), ENEMY_STD_SCALE//2, self.bullet_group, self.vel, self.kind)
        c8 = BunkerCrystal((pos[0] - ENEMY_STD_SCALE, pos[1] - 2 * ENEMY_STD_SCALE), ENEMY_STD_SCALE//2, self.bullet_group, self.vel, self.kind)


        c1.add_relatives([self, c2, c3, c4, c5, c6, c7, c8])
        c2.add_relatives([self, c1, c3, c4, c5, c6, c7, c8])
        c3.add_relatives([self, c1, c2, c4, c5, c6, c7, c8])
        c4.add_relatives([self, c1, c2, c3, c5, c6, c7, c8])
        c5.add_relatives([self, c1, c2, c3, c4, c6, c7, c8])
        c6.add_relatives([self, c1, c2, c3, c4, c5, c7, c8])
        c7.add_relatives([self, c1, c2, c3, c4, c5, c6, c8])
        c8.add_relatives([self, c1, c2, c3, c4, c5, c6, c7])


        self.game_state.enemy_group.add(c1)
        self.game_state.enemy_group.add(c2)
        self.game_state.enemy_group.add(c3)
        self.game_state.enemy_group.add(c4)
        self.game_state.enemy_group.add(c5)
        self.game_state.enemy_group.add(c6)
        self.game_state.enemy_group.add(c7)
        self.game_state.enemy_group.add(c8)


        self.crystals.append(c1)
        self.crystals.append(c2)
        self.crystals.append(c3)
        self.crystals.append(c4)
        self.crystals.append(c5)
        self.crystals.append(c6)
        self.crystals.append(c7)
        self.crystals.append(c8)

    def update(self):
        self.rect.centerx += self.vel[0]
        self.rect.centery += self.vel[1]

        if not self.passed and self.rect.centery > Base.HEIGHT/3:
            self.passed = True

        if self.check_boundaries():
            self.vel[0] *= -1
            for crystal in self.crystals:
                crystal.vel[0] *= -1


        if self.lives / float(self.total_lives) < 0.75:
            self.child.mode = 1
        if self.lives / float(self.total_lives) < 0.5:
            self.child.mode = 2
        if self.lives / float(self.total_lives) < 0.25:
            self.child.mode = 3

        if self.passed and (self.rect.y > Base.HEIGHT/2 or self.rect.y < 0):
            self.vel[1] *= -1
            for crystal in self.crystals:
                crystal.vel[1] *= -1

        pos = self.rect.center
        self.child.rect.center = (pos[0], pos[1] + self.child.rect.height/16)

    def kill(self, opt = None):
        self.game_state.on_boss = False
        self.game_state.actual_boss = None
        self.game_state.boss_killed = True
        self.child.kill()
        for crystal in self.crystals:
            crystal.kill()
        Enemy.kill(self)

class BrynhildrBoss(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 2):
        self.images = []
        self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Grisella/1.png"), (int(8* scale), int(9 * scale))))
        self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Grisella/2.png"), (int(8* scale), int(9 * scale))))
        self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Grisella/3.png"), (int(8* scale), int(9 * scale))))
        self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Grisella/4.png"), (int(8* scale), int(9 * scale))))
        self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Grisella/5.png"), (int(8* scale), int(9 * scale))))
        self.images.append(pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/Grisella/6.png"), (int(8* scale), int(9 * scale))))
        self.image_idx      = 0
        image = self.images[0]

        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.reward         = 100
        self.enemy_group    = self.game_state.enemy_group
        self.scale          = scale
        self.stachels       = []
        self.mode           = 0
        self.spawned        = False
        self.misc_group     = self.game_state.misc_group
        self.fires          = 3
        self.bullet_origin  = 1
        self.firing_angle   = 0

    def update(self):
        self.image_idx = (self.image_idx + 1) % 6
        self.image = self.images[self.image_idx]

        self.delta += 30

        if self.mode == 0:
            if self.delta > 300 and self.fires > 0:
                self.explode()
                self.fires -= 1
                self.delta = 0
            if self.delta > 1000 and self.fires == 0 :
                self.fires = 3
                self.delta = 0

        elif self.mode == 1:
            if self.delta > 500:
                self.spread()
                self.delta = 0

        elif self.mode == 2:
            if self.delta > 160:
                self.firing_angle += math.pi/20
                self.vortex(self.firing_angle)
                self.delta = 0
        else:
            if self.delta > 80:
                self.firing_angle += math.pi/20
                self.bullet_wall(self.firing_angle)
                self.delta = 0

    def vortex(self, angle):
        self.fire_angle(angle, (-self.rect.width/16, -self.rect.height/16))
        self.fire_angle(-angle, (self.rect.width/16, -self.rect.height/16))
        self.fire_angle(angle, (0, 0))
        self.fire_angle(-angle, (0, -self.rect.width/8))

    def bullet_wall(self, angle):
        step = 2 * math.pi / 5
        self.fire_angle(angle, (0, -self.rect.height/16))
        self.fire_angle(angle + step, (0, -self.rect.height/16))
        self.fire_angle(angle + 2 * step, (0, -self.rect.height/16))
        self.fire_angle(angle + 3 * step, (0, -self.rect.height/16))
        self.fire_angle(angle + 4 * step, (0, -self.rect.height/16))

    def explode(self):
        angle = 0

        for i in range(10):
            angle += math.pi / 5
            self.fire_angle(angle, (0, -self.rect.height/16))

    def fire_angle(self, angle, displacement = (0, 0)):
        Enemy.fire_angle(self, angle, displacement)

    def spread(self, position_var = (0, 0), speed = BULLET_SPEED):
        for angle in [math.pi, 0]:
            step = math.pi / 8.0
            self.fire_angle_spring(angle + step, (0, -self.rect.height/16), speed)
            self.fire_angle_spring(angle - step, (0, -self.rect.height/16), speed)
            self.fire_angle_spring(angle, (0, -self.rect.height/16), speed)


    def fire_angle_spring(self, angle = math.pi, position_var = (0, 0), speed = BULLET_SPEED):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        angle += math.pi / 2

        vel_x = math.cos(angle)
        vel_y = math.sin(angle)
        bullet_vel = []
        pos = list(self.rect.center)

        pos[0] += 0
        pos[1] += -self.rect.height/16

        bullet_vel.append(vel_x * speed)
        bullet_vel.append(vel_y * speed)
        self.bullet_group.add(ShortSpringBullet(pos, BULLET_WIDTH, bullet_vel, self.game_state))

class ErikaStachel1(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 2):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Stachel.png"), (scale//2, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 15
        self.reward         = 100
        self.binding_group  = None
        self.firing_mode    = 0
        self.delta2         = 0
        self.firing_angle   = 0
        self.bursting       = 0


    def update(self):
        self.delta  += 35
        self.delta2 += 35

        if self.firing_mode == 0:
            if self.delta > 900:
                self.spread_at_player()
                self.delta = 0
        elif self.firing_mode == 1:
            if self.delta > 160:
                self.firing_angle += math.pi/20
                self.delta = 0
                self.fire_angle(self.firing_angle)
        else:
            if self.delta > 90 and self.bursting > 0:
                self.fire_angle(0)
                self.fire_angle(math.pi/8, (-BULLET_WIDTH, 0))
                self.fire_angle(-math.pi/8, (BULLET_WIDTH, 0))
                self.delta = 0
                self.bursting -= 1
            elif self.delta > 2000:
                self.bursting = 12
                self.delta = 0

        if self.delta2 > 4000:
            if self.firing_mode == 2:
                self.firing_mode = 0
            else:
                self.firing_mode += 1
            self.delta2 = 0

    def spread_at_player(self, position_var = (0, 0), speed = 2 * BULLET_SPEED):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if to_player[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2

        self.fire_angle(angle, position_var, speed)
        self.fire_angle(angle + math.pi/3, position_var, speed)
        self.fire_angle(angle - math.pi/3, position_var, speed)
        self.fire_angle(angle + math.pi/5, position_var, speed)
        self.fire_angle(angle - math.pi/5, position_var, speed)

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class ErikaStachel2(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Stachel.png"), (scale//2, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.lives          = 15
        self.reward         = 100
        self.binding_group  = None
        self.firing_mode    = 0
        self.delta2         = 0
        self.firing_angle   = 0
        self.bursting       = 0
        self.enemy_group    = self.game_state.enemy_group
        self.scale          = scale


    def update(self):
        self.delta  += 35
        self.delta2 += 35

        if self.firing_mode == 0:
            if self.delta > 900:
                self.giant_bullet_at_player()
                self.delta = 0
        elif self.firing_mode == 1:
            if self.delta > 900:
                self.fire_following_bullet()
                self.delta = 0
        else:
            if self.delta > 900:
                self.enemy_group.add(Blatt(self.rect.bottomleft, self.scale, self.bullet_group, (self.vel[0], 2), self.kind))
                self.delta = 0

        if self.delta2 > 4000:
            if self.firing_mode == 2:
                self.firing_mode = 0
            else:
                self.firing_mode += 1
            self.delta2 = 0



    def fire_following_bullet(self):
        if self.bullet_origin == 0:
            pos = list(self.rect.midbottom)
        else:
            pos = list(self.rect.center)

        self.bullet_group.add(FollowingBullet(pos, BULLET_WIDTH // 2, [int(1.5 * BULLET_SPEED), 2 * BULLET_SPEED + self.vel[1]], self.game_state, self.kind))

    def giant_bullet_at_player(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        self.fire_dir([0, 0], to_player, BULLET_SPEED // 2, 5 * BULLET_WIDTH)

    def spread_at_player(self, position_var = (0, 0), speed = 2 * BULLET_SPEED):
        to_player = (self.game_state.player.rect.center[0] - self.rect.center[0], self.game_state.player.rect.center[1] - self.rect.center[1])
        if to_player[0] != 0:
            angle = math.atan2(to_player[1],to_player[0])
            disp_x = 30 * math.sin(angle + math.pi/2)
            disp_y = 30 * math.cos(angle + math.pi/2)
        else:
            disp_x = 30
            disp_y = 0
            if to_player[1] < self.rect.centery:
                angle = 3 * math.pi / 2
            else:
                angle = math.pi/2

        angle -= math.pi/2

        self.fire_angle(angle, position_var, speed)
        self.fire_angle(angle + math.pi/3, position_var, speed)
        self.fire_angle(angle - math.pi/3, position_var, speed)
        self.fire_angle(angle + math.pi/5, position_var, speed)
        self.fire_angle(angle - math.pi/5, position_var, speed)

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class ErikaStachel3(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Stachel.png"), (scale//2, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.delta2         = 0
        self.delta3         = 0
        self.lives          = 15
        self.reward         = 100
        self.binding_group  = None
        self.firing         = True
        self.enemy_group    = self.game_state.enemy_group
        self.scale          = scale



    def update(self):
        self.delta  += 35
        self.delta2 += 35
        self.delta3 += 35

        if self.delta > 1200 and self.firing:
            self.fire_dir([0, 0], [1, 2], BULLET_SPEED, 2 * BULLET_WIDTH)
            self.fire_dir([0, 0], [-1, 2], BULLET_SPEED, 2 * BULLET_WIDTH)
            self.delta = 0

        if self.delta2 > 180 and self.firing:
            self.fire_dir()
            self.delta2 = 0
        if self.delta3 > 2000:
            self.firing = not self.firing
            self.delta3 = 0

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class ErikaStachel4(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Stachel.png"), (scale//2, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)

        self.delta          = 0
        self.delta2         = 0
        self.delta3         = 0
        self.lives          = 15
        self.reward         = 100
        self.binding_group  = None
        self.firing         = True
        self.enemy_group    = self.game_state.enemy_group
        self.scale          = scale

    def update(self):
        self.delta  += 35
        self.delta2 += 35
        self.delta3 += 35

        if self.delta > 2000:
            self.game_state.enemy_group.add(RocketEnemy(self.rect.midbottom, ENEMY_STD_SCALE/2, self.bullet_group, (0, 2*BULLET_SPEED)))
            self.delta = 0

    def kill(self, opt = 1):
        if opt > 0:
            Enemy.kill(self)

class Erika(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 4):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level4/Erika.png"), (int(3* scale), int(3 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.game_state.on_boss = True
        self.game_state.actual_boss = self
        self.misc_group = self.game_state.misc_group
        self.scale = scale
        self.lives = 800
        self.total_lives = self.lives
        self.damage_taken = 0
        self.bursting = 0
        self.spawning = True
        self.fire_mode = 0
        self.stachels = []
        self.spawn_stachels(0)
        self.v_speed        = vel[0]
        self.diving = False

    def spawn_stachels(self, mode):
        for stach in self.stachels:
            stach.kill()

        if mode == 0:
            left = list(self.rect.topleft)
            left[0] -= ENEMY_STD_SCALE
            farleft = list(left)
            farleft[0] -= ENEMY_STD_SCALE
            farleft[1] += ENEMY_STD_SCALE/2

            right = list(self.rect.topright)
            right[0] += ENEMY_STD_SCALE
            farright = list(right)
            farright[0] += ENEMY_STD_SCALE
            farright[1] += ENEMY_STD_SCALE/2


            s1 = ErikaStachel1(left, self.scale, self.bullet_group, self.vel, self.kind)
            s2 = ErikaStachel1(right, self.scale, self.bullet_group, self.vel, self.kind)
            s3 = ErikaStachel1(farleft, self.scale, self.bullet_group, self.vel, self.kind)
            s4 = ErikaStachel1(farright, self.scale, self.bullet_group, self.vel, self.kind)
            s1.binding_group = [self, s2, s3, s4]
            s2.binding_group = [self, s1, s3, s4]
            s3.binding_group = [self, s1, s2, s4]
            s4.binding_group = [self, s1, s2, s3]

            self.stachels.extend([s1,s2,s3,s4])

            self.misc_group.add(s1)
            self.misc_group.add(s2)
            self.misc_group.add(s3)
            self.misc_group.add(s4)

        elif mode == 1:
            left = list(self.rect.midbottom)
            left[0] -= ENEMY_STD_SCALE
            farleft = list(left)
            farleft[0] -= ENEMY_STD_SCALE
            farleft[1] -= ENEMY_STD_SCALE

            right = list(self.rect.midbottom)
            right[0] += ENEMY_STD_SCALE
            farright = list(right)
            farright[0] += ENEMY_STD_SCALE
            farright[1] -= ENEMY_STD_SCALE


            s1 = ErikaStachel2(left, self.scale, self.bullet_group, self.vel, self.kind)
            s2 = ErikaStachel2(right, self.scale, self.bullet_group, self.vel, self.kind)
            s3 = ErikaStachel2(farleft, self.scale, self.bullet_group, self.vel, self.kind)
            s4 = ErikaStachel2(farright, self.scale, self.bullet_group, self.vel, self.kind)
            s1.binding_group = [self, s2, s3, s4]
            s2.binding_group = [self, s1, s3, s4]
            s3.binding_group = [self, s1, s2, s4]
            s4.binding_group = [self, s1, s2, s3]

            self.stachels.extend([s1,s2,s3,s4])

            self.misc_group.add(s1)
            self.misc_group.add(s2)
            self.misc_group.add(s3)
            self.misc_group.add(s4)

        elif mode == 2:
            left = list(self.rect.midbottom)
            left[0] -= ENEMY_STD_SCALE
            farleft = list(left)
            farleft[0] -= ENEMY_STD_SCALE
            farleft[1] -= ENEMY_STD_SCALE

            right = list(self.rect.midbottom)
            right[0] += ENEMY_STD_SCALE

            farright = list(right)
            farright[0] += ENEMY_STD_SCALE
            farright[1] -= ENEMY_STD_SCALE


            s1 = ErikaStachel3(left, self.scale, self.bullet_group, self.vel, self.kind)
            s2 = ErikaStachel3(right, self.scale, self.bullet_group, self.vel, self.kind)
            s3 = ErikaStachel3(farleft, self.scale, self.bullet_group, self.vel, self.kind)
            s4 = ErikaStachel3(farright, self.scale, self.bullet_group, self.vel, self.kind)
            s1.binding_group = [self, s2, s3, s4]
            s2.binding_group = [self, s1, s3, s4]
            s3.binding_group = [self, s1, s2, s4]
            s4.binding_group = [self, s1, s2, s3]

            self.stachels.extend([s1,s2,s3,s4])

            self.misc_group.add(s1)
            self.misc_group.add(s2)
            self.misc_group.add(s3)
            self.misc_group.add(s4)

        elif mode == 3:
            left = list(self.rect.midbottom)
            left[0] -= ENEMY_STD_SCALE
            farleft = list(left)
            farleft[0] -= ENEMY_STD_SCALE
            farleft[1] -= ENEMY_STD_SCALE

            right = list(self.rect.midbottom)
            right[0] += ENEMY_STD_SCALE

            farright = list(right)
            farright[0] += ENEMY_STD_SCALE
            farright[1] -= ENEMY_STD_SCALE


            s1 = ErikaStachel4(left, self.scale, self.bullet_group, self.vel, self.kind)
            s2 = ErikaStachel4(right, self.scale, self.bullet_group, self.vel, self.kind)
            s3 = ErikaStachel4(farleft, self.scale, self.bullet_group, self.vel, self.kind)
            s4 = ErikaStachel4(farright, self.scale, self.bullet_group, self.vel, self.kind)
            s1.binding_group = [self, s2, s3, s4]
            s2.binding_group = [self, s1, s3, s4]
            s3.binding_group = [self, s1, s2, s4]
            s4.binding_group = [self, s1, s2, s3]

            self.stachels.extend([s1,s2,s3,s4])

            self.misc_group.add(s1)
            self.misc_group.add(s2)
            self.misc_group.add(s3)
            self.misc_group.add(s4)
            self.diving = True

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        for stach in self.stachels:
            stach.rect.centerx += self.vel[0]
            stach.rect.centery += self.vel[1]

        if self.damage_taken > self.total_lives / 5:
            self.fire_mode += 1
            self.damage_taken = 0
            self.spawn_stachels(self.fire_mode)
        if (not self.diving and self.rect.centery > Base.HEIGHT / 2) or (not self.spawning and self.rect.centery < 0):
            self.vel[1] *= -1
            self.spawning = False

        if self.rect.centery > Base.HEIGHT + self.rect.height:
            self.rect.centery = 0
            self.spawn_stachels(self.fire_mode)

        if self.fire_mode == 0:
            self.delta += 30

            if self.delta > 90 and self.bursting > 0:
                self.fire_angle(0)
                self.fire_angle(math.pi/8, (-BULLET_WIDTH, 0))
                self.fire_angle(-math.pi/8, (BULLET_WIDTH, 0))
                self.delta = 0
                self.bursting -= 1
            elif self.delta > 2000:
                self.bursting = 12
                self.delta = 0

        elif self.fire_mode == 1:
            self.delta += 30
            if self.delta > 1500:
                self.explode()
                self.delta = 0

        elif self.fire_mode == 2:
            self.delta += 30
            if abs(self.rect.centerx - self.game_state.player.rect.centerx) < abs(self.v_speed):
                self.vel[0] = 0
            elif self.rect.centerx > self.game_state.player.rect.centerx:
                self.vel[0] = self.v_speed
                self.vel[0] = -abs(self.vel[0])
            else:
                self.vel[0] = self.v_speed
                self.vel[0] = abs(self.vel[0])

            if self.delta > 60 and abs(self.rect.y - self.game_state.player.rect.y) < 2 * self.rect.height:
                self.fire_dir([0, 0], [0, 1], 3 * BULLET_SPEED, BULLET_WIDTH)
                self.delta = 0

        elif self.fire_mode == 3:
            if abs(self.rect.centerx - self.game_state.player.rect.centerx) < abs(self.v_speed):
                self.vel[0] = 0
            elif self.rect.centerx > self.game_state.player.rect.centerx:
                self.vel[0] = self.v_speed
                self.vel[0] = -abs(self.vel[0])
            else:
                self.vel[0] = self.v_speed
                self.vel[0] = abs(self.vel[0])

        elif self.fire_mode == 4:
            self.delta += 30
            if self.rect.centery - self.rect.height > ENEMY_STD_SCALE:
                self.vel[1] = -self.v_speed
            elif self.rect.centery - self.rect.height < ENEMY_STD_SCALE:
                self.vel[1] = self.v_speed
            else:
                self.vel[1] = 0

            if self.delta > 90 and self.bursting > 0:
                self.fire_dir([BULLET_WIDTH, 0])
                self.fire_dir([2*BULLET_WIDTH, 0])
                self.fire_dir([-BULLET_WIDTH, 0])
                self.fire_dir([-2*BULLET_WIDTH, 0])
                self.fire_dir([0, 0])
                self.delta = 0
                self.bursting -= 1
            elif self.delta > 1000:
                self.spawn_stachels(random.randint(0,3))
                for stach in self.stachels:
                    stach.vel[0] = self.vel[0]
                    stach.vel[1] = self.vel[1]
                self.bursting = 20
                self.delta = 0

        if self.check_boundaries():
            self.vel[0] *= -1

    def hit(self, value):
        self.damage_taken += value
        Enemy.hit(self, value)

    def explode(self):
        angle = 0

        for i in range(16):
            angle += math.pi / 8
            self.fire_angle(angle)

    def kill(self, opt = None):
        self.game_state.on_boss = False
        self.game_state.actual_boss = None
        self.game_state.boss_killed = True
        for stach in self.stachels:
            stach.kill()
        Enemy.kill(self)

class Malphas(Enemy):
        def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
            image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Malphas.png"), (int(1.2 * scale), int(1.2 * scale)))
            Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
            self.real_pos = map(float, self.rect)
            self.reward = 400
            self.lives  = 10
            self.delta  = 0
            self.firing_angle = 0

        def fire_angle(self, angle = 0, position_var = (0, 0), speed = BULLET_SPEED):
            enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
            speed += enemy_mag

            angle += math.pi / 2
            vel_x = math.cos(angle)
            vel_y = math.sin(angle)
            bullet_vel = []
            pos = list(self.rect.center)

            pos[0] += position_var[0]
            pos[1] += position_var[1]

            bullet_vel.append(vel_x * speed)
            bullet_vel.append(vel_y * speed)
            self.bullet_group.add(Bullet(pos, BULLET_WIDTH, bullet_vel, self.game_state, self.kind))

        def update(self):
            self.real_pos[0] += self.vel[0]
            self.real_pos[1] += self.vel[1]

            self.rect.x = self.real_pos[0]
            self.rect.y = self.real_pos[1]
            self.delta  += 35

            if self.check_boundaries():
                self.vel[0] *= -1

            if self.delta > 160:
                self.firing_angle += math.pi/20
                self.delta = 0
                self.fire_angle(self.firing_angle)
                self.fire_angle(self.firing_angle + math.pi/2)
                self.fire_angle(self.firing_angle + math.pi)
                self.fire_angle(self.firing_angle + 3 * math.pi/2)

            if self.rect.centery > 1.1 * Base.HEIGHT:
                self.kill()

class Forneus(Enemy):
        def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
            image           = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Forneus.png"), (scale, 2 * scale))
            Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
            self.real_pos   = map(float, self.rect)
            self.reward     = 400
            self.lives      = 10
            self.delta      = 0
            self.bursting   = 0

        def update(self):
            self.real_pos[0] += self.vel[0]
            self.real_pos[1] += self.vel[1]

            self.rect.x = self.real_pos[0]
            self.rect.y = self.real_pos[1]
            self.delta  += 35

            if self.check_boundaries():
                self.vel[0] *= -1

            if self.delta > 1200:
                self.bursting = 3
                self.delta = 0

            if self.delta > 160 and self.bursting > 0:
                self.delta = 0
                self.bursting -= 1
                self.fire_dir()

            if self.rect.centery > 1.1 * Base.HEIGHT:
                self.kill()

class Eligor(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image           = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Eligor.png"), (scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.real_pos   = map(float, self.rect)
        self.reward     = 400
        self.lives      = 10
        self.delta      = 0
        self.bursting   = 0

    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]

        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 1200:
            self.bursting = 3
            self.delta = 0

        if self.delta > 160 and self.bursting > 0:
            self.delta = 0
            self.bursting -= 1
            self.fire_dir()
            self.fire_angle(math.pi/4)
            self.fire_angle(-math.pi/4)

        if self.rect.centery > 1.1 * Base.HEIGHT:
            self.kill()

class Botis(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image           = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Botis.png"), (scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.real_pos   = map(float, self.rect)
        self.reward     = 400
        self.lives      = 10
        self.delta      = 0
        self.bursting   = 10

    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]

        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 2400:
            self.bursting = 10
            self.delta = 0

        if self.delta > 120 and self.bursting > 0:
            self.delta = 0
            self.bursting -= 1
            self.fire_dir()

        if self.rect.centery > 1.1 * Base.HEIGHT:
            self.kill()

class Valefor(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image           = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Valefor.png"), (scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.real_pos   = map(float, self.rect)
        self.reward     = 400
        self.lives      = 10
        self.delta      = 0
        self.bursting   = 4

    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]

        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 1200:
            self.bursting = 4
            self.delta = 0

        if self.delta > 120 and self.bursting > 0:
            self.delta = 0
            self.bursting -= 1
            self.fire_at_player([0, 0], 2 * BULLET_SPEED)

        if self.rect.centery > 1.1 * Base.HEIGHT:
            self.kill()

class ExplosiveBullet(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 2], kind = 1):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Malachite.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.kind = kind

        self.lives  = 6
        self.reward = 1000
        self.delta  = 0

    def update(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.midbottom[0], self.game_state.player.rect.center[1] - self.rect.midbottom[1])
        mag = math.sqrt(to_player[0] ** 2 + to_player[1] ** 2)
        if mag == 0:
            vel_x = 0
        else:
            vel_x =  BULLET_SPEED * to_player[0] / mag
        vel_y = self.vel[1]

        self.rect.x += vel_x
        self.rect.y += vel_y
        self.delta  += 50

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def kill(self, opt = -1):
        self.explode()
        Enemy.kill(self)

    def explode(self):
        for angle in range(16):
            self.fire_angle(angle * math.pi/8)

class Decarabia(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image           = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Decarabia.png"), (scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.real_pos   = map(float, self.rect)
        self.reward     = 400
        self.lives      = 10
        self.delta      = 0

    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]

        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 2500:
            self.fire_at_player()
            self.delta = 0


        if self.rect.centery > 1.1 * Base.HEIGHT:
            self.kill()

    def fire_dir(self, position_var = [0, 0], direction = [0, 1], speed = BULLET_SPEED, size =  ENEMY_STD_SCALE):
        enemy_mag = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
        speed += enemy_mag

        direction = list(direction)
        position_var = list(position_var)
        magnitude = float(math.sqrt(direction[0] ** 2 + direction[1] ** 2))


        if magnitude > 1:
            direction[0] = speed * direction[0] / magnitude
            direction[1] = speed * direction[1] / magnitude
        else:
            direction[0] *= speed
            direction[1] *= speed

        if magnitude == 0:
            magnitude = 1

        if self.bullet_origin == 0:
            pos = list(self.rect.midbottom)
        else:
            pos = list(self.rect.center)

        pos[0] += position_var[0]
        pos[1] += position_var[1]

        self.game_state.enemy_group.add(ExplosiveBullet(pos, 2 * ENEMY_STD_SCALE, self.bullet_group, direction, self.kind))

class Barbatos(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image           = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Barbatos.png"), (2 * scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward     = 400
        self.lives      = 10
        self.delta      = 0
        self.bursting   = 8

    def update(self):

        self.rect.centerx += self.vel[0]
        self.rect.centery += self.vel[1]
        self.delta  += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 1200:
            self.bursting = 8
            self.delta = 0

        if self.delta > 120 and self.bursting > 0:
            self.delta = 0
            self.bursting -= 1
            self.fire_dir()
            self.fire_angle(math.pi/3)
            self.fire_angle(2 * math.pi/3)
            self.fire_angle(-math.pi/3)
            self.fire_angle(-2 * math.pi/3)



        if self.rect.centery > 1.1 * Base.HEIGHT:
            self.kill()

class XRocket(Enemy):
    def __init__(self, pos, scale, bullet_group, vel, kind, time):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level3/V2.png"), (0, 0))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.scale = scale
        self.kind = kind

        self.lives  = 3
        self.reward = 1000
        self.delta  = 0
        self.time = time

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta  += 50

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            self.explode()

        if self.delta > self.time:
            self.explode()

    def explode(self):
        angle = 0

        for i in range(8):
            angle += math.pi / 4
            self.fire_angle(angle)
        self.kill()

class Baalberith(Enemy):
    def __init__(self, pos, scale, bullet_group, vel, kind = 1):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Baalberith.png"), (scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.scale = scale
        self.lives  = 10
        self.reward = 1000

    def kill(self, opt = 1):
        if opt != -1:
            self.explode()
        Enemy.kill(self, opt)

    def explode(self):
        for i in range(5):
            self.game_state.enemy_group.add(XRocket(self.rect.center, self.scale, self.bullet_group, self.vel, self.kind, 300 * i))
        for angle in range(16):
            self.fire_angle(angle * math.pi/8)

class Astaroth(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 0):
        image           = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Astaroth.png"), (scale, 2 * scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.real_pos   = map(float, self.rect)
        self.reward     = 400
        self.lives      = 10
        self.delta      = 0
        self.delta2     = 0
        self.bursting   = 0
        self.bursting2  = 0

    def update(self):
        self.real_pos[0] += self.vel[0]
        self.real_pos[1] += self.vel[1]

        self.rect.x = self.real_pos[0]
        self.rect.y = self.real_pos[1]
        self.delta  += 35
        self.delta2 += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 120 and self.bursting2 > 0:
            self.fire_dir()
            self.fire_dir([BULLET_WIDTH,0])
            self.fire_dir([-BULLET_WIDTH,0])
            self.delta = 0
            self.bursting2 -= 1
        elif self.delta > 1400:
            self.delta = 0
            self.spread_on_side()
            self.bursting2 = 12

        if self.delta2 > 120 and self.bursting > 0:
            self.fire_angle_spring(3*math.pi/4, [0, -self.rect.height])
            self.fire_angle_spring(-3*math.pi/4, [0, -self.rect.height])
            self.bursting -= 1
            self.delta2 = 0
        elif self.delta2 > 1000:
            self.bursting = 3
            self.delta2 = 0


        if self.rect.centery > 1.1 * Base.HEIGHT:
            self.kill()

    def spread_on_side(self):
        for angle in [math.pi/3, -math.pi/1.75]:
            for i in range(3):
                self.fire_angle(angle + i * math.pi/ 8, [0, -self.rect.height/2])

class RedStar(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 3], kind = 1):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.kind = kind

        self.lives  = 6
        self.reward = 1000
        self.delta  = 0

    def update(self):
        to_player = (self.game_state.player.rect.center[0] - self.rect.midbottom[0], self.game_state.player.rect.center[1] - self.rect.midbottom[1])
        mag = math.sqrt(to_player[0] ** 2 + to_player[1] ** 2)
        if mag == 0:
            vel_x = 0
        else:
            vel_x =  BULLET_SPEED * to_player[0] / mag
        vel_y = self.vel[1]

        self.rect.x += vel_x
        self.rect.y += vel_y
        self.delta  += 50

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            self.kill()

        if self.rect.bottom < ENEMY_STD_SCALE:
            self.kill()

    def kill(self, opt = -1):
        self.explode()
        Enemy.kill(self)

    def explode(self):
        for angle in range(4):
            self.fire_angle(angle * math.pi/2, (0, 0), 2 * BULLET_SPEED)
            self.fire_angle(angle * math.pi/2)
            self.fire_angle(angle * math.pi/2, (0, 0), BULLET_SPEED / 2)
            self.fire_angle(angle * math.pi/2, (0, 0), BULLET_SPEED / 4)
        for angle in range(16):
            self.fire_angle(angle * math.pi/8)
            self.fire_angle(angle * math.pi/8, (0, 0), BULLET_SPEED / 2)
            self.fire_angle(angle * math.pi/8, (0, 0), BULLET_SPEED / 4)

class StationaryRedStar(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 3], kind = 1):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.kind = kind

        self.lives  = 6
        self.reward = 1000
        self.delta  = 0
        self.timer  = 2300

    def update(self):
        self.delta  += 30
        if self.delta > self.timer:
            to_player = (self.game_state.player.rect.center[0] - self.rect.midbottom[0], self.game_state.player.rect.center[1] - self.rect.midbottom[1])
            mag = math.sqrt(to_player[0] ** 2 + to_player[1] ** 2)
            if mag == 0:
                vel_x = 0
            else:
                vel_x =  BULLET_SPEED * to_player[0] / mag
            vel_y = 3

            self.rect.x += vel_x
            self.rect.y += vel_y
        else:
            self.rect.centerx += self.vel[0]
            self.rect.centery += self.vel[1]

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.rect.top > Base.HEIGHT:
            self.kill()

    def kill(self, opt = -1):
        self.explode()
        Enemy.kill(self)

    def explode(self):
        for angle in range(4):
            self.fire_angle(angle * math.pi/2, (0, 0), 2 * BULLET_SPEED)
            self.fire_angle(angle * math.pi/2)
            self.fire_angle(angle * math.pi/2, (0, 0), BULLET_SPEED / 2)
            self.fire_angle(angle * math.pi/2, (0, 0), BULLET_SPEED / 4)
        for angle in range(16):
            self.fire_angle(angle * math.pi/8)
            self.fire_angle(angle * math.pi/8, (0, 0), BULLET_SPEED / 2)
            self.fire_angle(angle * math.pi/8, (0, 0), BULLET_SPEED / 4)

class ScoutStar(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.firing_rate = 1500
        self.delta2 = 0
        self.bursting = 0

    def update(self):
        self.move_top()
        self.rect.centerx += self.vel[0]
        self.rect.centery += self.vel[1]

        self.delta  += 35
        self.delta2 += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta2 > 120 and self.bursting > 0:
            self.fire_dir()
            self.fire_dir([BULLET_WIDTH, 0])
            self.fire_dir([-BULLET_WIDTH, 0])
            self.bursting -= 1
            self.delta2 = 0
        elif self.delta2 > 1000:
            self.bursting = 3
            for angle in range(-5, 4):
                self.fire_angle(angle * math.pi/12)
            self.delta2 = 0

    def kill(self, opt = 1):
        if opt == 1:
            Enemy.kill(self)

    def move_top(self):
        if self.vel[0] == 0:
            self.vel[0] = 2
            self.move_direction = 0
        if self.rect.y > 2 * ENEMY_STD_SCALE:
            self.vel[1] = -2
        else:
            self.vel[1] = 0

        if self.rect.x <= 0 and self.move_direction == 0:
            self.vel[0] = -2
            self.move_direction = 1
        elif self.rect.x < Base.WIDTH - self.rect.width and self.move_direction == 1:
            self.vel[0] = 2
            self.move_direction = 0

class MorgStachel1(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.firing_rate = 1500
        self.delta2 = 0
        self.delta3 = 0
        self.bursting = 0
        self.bullet_origin = 1

    def update(self):
        self.move_topleft()
        self.rect.centerx += self.vel[0]
        self.rect.centery += self.vel[1]

        self.delta  += 35
        self.delta2 += 35
        self.delta3 += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 90 and self.delta2 > 1000:
            self.fire_angle(-math.pi/2)
            self.fire_dir()
            self.delta = 0

        if self.delta3 > 800:
            for angle in range(0, 12):
                self.fire_angle(-angle * math.pi/24)
            self.delta3 = 0


    def kill(self, opt = 1):
        if opt == 1:
            Enemy.kill(self)

    def move_topleft(self):
        if self.vel[0] == 0:
            self.vel[0] = -2
            self.move_direction = 0
        if self.rect.y > 0:
            self.vel[1] = -2
        else:
            self.vel[1] = 0

        if self.rect.x <= 0:
            self.vel[0] = -2

class MorgStachel2(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.firing_rate = 1500
        self.delta2 = 0
        self.bursting = 0
        self.bullet_origin = 1

    def update(self):
        self.move_topright()
        self.rect.centerx += self.vel[0]
        self.rect.centery += self.vel[1]

        self.delta  += 35
        self.delta2 += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 200 and self.bursting > 0:
            self.fire_angle(math.pi/3)
            self.fire_angle(math.pi/4)
            self.fire_angle(math.pi/5)
            self.bursting -= 1
            self.delta = 0
        elif self.delta > 2000:
            self.bursting = 5
            self.delta = 0

    def kill(self, opt = 1):
        if opt == 1:
            Enemy.kill(self)

    def move_topright(self):
        if self.vel[0] == 0:
            self.vel[0] = 2
            self.move_direction = 0
        if self.rect.y > 0:
            self.vel[1] = -2
        else:
            self.vel[1] = 0

        if self.rect.x < Base.WIDTH - self.rect.width:
            self.vel[0] = 2
        else:
            self.vel[0] = 0

class MorgStachel3(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.firing_rate = 1500
        self.delta2 = 0
        self.bursting = 0
        self.bullet_origin = 1

    def update(self):
        self.move_bottomleft()
        self.rect.centerx += self.vel[0]
        self.rect.centery += self.vel[1]

        self.delta  += 35
        self.delta2 += 35

        if self.check_boundaries():
            self.vel[0] *= -1

        if self.delta > 200 and self.bursting > 0:
            self.fire_angle(math.pi + math.pi/3)
            self.fire_angle(math.pi + math.pi/4)
            self.fire_angle(math.pi + math.pi/5)
            self.bursting -= 1
            self.delta = 0
        elif self.delta > 2000:
            self.bursting = 5
            self.delta = 0

    def kill(self, opt = 1):
        if opt == 1:
            Enemy.kill(self)

    def move_bottomleft(self):
        if self.vel[0] == 0:
            self.vel[0] = -2
            self.move_direction = 0
        if Base.HEIGHT - self.rect.y > self.rect.height:
            self.vel[1] = 2
        else:
            self.vel[1] = 0

        if self.rect.x <= 0:
            self.vel[0] = -2

class MorgStachel4(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 3):
        image  = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Crystals/Pink.png"), (scale, scale))
        Enemy.__init__(self, pos, scale, bullet_group, image, vel, kind)
        self.reward = 400
        self.lives  = 3
        self.firing_rate = 1500
        self.delta2 = 0
        self.delta3 = 0
        self.bursting = 0
        self.bullet_origin = 1
        self.scale = scale

    def update(self):
        self.move_bottomright()
        self.rect.centerx += self.vel[0]
        self.rect.centery += self.vel[1]

        self.delta  += 35
        self.delta2 += 35
        self.delta3 += 35

        if self.delta > 120 and self.delta2 > 2000:
            self.fire_angle(math.pi/2)
            self.fire_angle(math.pi)
            self.delta = 0

        if self.delta3 > 2200:
            self.game_state.enemy_group.add(RedStar(self.rect.center, self.scale, self.bullet_group, [0, -2]))
            self.delta3 = 0

        if self.check_boundaries():
            self.vel[0] *= -1

    def kill(self, opt = 1):
        if opt == 1:
            Enemy.kill(self)

    def move_bottomright(self):
        if self.vel[0] == 0:
            self.vel[0] = 2
            self.move_direction = 0
        if Base.HEIGHT - self.rect.y > self.rect.height:
            self.vel[1] = 2
        else:
            self.vel[1] = 0

        if self.rect.x < Base.WIDTH - self.rect.width:
            self.vel[0] = 2
        else:
            self.vel[0] = 0

class Morgenstern(Enemy):
    def __init__(self, pos, scale, bullet_group, vel = [0, 0], kind = 2):
        image = pygame.transform.scale(pygame.image.load(Base.STD_PATH + "res/Level5/Morgenstern.png"), (int(4 * scale), int(4 * scale)))
        Enemy.__init__(self, pos, scale, bullet_group, image, [0, 4], kind)
        self.game_state.on_boss = True
        self.game_state.actual_boss = self
        self.misc_group = self.game_state.misc_group
        self.scale = scale
        self.lives = 1000
        self.total_lives = self.lives
        self.damage_taken = 0
        self.fire_mode = -1
        self.delta      = 0
        self.delta2     = 0
        self.firing_angle = 0
        self.bullet_origin = 1
        self.bursting = 0
        self.firing_mode = 0
        self.pos_delta = 0
        self.move_direction = 0
        self.firing_angle_speed = math.pi/16
        self.laser_angle        = 0
        #0 for left, 1 for down, 2 for right, 3 for up
        self.spawned = False
        self.spawned_stars = []
        self.spawned_stachels = []

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.delta += 30
        self.delta2 += 30
        if self.damage_taken >= self.total_lives / 10:
            self.fire_mode += 1
            self.damage_taken = 0

        if self.rect.centery > Base.HEIGHT/2 and self.fire_mode == -1:
            self.vel[1] = 0
            self.fire_mode = 0

        if self.fire_mode == 0:
            if self.delta > 4000:
                self.game_state.enemy_group.add(RedStar(self.rect.center, self.scale, self.bullet_group))
                self.delta = 0
        elif self.fire_mode == 1:
            if self.delta > 1200:
                self.firing_angle += math.pi/4
                self.delta = 0
                self.bursting = 5
            elif self.delta > 120 and self.bursting > 0:
                for angle in range(0, 6):
                    self.fire_angle_spring(self.firing_angle + angle * math.pi/3)
                self.bursting -= 1
                self.delta = 0
        elif self.fire_mode == 2:
            self.follow_player()
            if self.firing_mode == 0:
                if self.delta > 1500:
                    for angle in range(1,12):
                        firing_angle = 3 * math.pi/4
                        self.fire_angle_spring(firing_angle + angle * math.pi/24)
                    self.firing_mode = 1
                    self.bursting = 2
                    self.delta = 0
                elif self.delta > 120 and self.bursting > 0:
                    self.fire_angle_spring()
                    self.fire_angle_spring(math.pi/3)
                    self.fire_angle_spring(-math.pi/3)
                    self.delta = 0
                    self.bursting -= 1
            else:
                if self.delta > 1500:
                    for angle in range(1,12):
                        firing_angle = -math.pi/4
                        self.fire_angle_spring(firing_angle + angle * math.pi/24)
                    self.firing_mode = 0
                    self.bursting = 2
                    self.delta = 0
                elif self.delta > 120 and self.bursting > 0:
                    self.fire_angle_spring(math.pi)
                    self.fire_angle_spring(4 * math.pi/3)
                    self.fire_angle_spring(2 * math.pi/3)
                    self.delta = 0
                    self.bursting -= 1
        elif self.fire_mode == 3:
            self.grind_screen()
            self.firing_angle += self.firing_angle_speed
            if self.delta > 180:
                self.fire_angle(self.firing_angle)
                self.fire_angle(math.pi/2 + self.firing_angle)
                self.fire_angle(math.pi + self.firing_angle)
                self.fire_angle(3 * math.pi / 2 + self.firing_angle)
                self.delta = 0
        elif self.fire_mode == 4:
            self.move_center()
            self.firing_angle += math.pi/16
            self.laser_angle += math.pi/150
            if self.delta > 200:
                self.fire_angle(self.firing_angle)
                self.fire_angle(self.firing_angle + math.pi/2)
                self.fire_angle(self.firing_angle + math.pi)
                self.fire_angle(self.firing_angle + 3 * math.pi/2)
                self.delta = 0
            if self.delta2 > 90:
                self.fire_angle(self.laser_angle)
                self.fire_angle(self.laser_angle + math.pi/2)
                self.fire_angle(self.laser_angle + math.pi)
                self.fire_angle(self.laser_angle + 3 * math.pi/2)
                self.delta2 = 0
        elif self.fire_mode == 5:
            self.move_top()
            if self.delta > 1200:
                self.fire_angle_spring(math.pi/6)
                self.fire_angle_spring(2 * math.pi/6)
                self.fire_angle_spring(math.pi/2)
                self.fire_angle_spring(-2 * math.pi/6)
                self.fire_angle_spring(-math.pi/2)
                self.fire_angle_spring(-math.pi/6)
                self.delta = 0
            if self.delta2 > 3000:
                self.bursting = 5
                self.delta2 = 0
            elif self.delta2 > 120 and self.bursting > 0:
                self.fire_dir()
                self.fire_dir([BULLET_WIDTH, 0])
                self.fire_dir([-BULLET_WIDTH, 0])
                self.delta2 = 0
                self.bursting -= 1
        elif self.fire_mode == 6:
            self.move_center()
            if self.delta > 200 and self.bursting == 0:
                self.game_state.enemy_group.add(StationaryRedStar(self.rect.center, self.scale, self.bullet_group, [0, 2]))
                self.game_state.enemy_group.add(StationaryRedStar(self.rect.center, self.scale, self.bullet_group, [0, -2]))
                self.game_state.enemy_group.add(StationaryRedStar(self.rect.center, self.scale, self.bullet_group, [2, 0]))
                self.game_state.enemy_group.add(StationaryRedStar(self.rect.center, self.scale, self.bullet_group, [-2, 0]))
                self.bursting = 1
                self.delta = 0
                self.delta2 = 0
            if self.delta2 > 3000 and self.bursting == 1:
                for angle in range(1, 36):
                    self.fire_angle(angle * math.pi/18)
                    self.delta2 = 0
                self.bursting = 0
        elif self.fire_mode == 7:
            self.move_top()
            if not self.spawned:
                self.spawn_stars()
                self.spawned = True
            if self.delta > 2400:
                for angle in range(-18, 17):
                    self.fire_angle(angle*math.pi/36)
                self.delta = 0
        elif self.fire_mode == 8 or self.fire_mode == 9:
            self.move_center()
            if self.spawned:
                for star in self.spawned_stars:
                    star.kill()
                self.spawned = False
                self.spawn_stachels()

        if self.check_boundaries():
            self.vel[0] *= -1

    def kill(self, opt = 1):
        self.game_state.boss_killed = True
        for stachel in self.spawned_stachels:
            stachel.kill()
        Enemy.kill(self, opt)

    def hit(self, value):
        if self.fire_mode >= 0:
            self.damage_taken += value
            Enemy.hit(self, value)

    def spawn_stachels(self):
        S1 = MorgStachel1(self.rect.center, self.scale, self.bullet_group)
        S2 = MorgStachel2(self.rect.center, self.scale, self.bullet_group)
        S3 = MorgStachel3(self.rect.center, self.scale, self.bullet_group)
        S4 = MorgStachel4(self.rect.center, self.scale, self.bullet_group)
        self.spawned_stachels.extend([S1,S2,S3,S4])
        for stachel in self.spawned_stachels:
            self.game_state.enemy_group.add(stachel)

    def spawn_stars(self):
        firsts_pos = list(self.rect.center)
        firsts_pos[0] += self.rect.width/2
        seconds_pos = list(self.rect.center)
        seconds_pos[0] -= self.rect.width/2
        S1 = ScoutStar(firsts_pos, self.scale, self.bullet_group)
        S2 = ScoutStar(seconds_pos, self.scale, self.bullet_group)
        S3 = ScoutStar(self.rect.center, self.scale, self.bullet_group)
        self.game_state.enemy_group.add(S1)
        self.game_state.enemy_group.add(S2)
        self.game_state.enemy_group.add(S3)
        self.spawned_stars.extend([S1,S2,S3])

    def move_top(self):
        if self.vel[0] == 0:
            self.vel[0] = 2
            self.move_direction = 0
        if self.rect.y > 0:
            self.vel[1] = -2
        else:
            self.vel[1] = 0

        if self.rect.x <= 0 and self.move_direction == 0:
            self.vel[0] = -(2 + self.damage_taken/(self.total_lives/10))
            self.move_direction = 1
        elif self.rect.x < Base.WIDTH - self.rect.width and self.move_direction == 1:
            self.vel[0] = (2 + self.damage_taken/(self.total_lives/10))
            self.move_direction = 0

    def move_center(self):
        if self.rect.centerx > Base.WIDTH/2:
            self.vel[0] = -1
        elif self.rect.centerx < Base.WIDTH/2:
            self.vel[0] = 1
        else:
            self.vel[0] = 0

        if self.rect.centery > Base.HEIGHT/2:
            self.vel[1] = -1
        elif self.rect.centery < Base.HEIGHT/2:
            self.vel[1] = 1
        else:
            self.vel[1] = 0

    def follow_player(self):
        if self.rect.centerx > self.game_state.player.rect.centerx:
            self.vel[0] = -1
        elif self.rect.centerx < self.game_state.player.rect.centerx:
            self.vel[0] = 1
        else:
            self.vel[0] = 0

    def grind_screen(self):
        self.firing_angle_speed = (1 + self.damage_taken/(self.total_lives/10)) * math.pi/16
        if self.damage_taken > self.total_lives/1.5 and self.delta2 > 2000:
            for angle in range(0, 12):
                self.fire_angle(angle * math.pi/6)
            self.delta2 = 0

        if self.move_direction == 0 and self.rect.x > 0:
            self.vel[0] = -1
            self.vel[1] = 0
        elif self.move_direction == 1 and Base.HEIGHT - self.rect.y > self.rect.height:
            self.vel[1] = 1
            self.vel[0] = 0
        elif self.move_direction == 2 and self.rect.x < Base.WIDTH - self.rect.width:
            self.vel[1] = 0
            self.vel[0] = 1
        elif self.move_direction == 3 and self.rect.y > 0:
            self.vel[1] = -1
            self.vel[0] = 0
        else:
            self.move_direction = (self.move_direction + 1) % 4
            self.vel[1] = 0
            self.vel[0] = 0
