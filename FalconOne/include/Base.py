SINGLE_FIRE     = 0
DUAL_FIRE       = 1
TRIPLE_FIRE     = 2
SPECIAL_FIRE    = 3
STD_PATH        = ""
WIDTH, HEIGHT   = 600, 700

class GameState:
    def __init__(self, player = None):
        self.gameOver   = False
        self.points     = 0
        self.player     = player
        self.step       = 0
        self.step_done  = False
        self.level      = 1
        self.on_boss    = False
        self.enemy_group = None
        self.actual_boss = None
        self.boss_waiting = False
        self.boss_cmd = None
        self.boss_killed = False
        self.misc_group = None
        self.started        = False

    def add_misc_group(self, misc_group):
        self.misc_group = misc_group

    def restart_game(self):
        self.gameOver = False
        self.points = 0
        self.step = 0
        self.step_done = False
        self.level = 1
        self.on_boss = False
        if self.actual_boss != None:
            self.actual_boss.kill()
            self.actual_boss = None
        self.boss_killed = False

    def next_level(self):
        self.step = 0
        self.step_done = False
        self.level +=1
        self.on_boss = False
        self.actual_boss = None

    def restart_level(self):
        self.on_boss = False
        self.step = 0
        self.step_done = False
        if self.actual_boss != None:
            self.actual_boss.kill()
            self.actual_boss = None
        self.boss_killed = False

    def add_player(self, player):
        self.player     = player

    def add_enemy_group(self, enemy_group):
        self.enemy_group = enemy_group

    def start_boss(self, boss):
        self.actual_boss = boss

    def actual_boss_percentage(self):
        return 1.0 * self.actual_boss.lives / self.actual_boss.total_lives

STD_GAME_STATE  = GameState()

class GameCommand:
    def __init__(self, cmmd):
        split_commands = cmmd.split(" ")
        self.entity = split_commands[0]
        self.pos    = split_commands[1]
        self.vel    = split_commands[2]

    def render(self):
        if self.entity == "UpgradeCarrier":
            return "enemy_group.add(SimpleCarrier({0}, ENEMY_STD_SCALE, item_group, \"U\", {1}))".format(self.pos, self.vel)
        elif self.entity == "PointCarrier":
            return "enemy_group.add(SimpleCarrier({0}, ENEMY_STD_SCALE, item_group, \"P\", {1}))".format(self.pos, self.vel)
        elif self.entity == "BombCarrier":
            return "enemy_group.add(SimpleCarrier({0}, ENEMY_STD_SCALE, item_group, \"B\", {1}))".format(self.pos, self.vel)
        elif self.entity == "LifeCarrier":
            return "enemy_group.add(SimpleCarrier({0}, ENEMY_STD_SCALE, item_group, \"L\", {1}))".format(self.pos, self.vel)
        elif self.entity == "make_enemy_triangle":
            return "make_enemy_triangle({0}, {1})".format(self.pos, self.vel)
        elif self.entity == "make_enemy_ship":
            return "make_enemy_ship({0}, {1}, \"Default\")".format(self.pos, self.vel)
        elif self.entity == "make_tank":
            return "make_enemy_tank({0}, {1}, \"Default\")".format(self.pos, self.vel)
        elif self.entity == "make_thin_tank":
            return "make_enemy_tank({0}, {1}, \"Thin\")".format(self.pos, self.vel)
        elif self.entity == "make_small_tank":
            return "make_enemy_tank({0}, {1}, \"Small\")".format(self.pos, self.vel)
        elif self.entity == "make_small_cannon_ship":
            return "make_enemy_ship({0}, {1}, \"Small\")".format(self.pos, self.vel)
        elif self.entity == "make_thin_cannon_ship":
            return "make_enemy_ship({0}, {1}, \"Thin\")".format(self.pos, self.vel)
        elif self.entity == "make_rocket_triangle":
            return "make_rocket_triangle({0}, {1})".format(self.pos, self.vel)
        elif self.entity == "Fabric1":
            return "enemy_group.add(Fabric({1}, ENEMY_STD_SCALE, enemy_bullets, {2}, 0))".format(self.entity, self.pos, self.vel)
        elif self.entity == "Fabric2":
            return "enemy_group.add(Fabric({1}, ENEMY_STD_SCALE, enemy_bullets, {2}, 1))".format(self.entity, self.pos, self.vel)
        elif self.entity == "Fabric3":
            return "enemy_group.add(Fabric({1}, ENEMY_STD_SCALE, enemy_bullets, {2}, 2))".format(self.entity, self.pos, self.vel)
        elif self.entity == "Alessia":
            return "start_boss_Alessia({0}, {1})".format(self.pos, self.vel)
        elif self.entity == "Georgia":
            return "start_boss_Georgia({0}, {1})".format(self.pos, self.vel)
        elif self.entity == "Brynhildr":
            return "start_boss_Brynhildr({0}, {1})".format(self.pos, self.vel)
        else:
            return "enemy_group.add({0}({1}, ENEMY_STD_SCALE, enemy_bullets, {2}))".format(self.entity, self.pos, self.vel)
    def __str__(self):
        return self.entity + " " + self.pos + " " + self.vel

    def __repr__(self):
        return str(self)
