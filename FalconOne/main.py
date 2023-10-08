import sys, pygame
from include.Items import *
from include.Player import *
from include.Enemies import *
from include.Base import *
from include.Bullets import *

# Iniciando o pygame.
pygame.init()
pygame.joystick.init()


if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

def read_rank():
    with open(STD_PATH + 'info/rank.dat', 'r') as file:
        file_text = file.read()
        if file_text == '':
            return 0
        else:
            return int(file_text)


def write_rank(text):
    with open(STD_PATH + 'info/rank.dat', 'w') as file:
        file.write(text)

# Lendo o rank a partir do arquivo rank.dat.
record              = read_rank()


# Criando a fonte padrao e criando o label do recorde
std_font            = pygame.font.SysFont("monospace", 20)
record_label        = std_font.render("Record: " + str(record), 1, (255, 255, 255))

# Criando os parametros do jogo.
starting_level      = 1

# Criando as variaveis de uso interno.
key_mappings = [2, 4, 3, 9]
#Em caso de raspberry
#key_mappings = [2, 9, 7, 1]
player_vel          = [0, 0]
gameClock           = pygame.time.Clock()
screen              = pygame.display.set_mode((WIDTH, HEIGHT))
done                = False
time                = 0
delta               = 0
spawn_speed         = 7
time_acc            = 0
time_step           = 2000
can_continue        = True
boss_bar_perc       = 100
menu_item           = -1
loop_background     = False
upgrade_timer       = 0
new_level_timer     = 0
waiting_next_level  = False
on_boss_rush        = False
boss_rush_step      = 1
on_victory          = False
game_over_music_started = False
game_paused = False
boss_cleared = False

# Criando os grupos de sprites
player_group        = pygame.sprite.Group()
rock_group          = pygame.sprite.Group()
player_bullets      = pygame.sprite.Group()
enemy_group         = pygame.sprite.OrderedUpdates()
enemy_bullets       = pygame.sprite.Group()
item_group          = pygame.sprite.Group()
playership_group    = pygame.sprite.Group()
misc_group          = pygame.sprite.Group()
boss_group          = pygame.sprite.Group()
background_enemy    = pygame.sprite.Group()

# Carregando o plano de fundo.
gameOverImg         = pygame.transform.scale(pygame.image.load(STD_PATH + 'res/UI/GameOver.jpg'), (WIDTH, HEIGHT))

# Carregando a tela continue
continueImg         = pygame.transform.scale(pygame.image.load(STD_PATH + 'res/UI/Continue.png'), (WIDTH, HEIGHT))

# Carregando tela de pause
pausedImg           = pygame.transform.scale(pygame.image.load(STD_PATH + 'res/UI/Pause.png'), (WIDTH, HEIGHT))

victoryImg          = pygame.transform.scale(pygame.image.load(STD_PATH + 'res/UI/Victory.png'), (WIDTH, HEIGHT))

# Carregando menu
menuImg             = pygame.transform.scale(pygame.image.load(STD_PATH + 'res/UI/Menu.png'), (WIDTH, HEIGHT))

# Seletor do Menu
selectorImg         = pygame.transform.scale(pygame.image.load(STD_PATH + 'res/Crystals/Peridot.png'), (WIDTH/20, HEIGHT/20))
selectorImg_rect    = selectorImg.get_rect()



# Variaveis para controle de plano de fundo.
background          = pygame.image.load(STD_PATH + 'res/Backgrounds/{0}.png'.format(starting_level))
background          = pygame.transform.scale(background, (WIDTH, 12*HEIGHT)).convert()
background_rect     = background.get_rect()
w, h                = background.get_size()

y1                  = HEIGHT - h
x, y                = 0, 0

# Inicializando as constantes.
FPS                 = 40
mainChar            = Player((WIDTH // 2, HEIGHT - 50), 1, 0.1, player_bullets)

game_state          = STD_GAME_STATE

PlayerShip          = PlayerShip((0, 0), 50)

game_state.add_player(mainChar)
game_state.add_enemy_group(enemy_group)
game_state.add_misc_group(misc_group)
game_state.level = starting_level

playership_group.add(PlayerShip)
player_group.add(mainChar)

screen.blit(mainChar.image, mainChar.get_rect())

pygame.mixer.music.load(STD_PATH + 'res/Music/menu.ogg')
pygame.mixer.music.play(-1)


def make_enemy_triangle(pos, vel):
    pos = list(pos)
    if pos[0] < 2 * ENEMY_STD_SCALE:
        pos[0] = 2 * ENEMY_STD_SCALE
    elif pos[0] > WIDTH - 2 * ENEMY_STD_SCALE:
        pos[0] = WIDTH - 2 * ENEMY_STD_SCALE

    enemy_group.add(SmartEnemy(pos, ENEMY_STD_SCALE, enemy_bullets, vel))
    enemy_group.add(BigEnemy((pos[0] + ENEMY_STD_SCALE, pos[1] + ENEMY_STD_SCALE), ENEMY_STD_SCALE, enemy_bullets, vel))
    enemy_group.add(BigEnemy((pos[0] - ENEMY_STD_SCALE, pos[1] + ENEMY_STD_SCALE), ENEMY_STD_SCALE, enemy_bullets, vel))

def make_rocket_triangle(pos, vel):
    pos = list(pos)
    if pos[0] < 2 * ENEMY_STD_SCALE:
        pos[0] = 2 * ENEMY_STD_SCALE
    elif pos[0] > WIDTH - 2 * ENEMY_STD_SCALE:
        pos[0] = WIDTH - 2 * ENEMY_STD_SCALE

    enemy_group.add(Rocket(pos, ENEMY_STD_SCALE, enemy_bullets, vel))
    enemy_group.add(Rocket((pos[0] + ENEMY_STD_SCALE, pos[1] + ENEMY_STD_SCALE), ENEMY_STD_SCALE, enemy_bullets, vel))
    enemy_group.add(Rocket((pos[0] - ENEMY_STD_SCALE, pos[1] + ENEMY_STD_SCALE), ENEMY_STD_SCALE, enemy_bullets, vel))

def make_enemy_tank(pos, vel, cannon):
    children = []
    pos = list(pos)

    if pos[0] < ENEMY_STD_SCALE:
        pos[0] += ENEMY_STD_SCALE

    if cannon == "Default":
        c1 = DefaultTankCannon(pos, ENEMY_STD_SCALE // 3, enemy_bullets, vel)
    elif cannon == "Thin":
        c1 = ThinTankCannon(pos, ENEMY_STD_SCALE // 3, enemy_bullets, vel)
    elif cannon == "Small":
        c1 = SmallTankCannon(pos, ENEMY_STD_SCALE // 3, enemy_bullets, vel)

    children.append(c1)

    enemy_group.add(Tank(pos, ENEMY_STD_SCALE, children, vel))
    misc_group.add(c1)

def make_enemy_ship(pos, vel, cannon):
    children = []
    pos = list(pos)

    if pos[0] < ENEMY_STD_SCALE:
        pos[0] += ENEMY_STD_SCALE

    if cannon == "Default":
        c1 = ShipCannon(pos, ENEMY_STD_SCALE // 3, enemy_bullets, vel)
    elif cannon == "Thin":
        c1 = ThinCannon(pos, ENEMY_STD_SCALE // 3, enemy_bullets, vel)
    elif cannon == "Small":
        c1 = SmallCannon(pos, ENEMY_STD_SCALE // 3, enemy_bullets, vel)

    children.append(c1)

    enemy_group.add(BigShip(pos, ENEMY_STD_SCALE, children, vel))
    misc_group.add(c1)

def start_boss_Alessia(pos, vel):
    alessia = SubmarineBoss(pos, ENEMY_STD_SCALE, enemy_bullets, vel)
    boss_group.add(alessia)
    enemy_group.add(SubmarineCrystal(pos, ENEMY_STD_SCALE, alessia, vel))

def start_boss_Brynhildr(pos, vel):
    bryn = BrynhildrBoss(pos, ENEMY_STD_SCALE, enemy_bullets, vel)
    boss_group.add(bryn)
    enemy_group.add(BrynhildrCrystal(pos, ENEMY_STD_SCALE, enemy_bullets, bryn, vel))

def start_boss_Georgia(pos, vel):
    georgia = ScrewBoss(pos, ENEMY_STD_SCALE, enemy_bullets, vel)

    c1 = ScrewMinorCrystal(pos, ENEMY_STD_SCALE//2, enemy_bullets, vel)
    c2 = ScrewMinorCrystal(pos, ENEMY_STD_SCALE//2, enemy_bullets, vel, 1)
    boss_group.add(georgia)
    misc_group.add(c1)
    misc_group.add(c2)
    enemy_group.add(ScrewCrystal(pos, ENEMY_STD_SCALE, georgia, [c1, c2], vel))

def read_dsg(filename):
    # Supports up to 999 enemy spawns.
    level_cms = dict()
    dsg_text = None
    with open(filename, 'r') as fl:
        dsg_text = fl.read()

    i = 0
    pivot = 2
    while(dsg_text.find(str(i+1)+":") != -1):
        if i + 1 > 9:
            pivot = 3
        elif i + 1 > 99:
            pivot = 4
        level_cms[i] = [GameCommand(x) for x in dsg_text[dsg_text.find(str(i)+ ":") + pivot:dsg_text.find(str(i + 1)+ ":")].split('\n') if x != '' and x[0] != '/' and x != '\r']
        i += 1
    return level_cms

actualLevel = read_dsg(STD_PATH + "res/LevelDesigns/{0}.dsg".format(starting_level))

def update_level():
    if not game_state.step_done:
        # Waits until there are no enemies on the screen for the boss to show.
        if game_state.boss_waiting and len(enemy_group) <= 0:
            if game_state.level != 5:
                pygame.mixer.music.load(STD_PATH + 'res/Music/normalboss.ogg')
            else:
                pygame.mixer.music.load(STD_PATH + 'res/Music/finalboss.ogg')
            pygame.mixer.music.play(-1)
            exec(game_state.boss_cmd)
            game_state.boss_waiting = False
            game_state.boss_cmd = None

        # Spawn the enemies on the map design.
        if game_state.step in actualLevel.keys():
            for command in actualLevel[game_state.step]:
                if command.entity == "Alessia":
                    game_state.boss_waiting = True
                    game_state.boss_cmd = command.render()
                elif command.entity == "Georgia":
                    game_state.boss_waiting = True
                    game_state.boss_cmd = command.render()
                else:
                    exec(command.render())

        game_state.step_done = True

def clear_screen():
    pygame.mixer.Sound(STD_PATH + 'res/Music/bomb.wav').play()
    for enemy in enemy_group:
        if game_state.actual_boss != enemy:
            enemy.kill(-1)
    for misc in misc_group:
        misc.kill(-1)
    for bullet in enemy_bullets:
        bullet.kill()

def clear_game():
    for enemy in enemy_group:
        enemy.kill()
    for misc in misc_group:
        misc.kill()
    for bullet in enemy_bullets:
        bullet.kill()

def update_and_draw(surface):
    boss_group.update()
    boss_group.draw(surface)
    background_enemy.update()
    background_enemy.draw(surface)
    player_group.update([player_vel[0] * delta, player_vel[1] * delta])
    playership_group.update(mainChar.rect)
    playership_group.draw(surface)
    player_group.draw(surface)
    rock_group.update()
    rock_group.draw(surface)
    player_bullets.update()
    player_bullets.draw(surface)
    enemy_group.update()
    enemy_group.draw(surface)
    enemy_bullets.update()
    enemy_bullets.draw(surface)
    misc_group.update()
    misc_group.draw(surface)
    item_group.update()
    item_group.draw(surface)

def continue_game():
    global game_state, can_continue, mainChar, player_group

    game_state.gameOver = False
    can_continue        = False
    mainChar        = Player((WIDTH // 2, HEIGHT - 50), 15, 0.1, player_bullets)
    game_state.add_player(mainChar)
    player_group.add(mainChar)
    game_state.points = 0

    if on_boss_rush:
        pygame.mixer.music.load(STD_PATH + 'res/Music/normalboss.ogg')
    elif game_state.level == 1:
        pygame.mixer.music.load(STD_PATH + 'res/Music/lv1.mp3')
    else:
        pygame.mixer.music.load(STD_PATH + 'res/Music/lv{0}.ogg'.format(game_state.level))
    pygame.mixer.music.play(-1)
    game_over_music_started = False

def restart_game():
    global game_state, can_continue, mainChar, player_group, actualLevel, w, h, y1, x, y, time, menu_item, game_paused

    clear_game()
    game_state.restart_game()
    can_continue        = True
    mainChar        = Player((WIDTH // 2, HEIGHT - 50), 15, 0.1, player_bullets)
    game_state.add_player(mainChar)
    player_group.add(mainChar)

    actualLevel = read_dsg(STD_PATH + "res/LevelDesigns/{0}.dsg".format(starting_level))

    load_background(game_state.level)

    game_state.started = False
    time = 0
    menu_item = -1

    game_paused = False
    pygame.mixer.music.load(STD_PATH + 'res/Music/menu.ogg')
    pygame.mixer.music.play(-1)

def load_background(level):
    global background, background_rect, w, h, x, y, y1, loop_background
    background          = pygame.image.load(STD_PATH + 'res/Backgrounds/{0}.png'.format(level))
    background          = pygame.transform.scale(background, (WIDTH, 12*HEIGHT)).convert()
    background_rect     = background.get_rect()
    w, h                = background.get_size()
    y1                  = HEIGHT - h
    x, y                = 0, 0
    if level == 3 or level == 4:
        loop_background = True
    else:
        loop_background = False

while not done:
    points              = std_font.render("Points: " + str(game_state.points), 1, (255, 255, 255))
    remaining_lifes     = std_font.render("Lifes: " + str(mainChar.lives), 1, (255, 255, 255))
    bombs               = std_font.render("Bombs: " + str(mainChar.bombs), 1, (255, 255, 255))
    # Temporizadores para a fase e cadencia de tiro.


    if game_state.boss_killed and new_level_timer > 4000:
        if not on_boss_rush:
            game_state.on_boss = False
            game_state.boss_killed = False
            clear_screen()
            game_state.next_level()
            actualLevel = read_dsg(STD_PATH + "res/LevelDesigns/{0}.dsg".format(game_state.level))
            load_background(game_state.level)
            can_continue = True
            time = 0
            new_level_timer = 0
            if game_state.level == 1:
                pygame.mixer.music.load(STD_PATH + 'res/Music/lv1.mp3')
            else:
                pygame.mixer.music.load(STD_PATH + 'res/Music/lv{0}.ogg'.format(game_state.level))
        else:
            boss_rush_step += 1
            if boss_rush_step == 2:
                start_boss_Georgia((WIDTH/2,0), (0, 1))
            elif boss_rush_step == 3:
                start_boss_Brynhildr((WIDTH/2, 0), (0, 1))
            elif boss_rush_step == 4:
                enemy_group.add(Erika((WIDTH/2,0), ENEMY_STD_SCALE, enemy_bullets, (0, 1)))
            elif boss_rush_step == 5:
                enemy_group.add(Morgenstern((WIDTH/2,0), ENEMY_STD_SCALE, enemy_bullets, (0, 1)))
            else:
                on_victory = True
            game_state.boss_killed = False
            can_continue = True
            time = 0
            new_level_timer = 0
        pygame.mixer.music.play(-1)
        boss_cleared = False
    elif game_state.boss_killed:
        game_state.on_boss = True
        new_level_timer += 30
        if not boss_cleared:
            clear_screen()
            boss_cleared = True



    if game_state.actual_boss != None:
        boss_bar_perc = game_state.actual_boss_percentage()

    if time > time_step:
        time = 0
        game_state.step += 1
        game_state.step_done = False

    if not on_boss_rush and game_state.started:
        update_level()
        actual_time         = gameClock.get_time()
        time                = time + actual_time
        time_acc            = time_acc + actual_time


    # Checa as colisoes.
    explode_rock        = pygame.sprite.groupcollide(rock_group, player_bullets, True, True)
    destroy_enemy       = pygame.sprite.groupcollide(player_bullets, enemy_group, True, False)
    destroy_player      = pygame.sprite.groupcollide(enemy_bullets, player_group, True, False)
    collide_with_player = pygame.sprite.groupcollide(player_group, enemy_group, False, False)
    item_pickup         = pygame.sprite.groupcollide(player_group, item_group, False, True)

    # Item pegado.
    if len(item_pickup) > 0:
        for item in item_pickup[mainChar]:
            item.apply(mainChar)
            break

    if len(destroy_enemy) > 0:
        for bullet in destroy_enemy:
            destroy_enemy[bullet][0].hit(1)

    # Desconta vida do player em caso de colisao.
    if len(collide_with_player) > 0:
        mainChar.hit(1)
        if mainChar.burning == 0 and mainChar.shield == 0:
            game_state.points /= 2
            for enemy in collide_with_player[mainChar]:
                enemy.hit(1)

    elif len(destroy_player) > 0:
        mainChar.hit(1)

    for event in pygame.event.get():


        if event.type == pygame.JOYAXISMOTION:
            print(event)
            if event.axis == 1 and event.value > 0.5 and not game_state.started:
                menu_item += 1
                if menu_item > 1:
                    menu_item = 0
            elif event.value < -0.5 and not game_state.started:
                menu_item -= 1
                if menu_item < 0:
                    menu_item = 1
            elif event.axis == 1 and event.value > 0.5:
                player_vel[1] = 1
            elif event.axis == 1 and event.value < -0.5:
                player_vel[1] = -1
            elif event.axis == 1:
                player_vel[1] = 0
            if event.axis == 0 and game_state.started:
                if event.value > 0.5:
                    player_vel[0] = 1
                elif event.value < -0.5:
                    player_vel[0] = -1
                else:
                    player_vel[0] = 0

        if event.type == pygame.JOYHATMOTION:
            if event.value[1] != 0 and not game_state.started:
                menu_item -= event.value[1]
                if menu_item < 0:
                    menu_item = 1
                elif menu_item > 1:
                    menu_item = 0
            elif event.value[1] != 0:
                player_vel[1] = -event.value[1]
            if event.value[0] != 0 and game_state.started:
                player_vel[0] = event.value[0]
        if event.type == pygame.JOYBUTTONDOWN:
            if not game_state.started and event.button == key_mappings[0]:
                if menu_item == 0:
                    game_state.started = True
                    on_boss_rush = False
                    menu_item = -1
                    if starting_level == 1:
                        pygame.mixer.music.load(STD_PATH + 'res/Music/lv1.mp3')
                    else:
                        pygame.mixer.music.load(STD_PATH + 'res/Music/lv{0}.ogg'.format(starting_level))
                    pygame.mixer.music.play(-1)
                elif menu_item == 1:
                    menu_item = -1
                    y1 = 0
                    background          = pygame.image.load(STD_PATH + 'res/Backgrounds/6.png')
                    background          = pygame.transform.scale(background, (WIDTH, HEIGHT)).convert()
                    background_rect     = background.get_rect()
                    game_state.started = True
                    on_boss_rush       = True
                    start_boss_Alessia((WIDTH/2, 0), (0, 1))
                    pygame.mixer.music.load(STD_PATH + 'res/Music/normalboss.ogg')
                    pygame.mixer.music.play(-1)
            elif game_state.gameOver and can_continue and event.button == key_mappings[0]:
                continue_game()
            elif game_state.gameOver and not can_continue:
                restart_game()
            elif event.button == key_mappings[0]:
                mainChar.startFiring()
            if event.button == key_mappings[1]:
                mainChar.startSlowdown()
            if event.button == key_mappings[2]:
                if mainChar.bombs > 0:
                    game_state.points = (game_state.points * 3)//4
                    mainChar.bombs -= 1
                    mainChar.bomb_anim = 4
                    clear_screen()
            if event.button == key_mappings[3]:
                game_paused = not game_paused


        if event.type == pygame.JOYBUTTONUP:
            if event.button == key_mappings[0]:
                mainChar.stopFiring()
            if event.button == key_mappings[1]:
                mainChar.stopSlowdown()


        # Checar as teclas pressionadas.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not game_state.started:
                if menu_item == 0:
                    game_state.started = True
                    on_boss_rush = False
                    menu_item = -1
                    if starting_level == 1:
                        pygame.mixer.music.load(STD_PATH + 'res/Music/lv1.mp3')
                    else:
                        pygame.mixer.music.load(STD_PATH + 'res/Music/lv{0}.ogg'.format(starting_level))
                    pygame.mixer.music.play(-1)

                elif menu_item == 1:
                    menu_item = -1
                    y1 = 0
                    background          = pygame.image.load(STD_PATH + 'res/Backgrounds/6.png')
                    background          = pygame.transform.scale(background, (WIDTH, HEIGHT)).convert()
                    background_rect     = background.get_rect()
                    game_state.started = True
                    on_boss_rush       = True
                    start_boss_Alessia((WIDTH/2, 0), (0, 1))
                    pygame.mixer.music.load(STD_PATH + 'res/Music/normalboss.ogg')
                    pygame.mixer.music.play(-1)
            elif event.key == pygame.K_RETURN and game_state.gameOver and can_continue:
                continue_game()
            elif event.key == pygame.K_RETURN and game_state.gameOver:
                restart_game()
            if event.key == pygame.K_LEFT:
                player_vel[0] += -1
            if event.key == pygame.K_RIGHT:
                player_vel[0] += 1
            if event.key == pygame.K_UP:
                if not game_state.started:
                    menu_item -= 1
                    if menu_item < 0:
                        menu_item = 1
                player_vel[1] += -1
            if event.key == pygame.K_DOWN:
                if not game_state.started:
                    menu_item += 1
                    if menu_item > 1:
                        menu_item = 0

                player_vel[1] += 1
            if event.key == pygame.K_z and not game_state.gameOver:
                mainChar.startFiring()
            if event.key == pygame.K_LSHIFT:
                mainChar.startSlowdown()
            if event.key == pygame.K_x and not game_state.gameOver:
                if mainChar.bombs > 0:
                    game_state.points = (game_state.points * 3)//4
                    mainChar.bombs -= 1
                    mainChar.bomb_anim = 4
                    clear_screen()
            if event.key == pygame.K_p and not game_state.gameOver:
                game_paused = not game_paused
            if event.key == pygame.K_ESCAPE:
                done = True
                break

        if event.type == pygame.KEYUP:
            # if joystick.get_axis(1) == 0:
            #     player_vel[0] = 0
            # if joystick.get_axis(0) == 0:
            #     player_vel[1] = 0
            if event.key == pygame.K_LEFT:
                player_vel[0] -= -1
            if event.key == pygame.K_RIGHT:
                player_vel[0] -= 1
            if event.key == pygame.K_UP:
                player_vel[1] -= -1
            if event.key == pygame.K_DOWN:
                player_vel[1] -= 1
            if event.key == pygame.K_z:
                mainChar.stopFiring()
            if event.key == pygame.K_LSHIFT:
                mainChar.stopSlowdown()
        if event.type == pygame.QUIT:
            if game_state.points > record:
                write_rank(str(game_state.points))
            sys.exit()
            done = True
        else:
            pass
    if on_victory:
        screen.blit(gameOverImg, gameOverImg.get_rect())
    elif game_state.gameOver:
        print
        if not game_over_music_started:
            pygame.mixer.music.load(STD_PATH + 'res/Music/gameover.ogg')
            pygame.mixer.music.play(-1)
            game_over_music_started = True

        if game_state.points > record:
            write_rank(str(game_state.points))
        # Em caso de game over.
        if can_continue:
            screen.blit(continueImg, continueImg.get_rect())
        else:
            screen.blit(gameOverImg, gameOverImg.get_rect())
    elif not game_state.started:
        screen.blit(menuImg, menuImg.get_rect())
    elif not game_paused:
        if y1 > 0:
            y1 = h
            screen.blit(background, background_rect)
        else:
            if(not game_state.on_boss):
                y1  += 1.5
                y   += 1.5
            if y1 >= -5 and loop_background:
                w, h                = background.get_size()
                y1                  = HEIGHT - h
                x, y                = 0, 0
            screen.blit(background, background_rect)
            screen.blit(background,(0,y))
            screen.blit(background,(0,y1))

        screen.blit(points, (15, 10))
        screen.blit(remaining_lifes, (15, HEIGHT - 30))
        screen.blit(bombs, (WIDTH - 200, HEIGHT - 30))
        screen.blit(record_label, (WIDTH - 200, 10))

        if game_state.on_boss:

            pygame.draw.rect(screen, (255,255,255), (WIDTH/6,0, 4*WIDTH/6, HEIGHT/70))
            pygame.draw.rect(screen, (255,0,0), (WIDTH/6,0,boss_bar_perc * 4 * WIDTH/6,HEIGHT/70))

        update_and_draw(screen)
    elif on_victory:
        screen.blit(victoryImg, pausedImg.get_rect())
    else:
        screen.blit(pausedImg, pausedImg.get_rect())


    if not game_state.started:
        selectorImg_rect.centerx = .25 * WIDTH
        if menu_item == 0:
            selectorImg_rect.centery = .72 * HEIGHT
            screen.blit(selectorImg, selectorImg_rect)
        elif menu_item == 1:
            selectorImg_rect.centery = .78 * HEIGHT
            screen.blit(selectorImg, selectorImg_rect)

    # Atualizar somente uma lista de retangulos melhora o processamento.
    pygame.display.flip()
    # Fixa o framerate para suavizar a animacao.
    delta = gameClock.tick(FPS) / 3.0
